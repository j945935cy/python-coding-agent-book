import asyncio
import os
import time
from pathlib import Path

import pytest

from examples.advanced.sandbox_runner import CommandRejected, StructuredCommandRunner
from examples.advanced.full_registry import (
    ToolAuthorization,
    build_full_registry,
    is_authorized,
    tool_authorization,
)


def test_full_registry_exposes_capabilities_without_authorizing_them(tmp_path: Path) -> None:
    registry = build_full_registry(tmp_path)

    assert registry.names() == {"calculator", "read", "write", "edit", "bash"}
    assert tool_authorization("calculator") is ToolAuthorization.ALLOW
    assert tool_authorization("read") is ToolAuthorization.ALLOW
    assert tool_authorization("write") is ToolAuthorization.REQUIRE_APPROVAL
    assert tool_authorization("edit") is ToolAuthorization.REQUIRE_APPROVAL
    assert tool_authorization("bash") is ToolAuthorization.DENY


def test_approval_only_unlocks_tools_that_require_it() -> None:
    assert is_authorized("calculator")
    assert not is_authorized("write")
    assert is_authorized("write", approved=True)
    assert not is_authorized("bash", approved=True)
    assert not is_authorized("unregistered", approved=True)


def test_structured_runner_executes_allowed_argv_in_workspace(tmp_path: Path) -> None:
    (tmp_path / "note.txt").write_text("hello\n", encoding="utf-8")
    runner = StructuredCommandRunner(tmp_path)

    result = asyncio.run(runner.run(["cat", "note.txt"]))

    assert result.returncode == 0
    assert result.stdout == "hello\n"
    assert result.stderr == ""


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["python3", "-c", "print('unsafe')"],
        ["cat", "/etc/passwd"],
        ["cat", "../outside.txt"],
        ["cat", "note.txt;id"],
        ["cat", "note.txt|id"],
        ["cat", "$(id)"],
        ["cat", ""],
        ["cat", "note.txt\n"],
        ["cat", "note.txt\x00"],
    ],
)
def test_structured_runner_rejects_commands_outside_tiny_policy(
    tmp_path: Path, argv: list[str]
) -> None:
    runner = StructuredCommandRunner(tmp_path)

    with pytest.raises(CommandRejected):
        asyncio.run(runner.run(argv))


def test_structured_runner_times_out_without_leaving_process_running(tmp_path: Path) -> None:
    fifo = tmp_path / "blocked.fifo"
    os.mkfifo(fifo)
    runner = StructuredCommandRunner(tmp_path, timeout_seconds=0.05)
    started = time.monotonic()

    with pytest.raises(TimeoutError, match="timed out"):
        asyncio.run(runner.run(["cat", fifo.name]))

    assert time.monotonic() - started < 1.0
