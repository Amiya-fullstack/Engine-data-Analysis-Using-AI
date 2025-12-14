class EmbeddingsStore:
    """Minimal embeddings store abstraction."""

    def __init__(self):
        self._store = []

    def add(self, vector, metadata=None):
        self._store.append((vector, metadata))

    def query(self, vector, k=5):
        return []
