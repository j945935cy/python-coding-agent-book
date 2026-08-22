"""Validated multi-file changes with rollback on commit failure.

A candidate workspace is built and validated in a sibling temporary directory.
Commit uses two renames.  Filesystems do not provide a general atomic directory
swap, so a failure is reported honestly; restoration is attempted and its
outcome is included in :class:`CommitError`.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path, PurePath
from typing import Callable, Mapping

Change = bytes | str | None
Validator = Callable[[Path], bool | None]
Replace = Callable[[Path, Path], object]


class ValidationError(RuntimeError):
    """The candidate workspace did not pass validation."""


class CommitError(RuntimeError):
    """Commit failed; the message states whether rollback succeeded."""


def _safe_target(staging: Path, relative_name: str) -> Path:
    relative = Path(relative_name)
    if (
        not relative_name
        or relative.is_absolute()
        or any(part == ".." for part in PurePath(relative_name).parts)
    ):
        raise ValueError(f"path must stay inside workspace: {relative_name!r}")
    target = staging / relative
    try:
        target.resolve(strict=False).relative_to(staging.resolve())
    except ValueError as exc:
        raise ValueError(f"path must stay inside workspace: {relative_name!r}") from exc
    return target


def _apply_changes(staging: Path, changes: Mapping[str, Change]) -> None:
    # Validate every path before changing the candidate, avoiding partial input
    # handling and catching copied symlinks that point outside the workspace.
    targets = [(name, _safe_target(staging, name), value) for name, value in changes.items()]
    for _name, target, value in targets:
        if value is None:
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink(missing_ok=True)
            continue
        if target.exists() and target.is_dir():
            raise ValueError(f"cannot replace directory with file: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(value.encode("utf-8") if isinstance(value, str) else value)


def apply_transaction(
    workspace: str | Path,
    changes: Mapping[str, Change],
    validator: Validator,
    *,
    replace: Replace = Path.replace,
) -> None:
    """Apply ``changes`` only when the complete staged workspace validates.

    ``None`` deletes a path; strings are encoded as UTF-8.  The validator may
    return ``False`` or raise.  In both cases the original workspace is left
    untouched.  ``replace`` is injectable so commit failures can be tested.
    """
    root = Path(workspace)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("workspace must be an existing, non-symlink directory")

    # Reject lexical escapes before doing the potentially expensive copy.
    for name in changes:
        relative = Path(name)
        if (
            not name
            or relative.is_absolute()
            or any(part == ".." for part in PurePath(name).parts)
        ):
            raise ValueError(f"path must stay inside workspace: {name!r}")

    transaction_dir = Path(
        tempfile.mkdtemp(prefix=f".{root.name}-transaction-", dir=root.parent)
    )
    staging = transaction_dir / "staging"
    backup = transaction_dir / "original"
    preserve_recovery_files = False
    try:
        shutil.copytree(root, staging, symlinks=True)
        _apply_changes(staging, changes)
        try:
            accepted = validator(staging)
        except BaseException as exc:
            raise ValidationError(f"candidate validation raised: {exc}") from exc
        if accepted is False:
            raise ValidationError("candidate validation failed")

        try:
            replace(root, backup)
        except BaseException as exc:
            raise CommitError(f"commit did not start; original workspace is untouched: {exc}") from exc

        try:
            replace(staging, root)
        except BaseException as commit_exc:
            try:
                replace(backup, root)
            except BaseException as restore_exc:
                preserve_recovery_files = True
                raise CommitError(
                    "commit and rollback both failed; original remains at "
                    f"{backup}: commit={commit_exc}; rollback={restore_exc}"
                ) from commit_exc
            raise CommitError(
                f"commit failed and original workspace was restored: {commit_exc}"
            ) from commit_exc

        shutil.rmtree(backup)
    finally:
        if not preserve_recovery_files:
            shutil.rmtree(transaction_dir, ignore_errors=True)


class MultiFileTransaction:
    """Small object-oriented wrapper around :func:`apply_transaction`."""

    def __init__(self, workspace: str | Path, validator: Validator):
        self.workspace = Path(workspace)
        self.validator = validator

    def apply(
        self,
        changes: Mapping[str, Change],
        *,
        replace: Replace = Path.replace,
    ) -> None:
        apply_transaction(self.workspace, changes, self.validator, replace=replace)


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        workspace = Path(directory) / "workspace"
        workspace.mkdir()
        (workspace / "config.txt").write_text("version=1\n", encoding="utf-8")

        def validates(candidate: Path) -> bool:
            return (candidate / "config.txt").read_text(encoding="utf-8") == "version=2\n"

        apply_transaction(
            workspace,
            {"config.txt": "version=2\n", "notes.txt": "validated\n"},
            validates,
        )
        names = ",".join(sorted(path.name for path in workspace.iterdir()))
        print(f"committed=true files={names}")
        print((workspace / "config.txt").read_text(encoding="utf-8").strip())


if __name__ == "__main__":
    main()
