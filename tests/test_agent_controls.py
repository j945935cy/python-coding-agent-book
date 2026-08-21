import asyncio

import pytest

from mini_agent.agent_loop import run_agent_loop
from mini_agent.config import AgentConfig
from mini_agent.context import AgentContext
from mini_agent.messages import AssistantMessage, ToolCall, UserMessage
from mini_agent.model_client import FakeModel
from mini_agent.tools.base import ToolRegistry


@pytest.mark.asyncio
async def test_parallel_tool_results_keep_model_call_order():
    class Tool:
        name = "work"
        description = "test"

        async def execute(self, tool_call_id, arguments):
            await asyncio.sleep(arguments["delay"])
            return arguments["label"]

    model = FakeModel([
        AssistantMessage(content="", tool_calls=[
            ToolCall("a", "work", {"label": "A", "delay": 0.02}),
            ToolCall("b", "work", {"label": "B", "delay": 0}),
        ]),
        AssistantMessage(content="done"),
    ])
    result = await run_agent_loop(
        model, AgentContext([UserMessage("go")]), ToolRegistry([Tool()]),
        AgentConfig(tool_execution="parallel"),
    )

    assert [message.content for message in result[-3:-1]] == ["A", "B"]


@pytest.mark.asyncio
async def test_sync_safety_hook_can_block_tool():
    class Tool:
        name = "danger"
        description = "test"
        called = False

        async def execute(self, tool_call_id, arguments):
            self.called = True
            return "should not happen"

    tool = Tool()
    model = FakeModel([
        AssistantMessage(content="", tool_calls=[ToolCall("x", "danger", {})]),
        AssistantMessage(content="blocked"),
    ])
    result = await run_agent_loop(
        model, AgentContext([UserMessage("go")]), ToolRegistry([tool]), AgentConfig(),
        before_tool_call=lambda _id, _name, _args: False,
    )

    assert tool.called is False
    assert result[-2].is_error is True


@pytest.mark.asyncio
async def test_agent_stops_at_max_turns():
    class Tool:
        name = "again"
        description = "keep the loop alive"

        async def execute(self, tool_call_id, arguments):
            return "again"

    responses = [AssistantMessage(content="", tool_calls=[ToolCall(str(i), "again", {})]) for i in range(3)]
    model = FakeModel(responses)
    with pytest.raises(RuntimeError, match="maximum turns"):
        await run_agent_loop(
            model,
            AgentContext([UserMessage("go")]),
            ToolRegistry([Tool()]),
            AgentConfig(max_turns=1),
        )
