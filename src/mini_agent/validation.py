from __future__ import annotations

from collections.abc import Iterable

from .messages import ToolCall


class ToolValidationError(ValueError):
    pass


def validate_tool_call(call: ToolCall, known_tools: set[str]) -> None:
    if call.name not in known_tools:
        raise ToolValidationError(f"Unknown tool: {call.name}")
    if not isinstance(call.arguments, dict):
        raise ToolValidationError("Tool arguments must be an object")
    if not call.id.strip():
        raise ToolValidationError("Tool call id is required")
