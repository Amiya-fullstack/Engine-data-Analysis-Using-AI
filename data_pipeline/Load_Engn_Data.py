#!/usr/bin/env python3
"""
neo4j_ingest_full.py

Usage:
    python neo4j_ingest_full.py --csv /path/to/synthetic_engine_data.csv \
        --neo4j bolt://localhost:7687 --user neo4j --password test \
        --batch 500 --make-windows --window-size 200 --stride 50

What it does:
- Creates Engine nodes (one per unit_id)
- Ingests sensor readings in batches using UNWIND
- Creates FailureEvent nodes (if failure==1)
- Optionally computes aggregated FeatureWindow nodes (sliding windows) and ingests them
"""

import argparse
import pandas as pd
import math
from typing import Optional
from neo4j import GraphDatabase, exceptions as neo4j_exceptions
from tqdm import tqdm
import json
import uuid

# ----------------------------
# Helper functions / Cypher
# ----------------------------

CREATE_ENGINE_CONSTRAINT = """
CREATE CONSTRAINT IF NOT EXISTS FOR (e:Engine) REQUIRE e.id IS UNIQUE
"""

CREATE_FEATUREWINDOW_CONSTRAINT = """
CREATE CONSTRAINT IF NOT EXISTS FOR (fw:FeatureWindow) REQUIRE fw.window_id IS UNIQUE
"""

CYpher_UNWIND_READINGS = """
UNWIND $rows AS r
MERGE (eng:Engine {id: r.unit_id})
CREATE (rd:SensorReading {
    ts: r.ts,
    seq: r.seq,
    sensor_1: r.sensor_1,
    sensor_2: r.sensor_2,
    sensor_3: r.sensor_3,
    sensor_4: r.sensor_4,
    sensor_5: r.sensor_5,
    sensor_6: r.sensor_6
})
CREATE (eng)-[:HAS_READING]->(rd)
"""

CYpher_UNWIND_FAILURES = """
UNWIND $fails AS f
MATCH (eng:Engine {id: f.unit_id})
MERGE (fe:FailureEvent {event_id: f.event_id})
ON CREATE SET fe.ts = f.ts, fe.type = COALESCE(f.type, 'component_failure'), fe.severity = f.severity
MERGE (eng)-[:HAD_FAILURE]->(fe)
"""

CYpher_UNWIND_WINDOWS = """
UNWIND $windows AS w
MATCH (eng:Engine {id: w.unit_id})
MERGE (fw:FeatureWindow {window_id: w.window_id})
ON CREATE SET fw.start_ts = w.start_ts, fw.end_ts = w.end_ts,
              fw.features_json = w.features, fw.created_at = datetime()
MERGE (eng)-[:HAS_WINDOW]->(fw)
"""

# ----------------------------
# Ingest class
# ----------------------------

class Neo4jIngestor:
    def __init__(self, uri, user, password, database=None):
        # create driver and verify connectivity early to provide clearer errors
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        try:
            # verify connectivity to surface connection issues immediately
            self.driver.verify_connectivity()
        except Exception as exc:
            # wrap and re-raise with actionable message
            raise RuntimeError(f"Unable to connect to Neo4j at {uri}: {exc}") from exc
        self.database = database

    def close(self):
        self.driver.close()

    def run(self, query, parameters=None):
        with self.driver.session(database=self.database) as sess:
            return sess.run(query, parameters or {})

    def ensure_constraints(self):
        self.run(CREATE_ENGINE_CONSTRAINT)
        self.run(CREATE_FEATUREWINDOW_CONSTRAINT)

    def ingest_readings_batch(self, rows):
        """
        rows: list of dicts with keys:
          unit_id, ts (ISO string), seq (int), sensor_1..sensor_6 (floats)
        """
        # chunk sized queries if necessary (Neo4j has max parameter sizes)
        self.run(CYpher_UNWIND_READINGS, {"rows": rows})

    def ingest_failures_batch(self, fails):
        # fails: list of dicts with keys unit_id, ts, event_id, severity, type
        if not fails:
            return
        self.run(CYpher_UNWIND_FAILURES, {"fails": fails})

    def ingest_windows_batch(self, windows):
        # windows: list of dicts unit_id, window_id, start_ts, end_ts, features (map)
        if not windows:
            return
        try:
            self.run(CYpher_UNWIND_WINDOWS, {"windows": windows})
        except Exception as exc:
            # surface a helpful error with sample window to help debugging
            sample = windows[0] if isinstance(windows, list) and windows else windows
            raise RuntimeError(f"Failed to ingest windows batch; sample window: {sample}. Cause: {exc}") from exc


# ----------------------------
# Feature windowing utilities
# ----------------------------

def make_windows_for_unit(df_unit, unit_id, window_size=200, stride=50, features_cols=None):
    """
    df_unit: pandas DataFrame for a single unit sorted by time ascending
    returns list of window dicts:
    {
       "unit_id": unit_id,
       "window_id": <uuid or deterministic id>,
       "start_ts": <ISO str>,
       "end_ts": <ISO str>,
       "features": { "sensor_1_mean":..., "sensor_1_std":..., ... }
    }
    """
    if features_cols is None:
        features_cols = [c for c in df_unit.columns if c.startswith("sensor_")]
    windows = []
    n = len(df_unit)
    for start in range(0, n - window_size + 1, stride):
        end = start + window_size
        win = df_unit.iloc[start:end]
        feats = {}
        for c in features_cols:
            arr = win[c].values.astype(float)
            feats[f"{c}_mean"] = float(arr.mean()) if arr.size else None
            feats[f"{c}_std"] = float(arr.std(ddof=0)) if arr.size else None
            feats[f"{c}_min"] = float(arr.min()) if arr.size else None
            feats[f"{c}_max"] = float(arr.max()) if arr.size else None
        # optionally include failure count or event_in_horizon summarization
        feats["failure_count"] = int(win["failure"].sum()) if "failure" in win.columns else 0
        window_id = f"{unit_id}__{start}__{end}"
        # Neo4j properties must be primitives or arrays; serialize feature map as JSON string
        windows.append({
            "unit_id": unit_id,
            "window_id": window_id,
            "start_ts": win["time"].iloc[0].isoformat(),
            "end_ts": win["time"].iloc[-1].isoformat(),
            "features": json.dumps(feats)
        })
    return windows

# ----------------------------
# Main ingestion flow
# ----------------------------

def ingest_csv(csv_path, neo4j_uri, neo4j_user, neo4j_pass,
               batch_size=500, make_windows=False, window_size=200, stride=50,
               dry_run=False):
    print("Loading CSV:", csv_path)
    df = pd.read_csv(csv_path, parse_dates=["time"])
    # ensure expected columns
    expected = set(["unit_id", "time", "failure"])
    if not expected.issubset(set(df.columns)):
        raise ValueError(f"CSV must contain at least columns: {expected}. Found: {df.columns.tolist()}")

    # sort by unit_id and time
    df = df.sort_values(["unit_id", "time"]).reset_index(drop=True)

    ingestor: Optional[Neo4jIngestor] = None
    if not dry_run:
        ingestor = Neo4jIngestor(neo4j_uri, neo4j_user, neo4j_pass)
        print("Ensuring constraints...")
        ingestor.ensure_constraints()
        # narrow type for linters (Pylance) — ingestor is guaranteed non-None in non-dry-run
        assert ingestor is not None
    else:
        print("Running in dry-run mode: no Neo4j operations will be performed.")

    # Ingest Engines (idempotent)
    units = df["unit_id"].unique().tolist()
    print(f"Found {len(units)} unique units. MERGE Engine nodes...")
    if dry_run:
        # write a preview of engine merges to a file instead of running DB commands
        import json as _json
        engines_preview = [{"id": u} for u in units]
        with open("data_pipeline/engines_preview.json", "w", encoding="utf-8") as _f:
            _json.dump(engines_preview, _f, indent=2)
        print(f"[dry-run] Wrote {len(engines_preview)} engine previews to data_pipeline/engines_preview.json")
    else:
        for u in units:
            ingestor.run("MERGE (e:Engine {id:$id}) SET e.created = coalesce(e.created, datetime())", {"id": u})

    # Ingest readings in batches
    print("Ingesting sensor readings in batches (UNWIND)...")
    total = len(df)
    batches = math.ceil(total / batch_size)
    iterator = df.reset_index().to_dict(orient="records")
    preview_rows = []
    for i in tqdm(range(batches), desc="batches"):
        start = i * batch_size
        end = min((i+1) * batch_size, total)
        chunk = iterator[start:end]
        rows = []
        for r in chunk:
            rows.append({
                "unit_id": r["unit_id"],
                "ts": r["time"].isoformat(),
                "seq": int(r["index"]),
                "sensor_1": float(r.get("sensor_1", float("nan"))),
                "sensor_2": float(r.get("sensor_2", float("nan"))),
                "sensor_3": float(r.get("sensor_3", float("nan"))),
                "sensor_4": float(r.get("sensor_4", float("nan"))),
                "sensor_5": float(r.get("sensor_5", float("nan"))),
                "sensor_6": float(r.get("sensor_6", float("nan")))
            })
        if dry_run:
            # collect a small sample for preview and skip DB writes
            if len(preview_rows) < 10:
                preview_rows.extend(rows[:10 - len(preview_rows)])
        else:
            # ingestor is non-None here because dry_run is False; help static analysis
            assert ingestor is not None
            ingestor.ingest_readings_batch(rows)

    # Ingest failures as separate nodes (optional but helpful)
    print("Creating FailureEvent nodes (if any)...")
    fails_df = df[df["failure"] == 1]
    if not fails_df.empty:
        fails = []
        for _, r in fails_df.iterrows():
            eid = str(uuid.uuid4())
            fails.append({
                "unit_id": r["unit_id"],
                "ts": r["time"].isoformat(),
                "event_id": eid,
                "severity": int(1),
                "type": "component_failure"
            })
        # We may chunk but often failures are few
        if dry_run:
            import json as _json
            with open("data_pipeline/fails_preview.json", "w", encoding="utf-8") as _f:
                _json.dump(fails, _f, indent=2, default=str)
            print(f"[dry-run] Wrote {len(fails)} failures to data_pipeline/fails_preview.json")
        else:
            assert ingestor is not None
            ingestor.ingest_failures_batch(fails)
    else:
        print("No failures found in CSV (no FailureEvent nodes created).")

    # Optionally compute and ingest feature windows
    if make_windows:
        print("Computing aggregated FeatureWindow nodes per unit...")
        windows_all = []
        for unit in units:
            df_unit = df[df["unit_id"] == unit].reset_index(drop=True)
            wins = make_windows_for_unit(df_unit, unit, window_size=window_size, stride=stride)
            windows_all.extend(wins)
            # chunk windows to avoid big parameter lists
            if len(windows_all) >= batch_size:
                # ingest or preview batch
                if dry_run:
                    import json as _json
                    with open("data_pipeline/windows_preview_partial.json", "w", encoding="utf-8") as _f:
                        _json.dump(windows_all, _f, indent=2, default=str)
                    windows_all = []
                else:
                    assert ingestor is not None
                    ingestor.ingest_windows_batch(windows_all)
                    windows_all = []
        # ingest remaining
        if windows_all:
            if dry_run:
                import json as _json
                with open("data_pipeline/windows_preview.json", "w", encoding="utf-8") as _f:
                    _json.dump(windows_all, _f, indent=2, default=str)
                print(f"[dry-run] Wrote {len(windows_all)} windows to data_pipeline/windows_preview.json")
            else:
                assert ingestor is not None
                ingestor.ingest_windows_batch(windows_all)
        print("FeatureWindow ingestion complete.")

    if dry_run:
        import json as _json
        with open("data_pipeline/ingest_preview.json", "w", encoding="utf-8") as _f:
            _json.dump(preview_rows, _f, indent=2, default=str)
        print(f"[dry-run] Wrote sample {len(preview_rows)} readings to data_pipeline/ingest_preview.json")
        print("Done (dry-run). No DB connection was used.")
    else:
        print("Done. Closing connection.")
        ingestor.close()


# ----------------------------
# CLI
# ----------------------------
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, help="./synthetic_engine_data.csv")
    p.add_argument("--neo4j", default="bolt://localhost:7687", help="Neo4j bolt URI")
    p.add_argument("--user", default="neo4j", help="Neo4j user")
    p.add_argument("--password", default="test", help="Neo4j password")
    p.add_argument("--batch", type=int, default=500, help="Batch size for readings ingestion")
    p.add_argument("--make-windows", action="store_true", help="Compute & ingest aggregated feature windows")
    p.add_argument("--window-size", type=int, default=200, help="Window size (timesteps) for FeatureWindow")
    p.add_argument("--stride", type=int, default=50, help="Stride for sliding windows")
    p.add_argument("--dry-run", action="store_true", help="Run without writing to Neo4j; write preview files instead")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    ingest_csv(args.csv, args.neo4j, args.user, args.password,
               batch_size=args.batch, make_windows=args.make_windows,
               window_size=args.window_size, stride=args.stride,
               dry_run=args.dry_run)
