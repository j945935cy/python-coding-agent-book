"""A constrained structured-command runner -- not an operating-system sandbox.

The runner validates an argv sequence and starts it without a shell.  This
reduces command-injection risk, but it does not provide process isolation,
resource isolation, or a security boundary like an OS sandbox would.
"""

from __future__ import annotations

import asyncio
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


class CommandRejected(ValueError):
    """Raised when argv is outside this example's tiny command policy."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class StructuredCommandRunner:
    """Validate structured argv and execute it without invoking a shell."""

    _FORBIDDEN_CHARACTERS = re.compile(r"[;&|<>`$()\r\n\x00]")

    def __init__(self, workspace: Path, *, timeout_seconds: float = 2.0):
        self.workspace = workspace.resolve()
        self.timeout_seconds = timeout_seconds

    def _validated_argv(self, argv: Sequence[str]) -> tuple[str, str]:
        if isinstance(argv, (str, bytes)) or any(not isinstance(item, str) for item in argv):
            raise CommandRejected("argv must be a sequence of strings")
        if any(self._FORBIDDEN_CHARACTERS.search(item) for item in argv):
            raise CommandRejected("shell operators, newlines, and NUL are forbidden")
        if len(argv) != 2 or argv[0] != "cat":
            raise CommandRejected("allowed form: cat WORKSPACE_RELATIVE_FILE")
        if not argv[1]:
            raise CommandRejected("file path must not be empty")

        supplied_path = Path(argv[1])
        if supplied_path.is_absolute():
            raise CommandRejected("absolute paths are forbidden")
        candidate = (self.workspace / supplied_path).resolve()
        try:
            candidate.relative_to(self.workspace)
        except ValueError as exc:
            raise CommandRejected("path escapes workspace") from exc
        return "cat", str(candidate)

    async def run(self, argv: Sequence[str]) -> CommandResult:
        validated_argv = self._validated_argv(argv)
        process = await asyncio.create_subprocess_exec(
            *validated_argv,
            cwd=self.workspace,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError as exc:
            process.kill()
            await process.wait()
            raise TimeoutError(
                f"command timed out after {self.timeout_seconds} seconds"
            ) from exc
        assert process.returncode is not None
        return CommandResult(
            process.returncode,
            stdout.decode(errors="replace"),
            stderr.decode(errors="replace"),
        )


async def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        workspace = Path(directory)
        (workspace / "example.txt").write_text("structured argv\n", encoding="utf-8")
        result = await StructuredCommandRunner(workspace).run(["cat", "example.txt"])
        print(result.stdout, end="")


if __name__ == "__main__":
    asyncio.run(main())
