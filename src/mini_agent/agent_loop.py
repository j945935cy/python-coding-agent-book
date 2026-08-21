from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from .config import AgentConfig
from .context import AgentContext
from .events import AgentEvent
from .messages import AssistantMessage, ToolResultMessage
from .model_client import ModelClient
from .tools.base import ToolRegistry
from .validation import ToolValidationError, validate_tool_call

Hook = Callable[[str, str, dict[str, Any]], Awaitable[bool] | bool]


async def run_agent_loop(
    model: ModelClient,
    context: AgentContext,
    tools: ToolRegistry,
    config: AgentConfig,
    *,
    before_tool_call: Hook | None = None,
    events: list[AgentEvent] | None = None,
) -> list:
    history = context.messages
    for turn in range(config.max_turns):
        assistant = await model.complete(context)
        history.append(assistant)
        if assistant.stop_reason == "length" and assistant.tool_calls:
            for call in assistant.tool_calls:
                history.append(ToolResultMessage(call.id, call.name, "Model output was truncated; tool call was not executed.", True))
            return history
        if not assistant.tool_calls:
            return history

        async def execute(call):
            try:
                validate_tool_call(call, tools.names())
                if before_tool_call:
                    allowed = before_tool_call(call.id, call.name, call.arguments)
                    if inspect.isawaitable(allowed):
                        allowed = await allowed
                    if not allowed:
                        raise PermissionError("Tool call blocked by safety hook")
                if events is not None:
                    events.append(AgentEvent("tool_start", {"id": call.id, "name": call.name}))
                result = await asyncio.wait_for(
                    tools.execute(call.id, call.name, call.arguments),
                    timeout=config.tool_timeout_seconds,
                )
                return ToolResultMessage(call.id, call.name, result)
            except (Exception,) as exc:
                return ToolResultMessage(call.id, call.name, str(exc), True)
            finally:
                if events is not None:
                    events.append(AgentEvent("tool_end", {"id": call.id, "name": call.name}))

        if config.tool_execution == "parallel":
            results = await asyncio.gather(*(execute(call) for call in assistant.tool_calls))
        else:
            results = [await execute(call) for call in assistant.tool_calls]
        history.extend(results)

    raise RuntimeError(f"Agent reached maximum turns: {config.max_turns}")
