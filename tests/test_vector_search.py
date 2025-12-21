import pytest
from pathlib import Path

from mcp.tools.vector_search import VectorSearch
from vector_db.embeddings_store.faiss_store import FAISSEmbeddingsStore, faiss

pytestmark = pytest.mark.skipif(faiss is None, reason="faiss is not installed; skipping FAISS-backed tests")


def _make_store(dim: int = 3) -> FAISSEmbeddingsStore:
    """Create a small FAISS store with 3 orthogonal unit vectors and simple metadata."""
    store = FAISSEmbeddingsStore(dim=dim)
    store.add([1, 0, 0], {"id": "v1"})
    store.add([0, 1, 0], {"id": "v2"})
    store.add([0, 0, 1], {"id": "v3"})
    return store


def test_search_in_memory():
    store = _make_store()
    vs = VectorSearch(store=store)

    results = vs.search([1, 0, 0], k=2)
    assert isinstance(results, list)
    assert len(results) == 2

    # Best match should be the first vector (v1)
    assert results[0]["metadata"]["id"] == "v1"
    assert results[1]["metadata"]["id"] in {"v2", "v3"}
    assert results[0]["score"] >= results[1]["score"]


def test_from_path_and_search(tmp_path: Path):
    store = _make_store()
    base = tmp_path / "embeddings"
    store.save(base)

    vs = VectorSearch.from_path(base)
    results = vs.search([0, 1, 0], k=1)
    assert len(results) == 1
    assert results[0]["metadata"]["id"] == "v2"


def test_search_without_store_raises():
    vs = VectorSearch()
    with pytest.raises(RuntimeError):
        vs.search([0, 0, 0])


def test_wrong_store_type_raises():
    with pytest.raises(TypeError):
        VectorSearch(store="not-a-store")
