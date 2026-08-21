import pytest

from mini_agent.messages import ToolCall
from mini_agent.validation import ToolValidationError, validate_tool_call


def test_tool_call_requires_object_arguments():
    with pytest.raises(ToolValidationError, match="arguments"):
        validate_tool_call(ToolCall("1", "read", []), {"read"})


def test_unknown_tool_is_rejected():
    with pytest.raises(ToolValidationError, match="Unknown tool"):
        validate_tool_call(ToolCall("1", "missing", {}), {"read"})
