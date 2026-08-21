from __future__ import annotations

import argparse
from pathlib import Path

from mini_agent.api_audit import ApiSpec, audit_api_references


SPECS = [
    ApiSpec("AgentConfig", "mini_agent.config"),
    ApiSpec("AgentContext", "mini_agent.context"),
    ApiSpec("AgentEvent", "mini_agent.events"),
    ApiSpec("AgentCancelled", "mini_agent.cancellation"),
    ApiSpec("CancellationToken", "mini_agent.cancellation"),
    ApiSpec("ToolCall", "mini_agent.messages"),
    ApiSpec("UserMessage", "mini_agent.messages"),
    ApiSpec("AssistantMessage", "mini_agent.messages"),
    ApiSpec("ToolResultMessage", "mini_agent.messages"),
    ApiSpec("FakeModel", "mini_agent.model_client"),
    ApiSpec("ModelClient", "mini_agent.model_client"),
    ApiSpec("run_agent_loop", "mini_agent.agent_loop"),
    ApiSpec("ToolRegistry", "mini_agent.tools"),
    ApiSpec("CalculatorTool", "mini_agent.tools"),
    ApiSpec("ReadTool", "mini_agent.tools"),
    ApiSpec("WriteTool", "mini_agent.tools"),
    ApiSpec("EditTool", "mini_agent.tools"),
    ApiSpec("BashTool", "mini_agent.tools.bash_tool"),
    ApiSpec("WorkspaceViolation", "mini_agent.safety"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit chapter API references")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    report = audit_api_references(Path(args.root).resolve(), SPECS)
    for symbol, chapters in report.references.items():
        if chapters:
            print(f"{symbol}: {len(chapters)} chapter(s)")
    print(f"missing_symbols={report.missing_symbols}")
    print(f"valid={report.is_valid}")
    return 0 if report.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
