from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_REFERENCE_RE = re.compile(r"`((?:tests|examples)/[^`]+)`")
_CHAPTER_RE = re.compile(r"^(\d{2})-")


@dataclass(frozen=True)
class ChapterAuditReport:
    chapter_count: int
    chapter_numbers: list[int]
    missing_references: list[str]
    duplicate_numbers: list[int]
    missing_numbers: list[int]

    @property
    def is_valid(self) -> bool:
        return not (
            self.missing_references
            or self.duplicate_numbers
            or self.missing_numbers
        )


def audit_chapters(root: Path, expected_count: int | None = None) -> ChapterAuditReport:
    chapter_dir = root / "manuscript" / "chapters"
    paths = sorted(chapter_dir.glob("*.md"))
    numbers: list[int] = []
    for path in paths:
        match = _CHAPTER_RE.match(path.name)
        if match:
            numbers.append(int(match.group(1)))

    duplicates = sorted({number for number in numbers if numbers.count(number) > 1})
    expected = expected_count if expected_count is not None else max(numbers, default=0)
    missing_numbers = sorted(set(range(1, expected + 1)) - set(numbers))

    missing_refs: set[str] = set()
    for path in paths:
        for reference in _REFERENCE_RE.findall(path.read_text(encoding="utf-8")):
            if not (root / reference).exists():
                missing_refs.add(reference)

    return ChapterAuditReport(
        chapter_count=len(paths),
        chapter_numbers=sorted(numbers),
        missing_references=sorted(missing_refs),
        duplicate_numbers=duplicates,
        missing_numbers=missing_numbers,
    )
