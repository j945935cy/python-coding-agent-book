from __future__ import annotations

import asyncio

from mini_agent.agent_loop import run_agent_loop
from mini_agent.cancellation import AgentCancelled, CancellationToken
from mini_agent.config import AgentConfig
from mini_agent.context import AgentContext
from mini_agent.messages import AssistantMessage, ToolCall, UserMessage
from mini_agent.model_client import FakeModel
from mini_agent.tools import CalculatorTool, ToolRegistry


async def main() -> None:
    token = CancellationToken()

    def cancel_before_tool(_id, _name, _arguments):
        token.cancel("operator stop")
        return True

    model = FakeModel([
        AssistantMessage("", [ToolCall("call-1", "calculator", {"operation": "add", "a": 1, "b": 2})])
    ])
    try:
        await run_agent_loop(
            model,
            AgentContext([UserMessage("開始後取消")]),
            ToolRegistry([CalculatorTool()]),
            AgentConfig(),
            before_tool_call=cancel_before_tool,
            cancellation=token,
        )
    except AgentCancelled as exc:
        print(f"cancelled={exc.reason}")


if __name__ == "__main__":
    asyncio.run(main())
