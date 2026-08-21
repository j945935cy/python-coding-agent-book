from pathlib import Path

from mini_agent.chapter_audit import audit_chapters


def test_audit_reports_missing_referenced_file(tmp_path: Path):
    chapters = tmp_path / "manuscript" / "chapters"
    chapters.mkdir(parents=True)
    (chapters / "01-one.md").write_text(
        "# 1. One\n\nRun `tests/missing.py` and `examples/ok.py`.\n",
        encoding="utf-8",
    )
    (tmp_path / "examples").mkdir()
    (tmp_path / "examples" / "ok.py").write_text("print('ok')\n", encoding="utf-8")

    report = audit_chapters(tmp_path)

    assert "tests/missing.py" in report.missing_references
    assert report.chapter_count == 1
    assert report.is_valid is False


def test_audit_accepts_complete_chapter_index(tmp_path: Path):
    chapters = tmp_path / "manuscript" / "chapters"
    chapters.mkdir(parents=True)
    for number in range(1, 19):
        (chapters / f"{number:02d}-chapter.md").write_text(f"# {number}. Chapter\n", encoding="utf-8")

    report = audit_chapters(tmp_path)

    assert report.chapter_count == 18
    assert report.chapter_numbers == list(range(1, 19))
    assert report.is_valid is True
