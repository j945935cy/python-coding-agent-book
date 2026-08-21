import asyncio
from pathlib import Path

import pytest

from mini_agent.tools.bash_tool import BashTool


@pytest.mark.asyncio
async def test_bash_allows_pwd_inside_workspace(tmp_path: Path):
    result = await BashTool(tmp_path, timeout_seconds=1).execute("1", {"command": "pwd"})
    assert result["returncode"] == 0
    assert str(tmp_path) in result["stdout"]


@pytest.mark.asyncio
async def test_bash_rejects_shell_composition(tmp_path: Path):
    with pytest.raises(PermissionError):
        await BashTool(tmp_path).execute("1", {"command": "pwd; rm -rf ."})


@pytest.mark.asyncio
async def test_bash_times_out(tmp_path: Path):
    with pytest.raises(TimeoutError):
        await BashTool(tmp_path, timeout_seconds=0.01).execute("1", {"command": "sleep 1"})
