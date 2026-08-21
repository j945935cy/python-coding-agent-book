from pathlib import Path

from mini_agent.example_audit import ExampleSpec, verify_examples


def test_verify_examples_checks_expected_output(tmp_path: Path):
    script = tmp_path / "ok.py"
    script.write_text("print('ready')\n", encoding="utf-8")

    report = verify_examples(tmp_path, [ExampleSpec("ok.py", "ready")])

    assert report.is_valid is True
    assert report.results[0].returncode == 0
    assert report.results[0].matched is True


def test_verify_examples_reports_nonzero_exit(tmp_path: Path):
    script = tmp_path / "bad.py"
    script.write_text("raise SystemExit(3)\n", encoding="utf-8")

    report = verify_examples(tmp_path, [ExampleSpec("bad.py", "never")])

    assert report.is_valid is False
    assert report.results[0].returncode == 3
    assert report.results[0].matched is False
