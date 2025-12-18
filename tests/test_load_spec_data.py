import json
from pathlib import Path

import pytest

from data_pipeline.Load_Spec_Data import (
    deterministic_embedding,
    split_failure_modes,
    load_spec_text,
    store_spec_embeddings,
)
from vector_db.embeddings_store.store import EmbeddingsStore


def test_split_and_load_spec_file(tmp_path):
    root = Path(__file__).resolve().parents[1]
    spec_path = root / "data_sources" / "engine_spec_data.doc"
    text = load_spec_text(spec_path)
    docs = split_failure_modes(text)
    # Expect six failure mode sections from the provided doc
    assert len(docs) == 6
    ids = [d["id"] for d in docs]
    assert ids[0].startswith("FM-")


def test_deterministic_embedding_properties():
    v = deterministic_embedding("some text", dim=64)
    assert len(v) == 64
    assert all(0.0 <= x <= 1.0 for x in v)


def test_store_spec_embeddings_memory_store(tmp_path):
    root = Path(__file__).resolve().parents[1]
    spec_path = root / "data_sources" / "engine_spec_data.doc"
    store = EmbeddingsStore()
    count = store_spec_embeddings(spec_path, store)
    assert count == 6
    # internal store should contain 6 entries
    assert len(store._store) == 6
    # metadata for first entry should include id and title
    _, meta = store._store[0]
    assert "id" in meta and "title" in meta
