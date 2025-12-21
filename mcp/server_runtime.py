from typing import Any, Callable, Dict


class MCPServerRuntime:
    """
    Simple in-process MCP server runtime.
    Manages tool registration and invocation.
    """

    def __init__(self):
        self._tools: Dict[str, Callable[..., Any]] = {}

    def tool(self, name: str):
        """
        Decorator to register a tool.
        """
        def decorator(func: Callable[..., Any]):
            self._tools[name] = func
            return func
        return decorator

    def list_tools(self):
        return list(self._tools.keys())

    def call(self, tool_name: str, **kwargs):
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' not registered")
        return self._tools[tool_name](**kwargs)

    def run(self):
        """
        Placeholder for future IPC / HTTP / socket server.
        Currently runs in-process.
        """
        print("MCP Server Runtime started")
        print("Registered tools:", self.list_tools())
