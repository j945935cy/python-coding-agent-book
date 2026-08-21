from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from .context import AgentContext
from .messages import AssistantMessage


class ModelClient(Protocol):
    async def complete(self, context: AgentContext) -> AssistantMessage:
        ...


class FakeModel:
    """Predictable model used by examples and tests; never calls a network."""

    def __init__(self, responses: Sequence[AssistantMessage]):
        self._responses = list(responses)
        self.calls: list[list[dict]] = []

    async def complete(self, context: AgentContext) -> AssistantMessage:
        self.calls.append(context.convert_to_llm())
        if not self._responses:
            raise RuntimeError("FakeModel has no remaining response")
        return self._responses.pop(0)
