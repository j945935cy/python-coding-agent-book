"""A full tool registry paired with an independent authorization policy.

Registration describes what the application *can* call.  It does not grant
permission to call it; consult ``tool_authorization`` at every dispatch point.
"""

from __future__ import annotations

import asyncio
import tempfile
from enum import Enum
from pathlib import Path

from mini_agent.tools import CalculatorTool, EditTool, ReadTool, ToolRegistry, WriteTool
from mini_agent.tools.bash_tool import BashTool


class ToolAuthorization(Enum):
    """The default authorization decision for a registered tool."""

    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"


_POLICY = {
    "calculator": ToolAuthorization.ALLOW,
    "read": ToolAuthorization.ALLOW,
    "write": ToolAuthorization.REQUIRE_APPROVAL,
    "edit": ToolAuthorization.REQUIRE_APPROVAL,
    "bash": ToolAuthorization.DENY,
}


def build_full_registry(workspace: Path) -> ToolRegistry:
    """Build a registry containing every tool, including denied capabilities."""

    return ToolRegistry(
        [
            CalculatorTool(),
            ReadTool(workspace),
            WriteTool(workspace),
            EditTool(workspace),
            BashTool(workspace),
        ]
    )


def tool_authorization(tool_name: str) -> ToolAuthorization:
    """Return the fail-closed default policy for ``tool_name``."""

    return _POLICY.get(tool_name, ToolAuthorization.DENY)


def is_authorized(tool_name: str, *, approved: bool = False) -> bool:
    """Decide whether a call may run; approval never overrides a denial."""

    decision = tool_authorization(tool_name)
    return decision is ToolAuthorization.ALLOW or (
        decision is ToolAuthorization.REQUIRE_APPROVAL and approved
    )


async def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        registry = build_full_registry(Path(directory))
        print(f"registered={','.join(sorted(registry.names()))}")
        for name in sorted(registry.names()):
            print(f"{name}={tool_authorization(name).value}")


if __name__ == "__main__":
    asyncio.run(main())
