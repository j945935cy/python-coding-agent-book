from __future__ import annotations

import asyncio

from mini_agent.agent_loop import run_agent_loop
from mini_agent.config import AgentConfig
from mini_agent.context import AgentContext
from mini_agent.messages import AssistantMessage, ToolCall, ToolResultMessage, UserMessage
from mini_agent.model_client import FakeModel
from mini_agent.tools import CalculatorTool, ToolRegistry


async def main() -> None:
    model = FakeModel([
        AssistantMessage("", [ToolCall("call-1", "calculator", {"operation": "add", "a": 2, "b": 3})]),
        AssistantMessage("安全政策已生效。"),
    ])
    history = await run_agent_loop(
        model,
        AgentContext([UserMessage("執行需要核准的工具")]),
        ToolRegistry([CalculatorTool()]),
        AgentConfig(),
        before_tool_call=lambda _id, _name, _arguments: False,
    )
    denied = any(message.is_error for message in history if isinstance(message, ToolResultMessage))
    print(f"denied={denied}")


if __name__ == "__main__":
    asyncio.run(main())
