from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PythonSyntaxError:
    path: str
    line: int
    message: str


@dataclass(frozen=True)
class CodeAuditReport:
    block_count: int
    syntax_errors: list[PythonSyntaxError]

    @property
    def is_valid(self) -> bool:
        return not self.syntax_errors


def extract_python_blocks(path: Path) -> list[tuple[int, str]]:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    blocks: list[tuple[int, str]] = []
    inside = False
    start_line = 0
    current: list[str] = []
    for number, line in enumerate(lines, start=1):
        marker = line.strip().lower()
        if not inside and marker in {"```python", "```py"}:
            inside = True
            start_line = number + 1
            current = []
        elif inside and marker == "```":
            blocks.append((start_line, "".join(current)))
            inside = False
        elif inside:
            current.append(line)
    return blocks


def audit_python_blocks(root: Path) -> CodeAuditReport:
    chapter_dir = root / "manuscript" / "chapters"
    errors: list[PythonSyntaxError] = []
    count = 0
    for path in sorted(chapter_dir.glob("*.md")):
        for start_line, source in extract_python_blocks(path):
            count += 1
            try:
                compile(source, str(path), "exec")
            except SyntaxError as exc:
                errors.append(
                    PythonSyntaxError(
                        path=str(path.relative_to(root)),
                        line=start_line + max((exc.lineno or 1) - 1, 0),
                        message=exc.msg,
                    )
                )
    return CodeAuditReport(block_count=count, syntax_errors=errors)
