from pathlib import Path

from mini_agent.code_audit import audit_python_blocks, extract_python_blocks


def test_extracts_python_fenced_blocks(tmp_path: Path):
    chapter = tmp_path / "manuscript" / "chapters"
    chapter.mkdir(parents=True)
    (chapter / "01-demo.md").write_text(
        "text\n```python\nvalue = 1\n```\n```bash\necho no\n```\n",
        encoding="utf-8",
    )

    blocks = extract_python_blocks(chapter / "01-demo.md")

    assert blocks == [(3, "value = 1\n")]


def test_audit_reports_python_syntax_error(tmp_path: Path):
    chapter = tmp_path / "manuscript" / "chapters"
    chapter.mkdir(parents=True)
    (chapter / "01-demo.md").write_text("```python\nif True\n```\n", encoding="utf-8")

    report = audit_python_blocks(tmp_path)

    assert report.block_count == 1
    assert len(report.syntax_errors) == 1
    assert report.is_valid is False


def test_audit_accepts_valid_python_blocks(tmp_path: Path):
    chapter = tmp_path / "manuscript" / "chapters"
    chapter.mkdir(parents=True)
    (chapter / "01-demo.md").write_text("```python\nvalue = 1\n```\n", encoding="utf-8")

    report = audit_python_blocks(tmp_path)

    assert report.block_count == 1
    assert report.syntax_errors == []
    assert report.is_valid is True
