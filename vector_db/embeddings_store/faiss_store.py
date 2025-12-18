"""FAISS-backed embeddings store.

Provides a minimal FAISS index wrapper with metadata persistence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

try:
    import faiss
except Exception:  # pragma: no cover - optional dependency
    faiss = None

import numpy as np


class FAISSEmbeddingsStore:
    """A simple FAISS-backed embeddings store.

    Stores vectors in a FAISS IndexFlatIP index (cosine-sim via L2 norm
    normalization) and keeps metadata in a parallel list which is saved
    alongside the index as JSON.
    """

    def __init__(self, dim: int = 128):
        if faiss is None:
            raise RuntimeError("faiss is not installed. Install 'faiss-cpu' to enable this store.")
        self.dim = dim
        self.index = faiss.IndexFlatIP(self.dim)
        self._metadatas: List[Dict[str, Any]] = []

    def add(self, vector: List[float], metadata: Dict[str, Any] | None = None) -> None:
        arr = np.asarray(vector, dtype="float32").reshape(1, -1)
        if arr.shape[1] != self.dim:
            raise ValueError(f"Vector dimension {arr.shape[1]} does not match store dim {self.dim}")
        # Normalize for cosine-style similarity with inner-product index
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        arr = arr / norms
        self.index.add(arr)
        self._metadatas.append(metadata or {})

    def query(self, vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        arr = np.asarray(vector, dtype="float32").reshape(1, -1)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        arr = arr / norms
        distances, indices = self.index.search(arr, k)
        results: List[Dict[str, Any]] = []
        for score, idx in zip(distances[0].tolist(), indices[0].tolist()):
            if idx < 0 or idx >= len(self._metadatas):
                continue
            results.append({"score": float(score), "metadata": self._metadatas[idx]})
        return results

    def save(self, base_path: Path) -> None:
        base_path = Path(base_path)
        base_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(base_path.with_suffix(".index")))
        with open(base_path.with_suffix(".meta.json"), "w", encoding="utf-8") as fh:
            json.dump(self._metadatas, fh, indent=2)

    @classmethod
    def load(cls, base_path: Path) -> "FAISSEmbeddingsStore":
        if faiss is None:
            raise RuntimeError("faiss is not installed. Install 'faiss-cpu' to enable this store.")
        base_path = Path(base_path)
        idx = faiss.read_index(str(base_path.with_suffix(".index")))
        dim = idx.d
        inst = cls(dim=dim)
        inst.index = idx
        with open(base_path.with_suffix(".meta.json"), "r", encoding="utf-8") as fh:
            inst._metadatas = json.load(fh)
        return inst
