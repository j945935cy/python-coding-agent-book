from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPUB = ROOT / "dist/python-coding-agent-book.epub"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    hashes = []
    for _ in range(2):
        subprocess.run(
            [sys.executable, str(ROOT / "publishing/build_epub.py")],
            cwd=ROOT,
            check=True,
        )
        hashes.append(sha256(EPUB))
    print(f"first={hashes[0]}")
    print(f"second={hashes[1]}")
    print(f"reproducible={hashes[0] == hashes[1]}")
    return 0 if hashes[0] == hashes[1] else 1


if __name__ == "__main__":
    raise SystemExit(main())
