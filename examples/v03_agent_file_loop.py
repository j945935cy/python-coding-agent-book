from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from mini_agent.agent_loop import run_agent_loop
from mini_agent.config import AgentConfig
from mini_agent.context import AgentContext
from mini_agent.messages import AssistantMessage, ToolCall, UserMessage
from mini_agent.model_client import FakeModel
from mini_agent.tools import EditTool, ReadTool, ToolRegistry, WriteTool


async def main() -> None:
    with tempfile.TemporaryDirectory(prefix="mini-agent-v3-") as directory:
        workspace = Path(directory)
        model = FakeModel([
            AssistantMessage(content="", tool_calls=[ToolCall("w", "write", {"path": "hello.py", "content": "print('hello')\n"})]),
            AssistantMessage(content="", tool_calls=[ToolCall("e", "edit", {"path": "hello.py", "old": "print('hello')", "new": "print('hello, agent')"})]),
            AssistantMessage(content="", tool_calls=[ToolCall("r", "read", {"path": "hello.py"})]),
            AssistantMessage(content="檔案已建立、修改並讀回。"),
        ])
        context = AgentContext([UserMessage("建立並修改 hello.py")])
        tools = ToolRegistry([WriteTool(workspace), EditTool(workspace), ReadTool(workspace)])
        result = await run_agent_loop(model, context, tools, AgentConfig())
        print(result[-1].content)
        print((workspace / "hello.py").read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    asyncio.run(main())
