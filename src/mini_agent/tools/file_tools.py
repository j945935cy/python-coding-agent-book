from __future__ import annotations

from pathlib import Path

from ..safety import ensure_workspace_path
from .base import AgentTool


class ReadTool:
    name = "read"
    description = "Read a UTF-8 text file inside the workspace."

    def __init__(self, workspace: Path):
        self.workspace = workspace

    async def execute(self, tool_call_id: str, arguments: dict) -> str:
        path = ensure_workspace_path(self.workspace, arguments["path"])
        return path.read_text(encoding="utf-8")


class WriteTool:
    name = "write"
    description = "Write a UTF-8 text file inside the workspace."

    def __init__(self, workspace: Path):
        self.workspace = workspace

    async def execute(self, tool_call_id: str, arguments: dict) -> dict:
        path = ensure_workspace_path(self.workspace, arguments["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(arguments["content"], encoding="utf-8")
        return {"path": arguments["path"], "bytes": len(arguments["content"].encode("utf-8"))}


class EditTool:
    name = "edit"
    description = "Replace one unique text occurrence inside a workspace file."

    def __init__(self, workspace: Path):
        self.workspace = workspace

    async def execute(self, tool_call_id: str, arguments: dict) -> dict:
        path = ensure_workspace_path(self.workspace, arguments["path"])
        text = path.read_text(encoding="utf-8")
        count = text.count(arguments["old"])
        if count != 1:
            raise ValueError(f"Expected exactly one match, found {count}")
        path.write_text(text.replace(arguments["old"], arguments["new"], 1), encoding="utf-8")
        return {"path": arguments["path"], "replacements": 1}
