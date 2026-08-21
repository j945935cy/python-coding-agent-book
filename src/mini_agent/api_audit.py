from __future__ import annotations

import importlib
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ApiSpec:
    symbol: str
    module: str


@dataclass(frozen=True)
class ApiAuditReport:
    missing_symbols: list[str]
    references: dict[str, list[str]]

    @property
    def is_valid(self) -> bool:
        return not self.missing_symbols


def audit_api_references(root: Path, specs: list[ApiSpec]) -> ApiAuditReport:
    chapters = sorted((root / "manuscript" / "chapters").glob("*.md"))
    references: dict[str, list[str]] = {spec.symbol: [] for spec in specs}
    missing: set[str] = set()
    for spec in specs:
        try:
            module = importlib.import_module(spec.module)
            exists = hasattr(module, spec.symbol)
        except ImportError:
            exists = False
        if not exists:
            missing.add(spec.symbol)
        for chapter in chapters:
            text = chapter.read_text(encoding="utf-8")
            if re.search(rf"`{re.escape(spec.symbol)}`", text):
                references[spec.symbol].append(str(chapter.relative_to(root)))
    return ApiAuditReport(sorted(missing), references)
