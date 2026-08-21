from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mini_agent.verification import Check, run_checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Run every repository verification gate")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    python = sys.executable
    checks = [
        Check("chapter structure", [python, "scripts/audit_chapters.py", "."]),
        Check("Python code blocks", [python, "scripts/audit_code_blocks.py", "."]),
        Check("example outputs", [python, "scripts/verify_examples.py", "."]),
        Check("API references", [python, "scripts/audit_api_references.py", "."]),
        Check("Traditional Chinese style", [python, "scripts/audit_style.py", "."]),
        Check("learning sections", [python, "scripts/audit_learning_sections.py", "."]),
        Check("pytest", [python, "-m", "pytest", "-q"]),
        Check("compileall", [python, "-m", "compileall", "-q", "src", "tests", "examples", "scripts"]),
    ]
    report = run_checks(root, checks)
    for result in report.results:
        state = "PASS" if result.passed else "FAIL"
        print(f"[{state}] {result.name}")
        if not result.passed and result.output:
            print(result.output.rstrip())
    print(f"valid={report.is_valid}")
    return 0 if report.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
