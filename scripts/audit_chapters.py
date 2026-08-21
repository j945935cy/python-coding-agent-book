from __future__ import annotations

import argparse
from pathlib import Path

from mini_agent.chapter_audit import audit_chapters


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit manuscript chapter references")
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    parser.add_argument("--expected-count", type=int, default=18)
    args = parser.parse_args()

    report = audit_chapters(Path(args.root).resolve(), expected_count=args.expected_count)
    print(f"chapters={report.chapter_count}")
    print(f"numbers={report.chapter_numbers}")
    print(f"missing_references={report.missing_references}")
    print(f"duplicate_numbers={report.duplicate_numbers}")
    print(f"missing_numbers={report.missing_numbers}")
    print(f"valid={report.is_valid}")
    return 0 if report.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
