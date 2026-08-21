from pathlib import Path

from mini_agent.api_audit import ApiSpec, audit_api_references


def test_api_audit_reports_missing_symbol(tmp_path: Path):
    chapters = tmp_path / "manuscript" / "chapters"
    chapters.mkdir(parents=True)
    (chapters / "01-demo.md").write_text("使用 `MissingTool`。\n", encoding="utf-8")

    report = audit_api_references(tmp_path, [ApiSpec("MissingTool", "mini_agent.tools")])

    assert report.missing_symbols == ["MissingTool"]
    assert report.is_valid is False


def test_api_audit_accepts_existing_symbol(tmp_path: Path):
    chapters = tmp_path / "manuscript" / "chapters"
    chapters.mkdir(parents=True)
    (chapters / "01-demo.md").write_text("使用 `ToolRegistry`。\n", encoding="utf-8")

    report = audit_api_references(tmp_path, [ApiSpec("ToolRegistry", "mini_agent.tools")])

    assert report.missing_symbols == []
    assert report.references["ToolRegistry"] == ["manuscript/chapters/01-demo.md"]
    assert report.is_valid is True
