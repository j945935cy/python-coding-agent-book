from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from mini_agent.agent_loop import run_agent_loop
from mini_agent.cancellation import CancellationToken
from mini_agent.config import AgentConfig
from mini_agent.context import AgentContext
from mini_agent.events import AgentEvent
from mini_agent.messages import AssistantMessage, ToolCall, UserMessage
from mini_agent.model_client import FakeModel
from mini_agent.tools import EditTool, ReadTool, ToolRegistry, WriteTool


async def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        workspace = Path(directory)
        model = FakeModel([
            AssistantMessage("", [ToolCall("write-1", "write", {"path": "app.py", "content": "print('draft')\n"})]),
            AssistantMessage("", [ToolCall("edit-1", "edit", {"path": "app.py", "old": "draft", "new": "ready"})]),
            AssistantMessage("", [ToolCall("read-1", "read", {"path": "app.py"})]),
            AssistantMessage("完整 Agent 已完成。"),
        ])
        events: list[AgentEvent] = []
        allowed = {"write", "edit", "read"}
        history = await run_agent_loop(
            model,
            AgentContext([UserMessage("建立、修改並驗證 app.py")]),
            ToolRegistry([WriteTool(workspace), EditTool(workspace), ReadTool(workspace)]),
            AgentConfig(max_turns=6),
            before_tool_call=lambda _id, name, _arguments: name in allowed,
            events=events,
            cancellation=CancellationToken(),
        )
        print(history[-1].content)
        print((workspace / "app.py").read_text(encoding="utf-8").strip())
        print(f"events={len(events)}")


if __name__ == "__main__":
    asyncio.run(main())
