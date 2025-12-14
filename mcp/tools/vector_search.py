class VectorSearch:
    """Simple interface to encapsulate vector DB searches."""

    def __init__(self, index=None):
        self.index = index

    def search(self, vector, k=5):
        return []
