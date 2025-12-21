from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from vector_db.embeddings_store.faiss_store import FAISSEmbeddingsStore


class VectorSearch:
    """Simple wrapper around a local FAISS-backed embeddings store.

    This class provides a small, testable interface for searching a
    FAISS-based vector DB. It prefers an in-memory store instance but
    can also load a store from disk using ``FAISSEmbeddingsStore.load``.

    Example:
        store = FAISSEmbeddingsStore.load(Path("vector_db/embeddings"))
        vs = VectorSearch(store=store)
        results = vs.search([0.1, 0.2, ...], k=5)

    Results are lists of dicts in the form: {"score": float, "metadata": dict}
    """

    def __init__(self, store: Optional[FAISSEmbeddingsStore] = None, base_path: Optional[Path] = None):
        if store is not None and not isinstance(store, FAISSEmbeddingsStore):
            raise TypeError("store must be an instance of FAISSEmbeddingsStore")
        self.store: Optional[FAISSEmbeddingsStore] = store
        if self.store is None and base_path is not None:
            self.load_from_path(base_path)

    @classmethod
    def from_path(cls, base_path: Path) -> "VectorSearch":
        """Create a VectorSearch by loading a FAISS store from disk."""
        inst = cls()
        inst.load_from_path(base_path)
        return inst

    def load_from_path(self, base_path: Path) -> None:
        """Load a FAISS index and metadata from the given base path.

        The path refers to the same base used by ``FAISSEmbeddingsStore.save`` and
        ``FAISSEmbeddingsStore.load`` (the implementation expects a .index and
        a .meta.json file alongside the provided base path).
        """
        self.store = FAISSEmbeddingsStore.load(Path(base_path))

    def search(self, vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Search the underlying FAISS store for top-k nearest neighbors.

        Args:
            vector: The query vector as a list of floats.
            k: Number of nearest neighbors to return.

        Returns:
            A list of result dicts, each with keys ``score`` and ``metadata``.
        """
        if self.store is None:
            raise RuntimeError("No vector store is loaded. Provide a store or a base_path to load from.")
        return self.store.query(vector, k=k)

