import pytest

from mini_agent.tools.calculator import CalculatorTool


@pytest.mark.asyncio
async def test_calculator_supports_basic_arithmetic_without_eval():
    result = await CalculatorTool().execute("1", {"operation": "add", "left": 2, "right": 3})
    assert result == {"result": 5}


@pytest.mark.asyncio
async def test_calculator_rejects_unknown_operation():
    with pytest.raises(ValueError, match="Unsupported operation"):
        await CalculatorTool().execute("1", {"operation": "divide", "left": 2, "right": 3})


@pytest.mark.asyncio
async def test_calculator_rejects_non_numeric_operands():
    with pytest.raises(TypeError, match="left and right must be numbers"):
        await CalculatorTool().execute("1", {"operation": "add", "left": "2", "right": 3})
