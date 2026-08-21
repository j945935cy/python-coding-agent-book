from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Protocol


class AgentTool(Protocol):
    name: str
    description: str

    async def execute(self, tool_call_id: str, arguments: dict[str, Any]) -> Any:
        ...


class ToolRegistry:
    def __init__(self, tools: Iterable[AgentTool] = ()):
        self._tools: dict[str, AgentTool] = {}
        for tool in tools:
            self.register(tool)

    def register(self, tool: AgentTool) -> None:
        if not tool.name:
            raise ValueError("Tool name is required")
        if tool.name in self._tools:
            raise ValueError(f"Duplicate tool name: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> AgentTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {name}") from exc

    def names(self) -> set[str]:
        return set(self._tools)

    async def execute(self, tool_call_id: str, name: str, arguments: dict[str, Any]) -> Any:
        return await self.get(name).execute(tool_call_id, arguments)
