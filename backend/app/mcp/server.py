"""Model Context Protocol (MCP) server definitions and tool registry.

Scaffolding for Phase 5: FastMCP exposure of codebase tools (file viewer,
symbol finder, dependency graph inspector).
"""

from typing import Any, Callable, Dict
from app.core.logging import get_logger

logger = get_logger("app.mcp")


class MCPToolRegistry:
    """Registry for codebase MCP tools exposed to external agents."""

    def __init__(self) -> None:
        self._tools: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, func: Callable[..., Any]) -> None:
        """Register a new MCP tool callable."""
        self._tools[name] = func
        logger.info(f"Registered MCP tool stub: {name}")

    def list_tools(self) -> Dict[str, str]:
        """List registered tool names and descriptions."""
        return {name: (func.__doc__ or "No description") for name, func in self._tools.items()}
