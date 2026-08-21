import os
import subprocess
import sys
from pathlib import Path


def test_v06_event_consumer_reports_successful_calculator_result():
    root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(root / "src")

    completed = subprocess.run(
        [sys.executable, str(root / "examples/v06_event_consumer.py")],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "tool_result=10 error=False" in completed.stdout
