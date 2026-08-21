from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExampleSpec:
    path: str
    expected_output: str
    timeout_seconds: float = 10.0


@dataclass(frozen=True)
class ExampleResult:
    path: str
    returncode: int
    output: str
    matched: bool
    timed_out: bool = False


@dataclass(frozen=True)
class ExampleAuditReport:
    results: list[ExampleResult]

    @property
    def is_valid(self) -> bool:
        return all(result.returncode == 0 and result.matched for result in self.results)


def verify_examples(root: Path, specs: list[ExampleSpec]) -> ExampleAuditReport:
    results: list[ExampleResult] = []
    environment = os.environ.copy()
    source_path = str(root / "src")
    environment["PYTHONPATH"] = source_path + os.pathsep + environment.get("PYTHONPATH", "")
    for spec in specs:
        try:
            completed = subprocess.run(
                [sys.executable, str(root / spec.path)],
                cwd=root,
                env=environment,
                capture_output=True,
                text=True,
                timeout=spec.timeout_seconds,
                check=False,
            )
            output = completed.stdout + completed.stderr
            results.append(
                ExampleResult(spec.path, completed.returncode, output, spec.expected_output in output)
            )
        except subprocess.TimeoutExpired as exc:
            parts = []
            for part in (exc.stdout, exc.stderr):
                if isinstance(part, bytes):
                    parts.append(part.decode("utf-8", errors="replace"))
                elif part:
                    parts.append(part)
            output = "".join(parts)
            results.append(ExampleResult(spec.path, -1, output, False, timed_out=True))
    return ExampleAuditReport(results)
