from pathlib import Path

from mini_agent.style_audit import audit_style


def test_style_audit_reports_forbidden_terms(tmp_path: Path):
    chapters = tmp_path / "manuscript" / "chapters"
    chapters.mkdir(parents=True)
    (chapters / "01-demo.md").write_text("這是一個程序，包含函数。\n", encoding="utf-8")

    report = audit_style(tmp_path)

    assert report.violations["程序"] == ["manuscript/chapters/01-demo.md:1"]
    assert report.violations["函数"] == ["manuscript/chapters/01-demo.md:1"]
    assert report.is_valid is False


def test_style_audit_accepts_taiwan_terms(tmp_path: Path):
    chapters = tmp_path / "manuscript" / "chapters"
    chapters.mkdir(parents=True)
    (chapters / "01-demo.md").write_text("這是一個程式，包含函式。\n", encoding="utf-8")

    report = audit_style(tmp_path)

    assert report.violations == {}
    assert report.is_valid is True
