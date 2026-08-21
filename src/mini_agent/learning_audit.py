from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_REQUIRED = ("練習", "本章驗收")
_HEADING_RE = re.compile(r"^## (.+?)\s*$")


@dataclass(frozen=True)
class LearningAuditReport:
    missing_sections: dict[str, list[str]]
    empty_sections: dict[str, list[str]]

    @property
    def is_valid(self) -> bool:
        return not self.missing_sections and not self.empty_sections


def _sections(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    found: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        match = _HEADING_RE.match(line)
        if match:
            heading = match.group(1)
            current = heading
            found[heading] = []
        elif current is not None:
            found[current].append(line)
    return {name: "\n".join(body).strip() for name, body in found.items()}


def audit_learning_sections(root: Path) -> LearningAuditReport:
    missing: dict[str, list[str]] = {}
    empty: dict[str, list[str]] = {}
    for path in sorted((root / "manuscript" / "chapters").glob("*.md")):
        sections = _sections(path)
        missing_names = [name for name in _REQUIRED if name not in sections]
        empty_names = [name for name in _REQUIRED if name in sections and not sections[name]]
        relative = str(path.relative_to(root))
        if missing_names:
            missing[relative] = missing_names
        if empty_names:
            empty[relative] = empty_names
    return LearningAuditReport(missing, empty)
