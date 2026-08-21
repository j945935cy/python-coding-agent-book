from pathlib import Path

from mini_agent.learning_audit import audit_learning_sections


def test_learning_audit_reports_missing_section(tmp_path: Path):
    chapters = tmp_path / "manuscript" / "chapters"
    chapters.mkdir(parents=True)
    (chapters / "01-demo.md").write_text("# 1. Demo\n\n## 練習\n\n1. 做一件事。\n", encoding="utf-8")

    report = audit_learning_sections(tmp_path)

    assert report.missing_sections == {"manuscript/chapters/01-demo.md": ["本章驗收"]}
    assert report.is_valid is False


def test_learning_audit_accepts_complete_sections(tmp_path: Path):
    chapters = tmp_path / "manuscript" / "chapters"
    chapters.mkdir(parents=True)
    (chapters / "01-demo.md").write_text(
        "# 1. Demo\n\n## 練習\n\n1. 做一件事。\n\n## 本章驗收\n\n- 測試通過。\n",
        encoding="utf-8",
    )

    report = audit_learning_sections(tmp_path)

    assert report.missing_sections == {}
    assert report.empty_sections == {}
    assert report.is_valid is True
