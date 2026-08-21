from __future__ import annotations

import asyncio
import re
from pathlib import Path


_ALLOWED_COMMANDS = {"cat", "echo", "ls", "pwd", "python3", "sleep"}
_SHELL_OPERATORS = re.compile(r"[;&|<>`]|\x00")


class BashTool:
    name = "bash"
    description = "Run a restricted command inside the workspace."

    def __init__(self, workspace: Path, timeout_seconds: float = 10.0):
        self.workspace = workspace.resolve()
        self.timeout_seconds = timeout_seconds

    async def execute(self, tool_call_id: str, arguments: dict) -> dict:
        command = arguments["command"]
        if not isinstance(command, str) or not command.strip():
            raise ValueError("command must be a non-empty string")
        if _SHELL_OPERATORS.search(command):
            raise PermissionError("Shell composition is disabled in restricted mode")
        executable = command.strip().split(maxsplit=1)[0]
        if executable not in _ALLOWED_COMMANDS:
            raise PermissionError(f"Command is not allowed: {executable}")

        process = await asyncio.create_subprocess_shell(
            command,
            cwd=self.workspace,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), self.timeout_seconds)
        except asyncio.TimeoutError as exc:
            process.kill()
            await process.wait()
            raise TimeoutError(f"Command timed out after {self.timeout_seconds}s") from exc
        return {
            "returncode": process.returncode,
            "stdout": stdout.decode(errors="replace"),
            "stderr": stderr.decode(errors="replace"),
        }
