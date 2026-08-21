from __future__ import annotations

import asyncio

from mini_agent.agent_loop import run_agent_loop
from mini_agent.cancellation import CancellationToken
from mini_agent.config import AgentConfig
from mini_agent.context import AgentContext
from mini_agent.events import AgentEvent
from mini_agent.messages import AssistantMessage, ToolCall, UserMessage
from mini_agent.model_client import FakeModel
from mini_agent.tools import CalculatorTool, ToolRegistry


async def main() -> None:
    token = CancellationToken()
    events: list[AgentEvent] = []
    model = FakeModel([
        AssistantMessage(content="", tool_calls=[ToolCall("a", "calculator", {"operation": "add", "left": 4, "right": 5})]),
        AssistantMessage(content="9"),
    ])
    result = await run_agent_loop(
        model,
        AgentContext([UserMessage("4 加 5")]),
        ToolRegistry([CalculatorTool()]),
        AgentConfig(tool_execution="parallel"),
        events=events,
        cancellation=token,
    )
    print(result[-1].content)
    print("events=" + ",".join(event.type for event in events))


if __name__ == "__main__":
    asyncio.run(main())
