def run_graph_query(driver, cypher: str, params: dict = None):
    """Run a Cypher query against a Neo4j driver. Placeholder for MCP tool."""
    with driver.session() as sess:
        return list(sess.run(cypher, params or {}))
