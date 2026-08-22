"""No-key model adapter driven entirely by recorded fixtures."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
import json
from typing import Any

from mini_agent.context import AgentContext
from mini_agent.messages import AssistantMessage, ToolCall


class AdapterResponseError(ValueError):
    """The recorded provider response does not match the expected schema."""


def _tool_call(item: dict[str, Any]) -> ToolCall:
    call_id = item.get("id")
    if not isinstance(call_id, str) or not call_id.strip():
        raise AdapterResponseError("tool call id must be a non-empty string")
    try:
        function = item["function"]
        name = function["name"]
        arguments = json.loads(function["arguments"])
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise AdapterResponseError("tool call arguments must be a JSON object") from exc
    if not isinstance(name, str) or not name or not isinstance(arguments, dict):
        raise AdapterResponseError("tool call arguments must be a JSON object")
    return ToolCall(call_id, name, arguments)


def _assistant_message(response: dict[str, Any]) -> AssistantMessage:
    try:
        choices = response["choices"]
        choice = choices[0]
        message = choice["message"]
        content = message.get("content")
        raw_calls = message.get("tool_calls", [])
        stop_reason = choice.get("finish_reason") or "stop"
        if not isinstance(message, dict) or not isinstance(raw_calls, list):
            raise TypeError
        if content is not None and not isinstance(content, str):
            raise TypeError
        if not isinstance(stop_reason, str):
            raise TypeError
    except (AttributeError, KeyError, IndexError, TypeError) as exc:
        raise AdapterResponseError("malformed provider response") from exc

    try:
        calls = [_tool_call(item) for item in raw_calls]
    except AttributeError as exc:
        raise AdapterResponseError("malformed provider response") from exc
    seen_ids: set[str] = set()
    for call in calls:
        if call.id in seen_ids:
            raise AdapterResponseError(f"duplicate tool call id: {call.id}")
        seen_ids.add(call.id)
    return AssistantMessage(content or "", calls, stop_reason)


class FakeTransport:
    """Return provider-shaped fixtures without making network calls."""

    def __init__(self, responses: Sequence[dict[str, Any] | Exception]):
        self._responses = list(responses)
        self.requests: list[dict[str, Any]] = []

    async def send(self, request: dict[str, Any]) -> dict[str, Any]:
        self.requests.append(request)
        if not self._responses:
            raise RuntimeError("FakeTransport has no remaining response")
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class RecordingAdapter:
    """Translate provider-like responses into the mini-agent message model."""

    def __init__(self, transport: FakeTransport, *, max_retries: int = 0):
        if max_retries < 0:
            raise ValueError("max_retries must not be negative")
        self.transport = transport
        self.max_retries = max_retries
        self.requests: list[dict[str, Any]] = []

    async def complete(self, context: AgentContext) -> AssistantMessage:
        request = {
            "messages": context.convert_to_llm(),
            "system": context.system_prompt,
        }
        self.requests.append(request)
        response: dict[str, Any] | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.transport.send(request)
                break
            except (TimeoutError, ConnectionError):
                if attempt == self.max_retries:
                    raise
        if response is None:  # The loop always returns or raises; narrows the type.
            raise RuntimeError("transport returned no response")
        return _assistant_message(response)


async def _demo() -> None:
    fixture = {
        "choices": [
            {
                "message": {"content": "Offline adapter response.", "tool_calls": []},
                "finish_reason": "stop",
            }
        ]
    }
    adapter = RecordingAdapter(FakeTransport([fixture]))
    result = await adapter.complete(AgentContext())
    print(f"assistant> {result.content}")
    print(f"requests={len(adapter.requests)}")


def main() -> None:
    asyncio.run(_demo())


if __name__ == "__main__":
    main()
