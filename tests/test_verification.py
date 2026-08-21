from pathlib import Path
import sys

from mini_agent.verification import Check, run_checks


def test_run_checks_reports_success_and_failure(tmp_path: Path):
    ok = tmp_path / "ok.py"
    bad = tmp_path / "bad.py"
    ok.write_text("print('ok')\n", encoding="utf-8")
    bad.write_text("raise SystemExit(2)\n", encoding="utf-8")

    report = run_checks(
        tmp_path,
        [
            Check("ok", [sys.executable, str(ok)]),
            Check("bad", [sys.executable, str(bad)]),
        ],
    )

    assert report.results[0].passed is True
    assert report.results[1].passed is False
    assert report.results[1].returncode == 2
    assert report.is_valid is False


def test_run_checks_accepts_all_successful_commands(tmp_path: Path):
    ok = tmp_path / "ok.py"
    ok.write_text("print('verified')\n", encoding="utf-8")

    report = run_checks(tmp_path, [Check("ok", [sys.executable, str(ok)])])

    assert report.is_valid is True
    assert "verified" in report.results[0].output
