from __future__ import annotations

import argparse
from pathlib import Path

from mini_agent.learning_audit import audit_learning_sections


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit chapter exercises and acceptance sections")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    report = audit_learning_sections(Path(args.root).resolve())
    print(f"missing_sections={report.missing_sections}")
    print(f"empty_sections={report.empty_sections}")
    print(f"valid={report.is_valid}")
    return 0 if report.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
