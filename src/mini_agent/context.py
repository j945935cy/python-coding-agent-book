from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .messages import Message


@dataclass
class AgentContext:
    messages: list[Message] = field(default_factory=list)
    system_prompt: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def copy(self) -> "AgentContext":
        return AgentContext(messages=list(self.messages), system_prompt=self.system_prompt, metadata=dict(self.metadata))

    def convert_to_llm(self) -> list[dict[str, Any]]:
        return [message.to_dict() for message in self.messages]
