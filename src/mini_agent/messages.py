from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["user", "assistant", "tool"]


@dataclass(slots=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "arguments": self.arguments}


@dataclass(slots=True)
class UserMessage:
    content: str
    role: Role = "user"

    def to_dict(self) -> dict[str, Any]:
        return {"role": self.role, "content": self.content}


@dataclass(slots=True)
class AssistantMessage:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str = "stop"
    role: Role = "assistant"

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "tool_calls": [call.to_dict() for call in self.tool_calls],
            "stop_reason": self.stop_reason,
        }


@dataclass(slots=True)
class ToolResultMessage:
    tool_call_id: str
    tool_name: str
    content: Any
    is_error: bool = False
    role: Role = "tool"

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "tool_call_id": self.tool_call_id,
            "tool_name": self.tool_name,
            "content": self.content,
            "is_error": self.is_error,
        }


Message = UserMessage | AssistantMessage | ToolResultMessage
