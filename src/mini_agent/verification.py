from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    name: str
    command: list[str]
    timeout_seconds: float = 120.0


@dataclass(frozen=True)
class CheckResult:
    name: str
    returncode: int
    output: str
    timed_out: bool = False

    @property
    def passed(self) -> bool:
        return self.returncode == 0 and not self.timed_out


@dataclass(frozen=True)
class VerificationReport:
    results: list[CheckResult]

    @property
    def is_valid(self) -> bool:
        return all(result.passed for result in self.results)


def run_checks(root: Path, checks: list[Check]) -> VerificationReport:
    results: list[CheckResult] = []
    for check in checks:
        try:
            completed = subprocess.run(
                check.command,
                cwd=root,
                capture_output=True,
                text=True,
                timeout=check.timeout_seconds,
                check=False,
            )
            results.append(
                CheckResult(
                    name=check.name,
                    returncode=completed.returncode,
                    output=completed.stdout + completed.stderr,
                )
            )
        except subprocess.TimeoutExpired as exc:
            output = ""
            for part in (exc.stdout, exc.stderr):
                if isinstance(part, bytes):
                    output += part.decode("utf-8", errors="replace")
                elif part:
                    output += part
            results.append(CheckResult(check.name, -1, output, timed_out=True))
    return VerificationReport(results)
