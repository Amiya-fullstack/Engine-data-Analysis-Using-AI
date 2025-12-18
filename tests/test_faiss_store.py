import json
from pathlib import Path

import pytest


def test_faiss_store_add_query_and_persistence(tmp_path):
    # Skip this test entirely if faiss is not installed
    faiss = pytest.importorskip("faiss")

    from vector_db.embeddings_store.faiss_store import FAISSEmbeddingsStore
    from data_pipeline.Load_Spec_Data import (
        deterministic_embedding,
        load_spec_text,
        split_failure_modes,
    )

    # Load docs and build deterministic embeddings for repeatability
    root = Path(__file__).resolve().parents[1]
    spec_path = root / "data_sources" / "engine_spec_data.doc"
    text = load_spec_text(spec_path)
    docs = split_failure_modes(text)

    store = FAISSEmbeddingsStore(dim=128)
    for doc in docs:
        vec = deterministic_embedding(doc["text"], dim=128)
        store.add(vec, metadata={"id": doc["id"], "title": doc["title"]})

    # Query using the first doc embedding; expect top result to be the same doc
    q = deterministic_embedding(docs[0]["text"], dim=128)
    results = store.query(q, k=3)
    assert results
    assert results[0]["metadata"]["id"] == docs[0]["id"]

    # Persist and reload
    base = tmp_path / "faiss_test_store"
    store.save(base)
    loaded = FAISSEmbeddingsStore.load(base)
    q2 = deterministic_embedding(docs[1]["text"], dim=128)
    results2 = loaded.query(q2, k=2)
    assert results2
    assert all("metadata" in r for r in results2)
