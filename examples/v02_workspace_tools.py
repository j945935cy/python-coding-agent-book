from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from mini_agent.tools import EditTool, ReadTool, ToolRegistry, WriteTool


async def main() -> None:
    with tempfile.TemporaryDirectory(prefix="mini-agent-") as directory:
        workspace = Path(directory)
        tools = ToolRegistry([WriteTool(workspace), EditTool(workspace), ReadTool(workspace)])
        await tools.execute("1", "write", {"path": "src/hello.py", "content": "print('hello')\n"})
        await tools.execute(
            "2",
            "edit",
            {"path": "src/hello.py", "old": "print('hello')", "new": "print('hello, agent')"},
        )
        content = await tools.execute("3", "read", {"path": "src/hello.py"})
        print(content, end="")


if __name__ == "__main__":
    asyncio.run(main())
