from __future__ import annotations

import argparse
from pathlib import Path

from mini_agent.style_audit import audit_style


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Traditional Chinese book style")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    report = audit_style(Path(args.root).resolve())
    for term, locations in report.violations.items():
        print(f"{term}: {', '.join(locations)}")
    print(f"violations={sum(len(items) for items in report.violations.values())}")
    print(f"valid={report.is_valid}")
    return 0 if report.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
