"""
MCP Server
----------
Exposes Vector DB search as an MCP tool.

Run:
    python -m mcp.server
"""

from pathlib import Path
from typing import Any, Dict, List

from mcp.server_runtime import MCPServerRuntime
from mcp.tools.vector_search import VectorSearch


def main() -> None:
    print("Initializing MCP Server...")

    # ------------------------------------------------------------------
    # Load FAISS Vector Store
    # ------------------------------------------------------------------
    vector_store_base = Path("vector_db/faiss_store")

    if not vector_store_base.with_suffix(".index").exists():
        raise FileNotFoundError(
            f"FAISS index not found at {vector_store_base.with_suffix('.index')}"
        )

    if not vector_store_base.with_suffix(".meta.json").exists():
        raise FileNotFoundError(
            f"FAISS metadata not found at {vector_store_base.with_suffix('.meta.json')}"
        )

    vector_search = VectorSearch.from_path(vector_store_base)
    print("FAISS vector store loaded")

    # ------------------------------------------------------------------
    # Create MCP Server Runtime
    # ------------------------------------------------------------------
    server = MCPServerRuntime()

    # ------------------------------------------------------------------
    # Register MCP Tool: vector_search
    # ------------------------------------------------------------------
    @server.tool(name="vector_search")
    def vector_search_tool(
        query_embedding: List[float],
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        MCP Tool: Vector similarity search

        Args:
            query_embedding: embedding vector for the query
            k: number of nearest neighbors

        Returns:
            List of search results with score + metadata
        """
        print("MCP TOOL CALLED → vector_search")
        print(f"   embedding_dim={len(query_embedding)}, k={k}")

        results = vector_search.search(query_embedding, k=k)

        print(f"   results_returned={len(results)}")
        return results

    # ------------------------------------------------------------------
    # Start Server
    # ------------------------------------------------------------------
    print("MCP Server started successfully")
    print("Registered tools:", server.list_tools())
    print("Waiting for MCP client calls...\n")

    server.run()


if __name__ == "__main__":
    main()
