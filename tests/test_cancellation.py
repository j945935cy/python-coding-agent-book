import pytest

from mini_agent.agent_loop import run_agent_loop
from mini_agent.config import AgentConfig
from mini_agent.context import AgentContext
from mini_agent.events import AgentEvent
from mini_agent.messages import AssistantMessage, ToolCall, UserMessage
from mini_agent.model_client import FakeModel
from mini_agent.tools.base import ToolRegistry
from mini_agent.cancellation import AgentCancelled, CancellationToken


@pytest.mark.asyncio
async def test_cancellation_stops_before_next_model_turn():
    class Tool:
        name = "cancel"
        description = "cancel the run"

        async def execute(self, tool_call_id, arguments):
            return {"ok": True}

    token = CancellationToken()
    model = FakeModel([
        AssistantMessage(content="", tool_calls=[ToolCall("1", "cancel", {})]),
        AssistantMessage(content="must not be requested"),
    ])

    async def hook(_id, _name, _args):
        token.cancel("user requested stop")
        return True

    with pytest.raises(AgentCancelled, match="user requested stop"):
        await run_agent_loop(
            model,
            AgentContext([UserMessage("stop after first decision")]),
            ToolRegistry([Tool()]),
            AgentConfig(),
            before_tool_call=hook,
            cancellation=token,
        )

    assert len(model.calls) == 1


@pytest.mark.asyncio
async def test_tool_events_always_have_matching_end_event_on_failure():
    class Tool:
        name = "fail"
        description = "fail"

        async def execute(self, tool_call_id, arguments):
            raise ValueError("broken")

    model = FakeModel([
        AssistantMessage(content="", tool_calls=[ToolCall("1", "fail", {})]),
        AssistantMessage(content="recovered"),
    ])
    events: list[AgentEvent] = []
    result = await run_agent_loop(
        model,
        AgentContext([UserMessage("run")]),
        ToolRegistry([Tool()]),
        AgentConfig(),
        events=events,
    )

    assert result[-1].content == "recovered"
    assert [event.type for event in events] == ["tool_start", "tool_end"]
