from __future__ import annotations

import operator
from typing import Any


class CalculatorTool:
    name = "calculator"
    description = "Perform one basic arithmetic operation without evaluating arbitrary Python."
    _operations = {"add": operator.add, "subtract": operator.sub, "multiply": operator.mul}

    async def execute(self, tool_call_id: str, arguments: dict[str, Any]) -> dict[str, int | float]:
        operation = arguments.get("operation")
        if operation not in self._operations:
            raise ValueError(f"Unsupported operation: {operation}")
        left = arguments.get("left")
        right = arguments.get("right")
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise TypeError("left and right must be numbers")
        return {"result": self._operations[operation](left, right)}
