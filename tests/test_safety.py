from pathlib import Path

import pytest

from mini_agent.safety import WorkspaceViolation, ensure_workspace_path


def test_workspace_rejects_parent_escape(tmp_path: Path):
    with pytest.raises(WorkspaceViolation):
        ensure_workspace_path(tmp_path, "../outside.txt")


def test_workspace_accepts_child_path(tmp_path: Path):
    assert ensure_workspace_path(tmp_path, "src/main.py") == tmp_path / "src" / "main.py"
