from __future__ import annotations

import asyncio

from mini_agent.agent_loop import run_agent_loop
from mini_agent.config import AgentConfig
from mini_agent.context import AgentContext
from mini_agent.messages import AssistantMessage, ToolCall, ToolResultMessage, UserMessage
from mini_agent.model_client import FakeModel
from mini_agent.tools import ToolRegistry


class DelayTool:
    description = "Returns a value after a delay"

    def __init__(self, name: str, delay: float):
        self.name = name
        self.delay = delay

    async def execute(self, tool_call_id, arguments):
        await asyncio.sleep(self.delay)
        return self.name


async def main() -> None:
    model = FakeModel([
        AssistantMessage("", [
            ToolCall("call-slow", "slow", {}),
            ToolCall("call-fast", "fast", {}),
        ]),
        AssistantMessage("平行工具完成。"),
    ])
    history = await run_agent_loop(
        model,
        AgentContext([UserMessage("平行執行")]),
        ToolRegistry([DelayTool("slow", 0.03), DelayTool("fast", 0.0)]),
        AgentConfig(tool_execution="parallel"),
    )
    values = [message.content for message in history if isinstance(message, ToolResultMessage)]
    print("results=" + ",".join(values))


if __name__ == "__main__":
    asyncio.run(main())
