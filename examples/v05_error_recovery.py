from __future__ import annotations

import asyncio

from mini_agent.agent_loop import run_agent_loop
from mini_agent.config import AgentConfig
from mini_agent.context import AgentContext
from mini_agent.messages import AssistantMessage, ToolCall, UserMessage
from mini_agent.model_client import FakeModel
from mini_agent.tools import ToolRegistry


class FailingTool:
    name = "unstable"
    description = "Always fails for recovery demonstration"

    async def execute(self, tool_call_id, arguments):
        raise RuntimeError("temporary tool failure")


async def main() -> None:
    model = FakeModel([
        AssistantMessage("", [ToolCall("call-1", "unstable", {})]),
        AssistantMessage("已從工具錯誤恢復。"),
    ])
    context = AgentContext([UserMessage("執行不穩定工具並恢復")])
    history = await run_agent_loop(
        model,
        context,
        ToolRegistry([FailingTool()]),
        AgentConfig(max_turns=2),
    )
    print(history[-1].content)

    looping_model = FakeModel([
        AssistantMessage("", [ToolCall("call-2", "unstable", {})]),
    ])
    try:
        await run_agent_loop(
            looping_model,
            AgentContext([UserMessage("測試最大回合數")]),
            ToolRegistry([FailingTool()]),
            AgentConfig(max_turns=1),
        )
    except RuntimeError as exc:
        print(f"max_turns_guard={'maximum turns' in str(exc)}")


if __name__ == "__main__":
    asyncio.run(main())
