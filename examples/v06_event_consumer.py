from __future__ import annotations

import asyncio

from mini_agent.agent_loop import run_agent_loop
from mini_agent.config import AgentConfig
from mini_agent.context import AgentContext
from mini_agent.events import AgentEvent
from mini_agent.messages import AssistantMessage, ToolCall, UserMessage
from mini_agent.model_client import FakeModel
from mini_agent.tools import CalculatorTool, ToolRegistry


def render(event: AgentEvent) -> str:
    return f"{event.type}:{event.data['name']}"


async def main() -> None:
    events: list[AgentEvent] = []
    model = FakeModel([
        AssistantMessage("", [ToolCall("call-1", "calculator", {"operation": "add", "a": 4, "b": 6})]),
        AssistantMessage("事件已完整收尾。"),
    ])
    await run_agent_loop(
        model,
        AgentContext([UserMessage("計算並顯示狀態")]),
        ToolRegistry([CalculatorTool()]),
        AgentConfig(),
        events=events,
    )
    print("events=" + ",".join(render(event) for event in events))


if __name__ == "__main__":
    asyncio.run(main())
