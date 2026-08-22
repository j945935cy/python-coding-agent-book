from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from examples.advanced.checkpoint_sqlite import (
    CheckpointStore,
    PayloadMismatchError,
)
from examples.advanced.multi_file_transaction import (
    CommitError,
    ValidationError,
    apply_transaction,
)


def test_checkpoint_reuses_result_after_database_reopen(tmp_path: Path) -> None:
    database = tmp_path / "checkpoints.sqlite3"
    calls = 0

    def perform() -> dict[str, int]:
        nonlocal calls
        calls += 1
        return {"answer": 42}

    with CheckpointStore(database, run_id="run-1") as store:
        assert store.execute("operation-1", {"b": 2, "a": 1}, perform) == {"answer": 42}

    with CheckpointStore(database, run_id="run-1") as reopened:
        assert reopened.execute("operation-1", {"a": 1, "b": 2}, perform) == {"answer": 42}

    assert calls == 1
    with sqlite3.connect(database) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (1,)


def test_checkpoint_rejects_reused_id_with_different_payload(tmp_path: Path) -> None:
    with CheckpointStore(tmp_path / "state.sqlite3", "run-1") as store:
        store.execute("same-id", {"value": 1}, lambda: "done")
        with pytest.raises(PayloadMismatchError):
            store.execute("same-id", {"value": 2}, lambda: "wrong")


def test_checkpoint_records_failed_status_and_allows_retry(tmp_path: Path) -> None:
    database = tmp_path / "state.sqlite3"
    with CheckpointStore(database, "run-1") as store:
        with pytest.raises(RuntimeError, match="boom"):
            store.execute("op", {}, lambda: (_ for _ in ()).throw(RuntimeError("boom")))
        assert store.get_record("op").status == "failed"
        assert store.execute("op", {}, lambda: "recovered") == "recovered"
        assert store.get_record("op").status == "completed"


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def test_transaction_commits_all_changes_only_after_validation(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "old.txt").write_bytes(b"old")
    observed: list[dict[str, bytes]] = []

    def validator(staging: Path) -> bool:
        observed.append(_snapshot(staging))
        return True

    apply_transaction(
        workspace,
        {"old.txt": b"new", "nested/added.txt": "added"},
        validator,
    )

    assert observed == [{"old.txt": b"new", "nested/added.txt": b"added"}]
    assert _snapshot(workspace) == observed[0]


def test_validation_failure_leaves_workspace_byte_identical(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "a.bin").write_bytes(b"\x00original\xff")
    before = _snapshot(workspace)

    with pytest.raises(ValidationError):
        apply_transaction(workspace, {"a.bin": b"changed"}, lambda _staging: False)

    assert _snapshot(workspace) == before


@pytest.mark.parametrize("path", ["../escape.txt", "/absolute.txt"])
def test_transaction_rejects_workspace_escape(tmp_path: Path, path: str) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    with pytest.raises(ValueError, match="workspace"):
        apply_transaction(workspace, {path: b"bad"}, lambda _staging: True)

    assert list(tmp_path.rglob("escape.txt")) == []


def test_commit_failure_restores_original_and_is_reported(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "original.txt").write_bytes(b"original")
    before = _snapshot(workspace)
    replacements = 0

    def replace(source: Path, destination: Path) -> None:
        nonlocal replacements
        replacements += 1
        if replacements == 2:
            raise OSError("injected commit failure")
        source.replace(destination)

    with pytest.raises(CommitError, match="original workspace was restored"):
        apply_transaction(
            workspace,
            {"original.txt": b"new"},
            lambda _staging: True,
            replace=replace,
        )

    assert _snapshot(workspace) == before


def test_rollback_failure_preserves_backup_and_reports_location(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "original.txt").write_bytes(b"original")
    replacements = 0

    def replace(source: Path, destination: Path) -> None:
        nonlocal replacements
        replacements += 1
        if replacements >= 2:
            raise OSError(f"injected failure {replacements}")
        source.replace(destination)

    with pytest.raises(CommitError, match="commit and rollback both failed") as raised:
        apply_transaction(
            workspace,
            {"original.txt": b"new"},
            lambda _staging: True,
            replace=replace,
        )

    message = str(raised.value)
    backup = Path(message.split("original remains at ", 1)[1].split(": commit=", 1)[0])
    assert (backup / "original.txt").read_bytes() == b"original"
