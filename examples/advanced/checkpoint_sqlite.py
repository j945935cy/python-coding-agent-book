"""Durable, payload-aware SQLite checkpoints.

This example provides idempotent replay for *completed checkpoint records*.  It
intentionally does not promise exactly-once execution: a process can crash after
an external side effect succeeds but before the completed result is committed.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

SCHEMA_VERSION = 1


class PayloadMismatchError(ValueError):
    """An operation id was reused with a different payload."""


@dataclass(frozen=True)
class CheckpointRecord:
    run_id: str
    operation_id: str
    payload_hash: str
    status: str
    result: Any


class CheckpointStore:
    """Store operation outcomes for one logical run in SQLite."""

    def __init__(self, database: str | Path, run_id: str):
        if not run_id:
            raise ValueError("run_id must not be empty")
        self.database = Path(database)
        self.run_id = run_id
        self._connection = sqlite3.connect(self.database)
        self._connection.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        with self._connection:
            version = self._connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, SCHEMA_VERSION):
                raise RuntimeError(f"unsupported checkpoint schema version: {version}")
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS checkpoints (
                    run_id TEXT NOT NULL,
                    operation_id TEXT NOT NULL,
                    payload_hash TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed')),
                    result TEXT,
                    PRIMARY KEY (run_id, operation_id)
                )
                """
            )
            self._connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    @staticmethod
    def payload_hash(payload: Any) -> str:
        encoded = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def execute(
        self,
        operation_id: str,
        payload: Any,
        operation: Callable[[], Any],
    ) -> Any:
        """Return a completed result or execute and checkpoint ``operation``.

        Pending/failed records are retried.  Such retries are at-least-once and
        callers must make external side effects independently idempotent.
        """
        if not operation_id:
            raise ValueError("operation_id must not be empty")
        digest = self.payload_hash(payload)
        row = self._connection.execute(
            "SELECT payload_hash, status, result FROM checkpoints "
            "WHERE run_id = ? AND operation_id = ?",
            (self.run_id, operation_id),
        ).fetchone()
        if row is not None and row["payload_hash"] != digest:
            raise PayloadMismatchError(
                f"operation {operation_id!r} was already used with a different payload"
            )
        if row is not None and row["status"] == "completed":
            return json.loads(row["result"])

        with self._connection:
            self._connection.execute(
                """
                INSERT INTO checkpoints(run_id, operation_id, payload_hash, status, result)
                VALUES (?, ?, ?, 'pending', NULL)
                ON CONFLICT(run_id, operation_id) DO UPDATE
                SET status = 'pending', result = NULL
                """,
                (self.run_id, operation_id, digest),
            )
        try:
            result = operation()
            serialized = json.dumps(
                result, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            )
        except BaseException as exc:
            with self._connection:
                self._connection.execute(
                    "UPDATE checkpoints SET status = 'failed', result = ? "
                    "WHERE run_id = ? AND operation_id = ?",
                    (json.dumps({"error": repr(exc)}), self.run_id, operation_id),
                )
            raise
        with self._connection:
            self._connection.execute(
                "UPDATE checkpoints SET status = 'completed', result = ? "
                "WHERE run_id = ? AND operation_id = ?",
                (serialized, self.run_id, operation_id),
            )
        return result

    def get_record(self, operation_id: str) -> CheckpointRecord | None:
        """Return the persisted record for this run, if one exists."""
        row = self._connection.execute(
            "SELECT payload_hash, status, result FROM checkpoints "
            "WHERE run_id = ? AND operation_id = ?",
            (self.run_id, operation_id),
        ).fetchone()
        if row is None:
            return None
        result = json.loads(row["result"]) if row["result"] is not None else None
        return CheckpointRecord(
            self.run_id, operation_id, row["payload_hash"], row["status"], result
        )

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> CheckpointStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def main() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / "demo.sqlite3"
        calls = 0

        def work() -> dict[str, str]:
            nonlocal calls
            calls += 1
            return {"message": "checkpointed"}

        with CheckpointStore(database, "demo-run") as store:
            first = store.execute("write-1", {"path": "hello.txt"}, work)
        with CheckpointStore(database, "demo-run") as store:
            second = store.execute("write-1", {"path": "hello.txt"}, work)
        print(f"result={first['message']} replay_equal={first == second} calls={calls}")
        print("guarantee=completed-record replay; not exactly-once across crash windows")


if __name__ == "__main__":
    main()
