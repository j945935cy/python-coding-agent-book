from __future__ import annotations

import argparse
from pathlib import Path

from mini_agent.example_audit import ExampleSpec, verify_examples


SPECS = [
    ExampleSpec("examples/v00_chatbot_baseline.py", "這只是一次模型回應。"),
    ExampleSpec("examples/v01_fake_model_loop.py", "計算結果是 5。"),
    ExampleSpec("examples/v02_workspace_tools.py", "print('hello, agent')"),
    ExampleSpec("examples/v03_agent_file_loop.py", "檔案已建立、修改並讀回。"),
    ExampleSpec("examples/v04_events_parallel_cancel.py", "events=tool_start,tool_end"),
    ExampleSpec("examples/v05_error_recovery.py", "max_turns_guard=True"),
    ExampleSpec("examples/v06_event_consumer.py", "events=tool_start:calculator,tool_end:calculator"),
    ExampleSpec("examples/v07_parallel_order.py", "results=slow,fast"),
    ExampleSpec("examples/v08_cooperative_cancel.py", "cancelled=operator stop"),
    ExampleSpec("examples/v09_safety_policy.py", "denied=True"),
    ExampleSpec("examples/v10_complete_agent.py", "完整 Agent 已完成。"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run and verify complete book examples")
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    args = parser.parse_args()
    report = verify_examples(Path(args.root).resolve(), SPECS)
    for result in report.results:
        state = "ok" if result.returncode == 0 and result.matched else "failed"
        if result.timed_out:
            state = "timeout"
        print(f"{state}: {result.path} returncode={result.returncode}")
    print(f"valid={report.is_valid}")
    return 0 if report.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
