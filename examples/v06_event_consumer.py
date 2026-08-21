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
        AssistantMessage("", [ToolCall("call-1", "calculator", {"operation": "add", "left": 4, "right": 6})]),
        AssistantMessage("事件已完整收尾。"),
    ])
    history = await run_agent_loop(
        model,
        AgentContext([UserMessage("計算並顯示狀態")]),
        ToolRegistry([CalculatorTool()]),
        AgentConfig(),
        events=events,
    )
    tool_result = history[-2]
    print(f"tool_result={tool_result.content['result']} error={tool_result.is_error}")
    print("events=" + ",".join(render(event) for event in events))


if __name__ == "__main__":
    asyncio.run(main())
