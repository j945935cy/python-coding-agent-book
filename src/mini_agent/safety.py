from __future__ import annotations

from pathlib import Path


class WorkspaceViolation(ValueError):
    pass


def ensure_workspace_path(workspace: Path, relative_path: str) -> Path:
    root = workspace.resolve()
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise WorkspaceViolation(f"Path escapes workspace: {relative_path}") from exc
    return candidate
