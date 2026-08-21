from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

FORBIDDEN_TERMS = (
    "程序",
    "函数",
    "配置",
    "用户",
    "信息",
    "目录",
    "文件",
    "对象",
    "异步",
    "线程",
)
_EMOJI_RE = re.compile("[\\U0001F300-\\U0001FAFF]")


@dataclass(frozen=True)
class StyleAuditReport:
    violations: dict[str, list[str]]

    @property
    def is_valid(self) -> bool:
        return not self.violations


def audit_style(root: Path) -> StyleAuditReport:
    violations: dict[str, list[str]] = {}
    for path in sorted((root / "manuscript" / "chapters").glob("*.md")):
        relative = str(path.relative_to(root))
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for term in FORBIDDEN_TERMS:
                if term in line:
                    violations.setdefault(term, []).append(f"{relative}:{line_number}")
            if _EMOJI_RE.search(line):
                violations.setdefault("emoji", []).append(f"{relative}:{line_number}")
    return StyleAuditReport(violations)
