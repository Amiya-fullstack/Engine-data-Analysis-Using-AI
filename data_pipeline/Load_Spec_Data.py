"""Load engine specification data and store embeddings into the vector DB.

This script reads `data_sources/engine_spec_data.doc`, splits it into
failure-mode documents, builds embeddings for each document (using the
project embedding pipeline or a deterministic hash-based fallback), and
stores them in the project's `EmbeddingsStore` abstraction.

Usage:
    python Load_Spec_Data.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

from data_pipeline.embedding_pipeline import build_embeddings
from vector_db.embeddings_store.store import EmbeddingsStore

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def load_spec_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Spec file not found: {path}")
    return path.read_text(encoding="utf-8")


def split_failure_modes(spec_text: str) -> List[Dict[str, str]]:
    """Split the specification text into sections per failure mode.

    Returns a list of dicts with keys: id, title, text.
    """
    # Find headings like 'FM-01: Progressive Turbine Imbalance'
    pattern = re.compile(r"^\s*(FM-\d{2}):\s*([^\n]+)", re.MULTILINE)
    matches = list(pattern.finditer(spec_text))
    docs: List[Dict[str, str]] = []
    if not matches:
        # Treat whole document as single doc
        docs.append({"id": "FM-00", "title": "engine_spec", "text": spec_text.strip()})
        return docs

    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(spec_text)
        block = spec_text[start:end].strip()
        fm_id = m.group(1).strip()
        title = m.group(2).strip()
        docs.append({"id": fm_id, "title": title, "text": block})
    return docs


def deterministic_embedding(text: str, dim: int = 128) -> List[float]:
    """Simple deterministic embedding using repeated sha256 digests.

    Produces a fixed-length vector of floats in [0, 1]. This is a
    fallback when a real embedding model is unavailable.
    """
    vec: List[float] = []
    i = 0
    while len(vec) < dim:
        m = hashlib.sha256()
        m.update(text.encode("utf-8"))
        m.update(i.to_bytes(2, "little", signed=False))
        digest = m.digest()
        vec.extend([b / 255.0 for b in digest])
        i += 1
    return vec[:dim]


def get_embeddings_for_docs(docs: Iterable[Dict[str, str]]) -> List[List[float]]:
    texts = [d["text"] for d in docs]
    LOG.info("Building embeddings for %d documents", len(texts))
    embeddings = build_embeddings(texts)
    # If the placeholder pipeline returned nothing or length mismatch,
    # fall back to deterministic embeddings.
    if not embeddings or len(embeddings) != len(texts):
        LOG.warning("Embedding pipeline produced no valid embeddings; using deterministic fallback")
        embeddings = [deterministic_embedding(t) for t in texts]
    return embeddings


def store_spec_embeddings(spec_path: Path, store: Any) -> int:
    text = load_spec_text(spec_path)
    docs = split_failure_modes(text)
    embeddings = get_embeddings_for_docs(docs)
    for doc, emb in zip(docs, embeddings):
        metadata = {"id": doc["id"], "title": doc["title"], "source": str(spec_path)}
        store.add(emb, metadata=metadata)
    LOG.info("Stored %d documents into vector store", len(docs))
    return len(docs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load spec docs and store embeddings into a vector DB")
    parser.add_argument("--store", choices=("memory", "faiss"), default="memory", help="Which store to use")
    parser.add_argument("--index-path", default="vector_db/faiss_store", help="Base path for FAISS index/meta files when using --store faiss")
    parser.add_argument("--dim", type=int, default=128, help="Embedding dimension (used by FAISS store)")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    spec_path = root / "data_sources" / "engine_spec_data.doc"

    if args.store == "faiss":
        try:
            from vector_db.embeddings_store.faiss_store import FAISSEmbeddingsStore
        except Exception as exc:  # pragma: no cover - provide friendly error if faiss missing
            LOG.exception("Failed to import FAISS store: %s", exc)
            print("FAISS is not available. Install 'faiss-cpu' or choose '--store memory'.")
            return
        try:
            store = FAISSEmbeddingsStore(dim=args.dim)
        except Exception as exc:  # pragma: no cover - friendly message
            LOG.exception("Failed to initialize FAISS store: %s", exc)
            print("FAISS cannot be used: check that 'faiss-cpu' is installed and available.")
            return
    else:
        store = EmbeddingsStore()

    try:
        count = store_spec_embeddings(spec_path, store)
        if args.store == "faiss":
            # persist index and metadata if the store exposes 'save'
            save_fn = getattr(store, "save", None)
            if callable(save_fn):
                try:
                    save_fn(Path(args.index_path))
                except Exception:
                    LOG.exception("Failed to save FAISS index")
        print(f"✅ Stored {count} spec documents into vector DB ({args.store})")
    except Exception as exc:  # pragma: no cover - simple CLI error reporting
        LOG.exception("Failed to load and store spec data: %s", exc)


if __name__ == "__main__":
    main()

