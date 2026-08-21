import pytest

from mini_agent.agent_loop import run_agent_loop
from mini_agent.config import AgentConfig
from mini_agent.context import AgentContext
from mini_agent.messages import AssistantMessage, ToolCall, ToolResultMessage, UserMessage
from mini_agent.model_client import FakeModel
from mini_agent.tools.base import ToolRegistry


class AddTool:
    name = "add"
    description = "Add two integers."

    async def execute(self, tool_call_id: str, arguments: dict) -> dict:
        return {"sum": arguments["a"] + arguments["b"]}


@pytest.mark.asyncio
async def test_agent_executes_tool_and_continues_until_final_answer():
    model = FakeModel(
        [
            AssistantMessage(
                content="",
                tool_calls=[ToolCall(id="call-1", name="add", arguments={"a": 2, "b": 3})],
            ),
            AssistantMessage(content="答案是 5。"),
        ]
    )
    context = AgentContext(messages=[UserMessage(content="2 加 3 是多少？")])
    registry = ToolRegistry([AddTool()])

    result = await run_agent_loop(model, context, registry, AgentConfig())

    assert result[-1].content == "答案是 5。"
    assert isinstance(result[-2], ToolResultMessage)
    assert result[-2].content == {"sum": 5}
    assert len(model.calls) == 2


@pytest.mark.asyncio
async def test_truncated_model_response_never_executes_tools():
    class ExplodingTool:
        name = "explode"
        description = "Must never run."
        called = False

        async def execute(self, tool_call_id: str, arguments: dict) -> dict:
            self.called = True
            raise AssertionError("truncated tool call was executed")

    tool = ExplodingTool()
    model = FakeModel(
        [AssistantMessage(content="", tool_calls=[ToolCall("x", "explode", {})], stop_reason="length")]
    )
    context = AgentContext(messages=[UserMessage(content="run it")])

    result = await run_agent_loop(model, context, ToolRegistry([tool]), AgentConfig())

    assert tool.called is False
    assert result[-1].is_error is True
