class MCPClientRuntime:
    """Lightweight runtime for MCP (Model Context Protocol) client-side calls."""

    def __init__(self):
        self.tools = {}

    def register_tool(self, name: str, func):
        self.tools[name] = func

    def call(self, name: str, *args, **kwargs):
        tool = self.tools.get(name)
        if not tool:
            raise KeyError(f"Tool {name} not registered")
        return tool(*args, **kwargs)
