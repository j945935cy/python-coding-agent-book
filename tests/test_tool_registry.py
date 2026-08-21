import pytest

from mini_agent.tools.base import ToolRegistry
from mini_agent.tools.calculator import CalculatorTool


def test_registry_rejects_empty_tool_name():
    class NamelessTool:
        name = ""
        description = "invalid"

        async def execute(self, tool_call_id, arguments):
            return None

    with pytest.raises(ValueError, match="Tool name is required"):
        ToolRegistry([NamelessTool()])


def test_registry_rejects_duplicate_tool_name():
    registry = ToolRegistry([CalculatorTool()])

    with pytest.raises(ValueError, match="Duplicate tool name: calculator"):
        registry.register(CalculatorTool())


@pytest.mark.asyncio
async def test_registry_rejects_unknown_tool_before_dispatch():
    registry = ToolRegistry([CalculatorTool()])

    with pytest.raises(KeyError, match="Unknown tool: missing"):
        await registry.execute("call-1", "missing", {})