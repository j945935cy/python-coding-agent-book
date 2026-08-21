from __future__ import annotations

import argparse
from pathlib import Path

from mini_agent.code_audit import audit_python_blocks


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile Python code blocks in chapters")
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    args = parser.parse_args()
    report = audit_python_blocks(Path(args.root).resolve())
    print(f"python_blocks={report.block_count}")
    print(f"syntax_errors={len(report.syntax_errors)}")
    for error in report.syntax_errors:
        print(f"{error.path}:{error.line}: {error.message}")
    print(f"valid={report.is_valid}")
    return 0 if report.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
