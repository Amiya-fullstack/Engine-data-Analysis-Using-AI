from pathlib import Path
from typing import Any, Dict, List

from mcp.tools.vector_search import VectorSearch


class DataRetrieverAgent:
    """
    AI agent responsible for semantic retrieval from a Vector DB.
    """

    def __init__(self, vector_store_path: Path, embedding_fn):
        """
        Args:
            vector_store_path: Path to FAISS vector store
            embedding_fn: Callable that converts text -> embedding vector
        """
        self.embedding_fn = embedding_fn
        self.vector_search = VectorSearch.from_path(vector_store_path)

    def retrieve(self, user_query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Convert user query to embedding and retrieve top-k results.
        """
        query_embedding = self.embedding_fn(user_query)
        return self.vector_search.search(query_embedding, k=k)
if __name__ == "__main__":
    from typing import List

    def dummy_embedding_function(text: str) -> List[float]:
        # Replace with Llama / sentence-transformer later
        return [0.1] * 128

    agent = DataRetrieverAgent(
        vector_store_path=Path("vector_db/faiss_store"),
        embedding_fn=dummy_embedding_function,
    )

    query = "Find information about engine failure modes"
    results = agent.retrieve(query, k=5)

    print("\nRetrieved Results:")
    for r in results:
        print(r)
