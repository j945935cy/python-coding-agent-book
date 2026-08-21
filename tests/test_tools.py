from pathlib import Path

import pytest

from mini_agent.tools.base import ToolRegistry
from mini_agent.tools.file_tools import EditTool, ReadTool, WriteTool


@pytest.mark.asyncio
async def test_file_tools_stay_inside_workspace(tmp_path: Path):
    registry = ToolRegistry([ReadTool(tmp_path), WriteTool(tmp_path), EditTool(tmp_path)])

    await registry.execute("w", "write", {"path": "note.txt", "content": "old"})
    result = await registry.execute("e", "edit", {"path": "note.txt", "old": "old", "new": "new"})

    assert result == {"path": "note.txt", "replacements": 1}
    assert (tmp_path / "note.txt").read_text() == "new"
