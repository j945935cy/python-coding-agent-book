import asyncio

import pytest

from mini_agent.context import AgentContext
from mini_agent.messages import AssistantMessage, ToolCall, UserMessage
from mini_agent.model_client import FakeModel
from mini_agent.tools.base import ToolRegistry


def openai_response(*, content=None, tool_calls=None, finish_reason="stop"):
    return {
        "choices": [
            {
                "message": {"content": content, "tool_calls": tool_calls or []},
                "finish_reason": finish_reason,
            }
        ]
    }


def test_adapter_converts_text_fixture_and_records_request():
    from examples.advanced.recording_adapter import FakeTransport, RecordingAdapter

    transport = FakeTransport([openai_response(content="hello")])
    adapter = RecordingAdapter(transport)
    context = AgentContext([UserMessage("hi")], system_prompt="Be concise")

    result = asyncio.run(adapter.complete(context))

    assert result == AssistantMessage("hello")
    assert adapter.requests == [
        {"messages": [{"role": "user", "content": "hi"}], "system": "Be concise"}
    ]


def test_adapter_converts_tool_call_arguments_from_json():
    from examples.advanced.recording_adapter import FakeTransport, RecordingAdapter

    fixture = openai_response(
        tool_calls=[
            {
                "id": "call-1",
                "type": "function",
                "function": {"name": "read", "arguments": '{"path": "app.py"}'},
            }
        ],
        finish_reason="tool_calls",
    )

    result = asyncio.run(RecordingAdapter(FakeTransport([fixture])).complete(AgentContext()))

    assert result == AssistantMessage(
        "", [ToolCall("call-1", "read", {"path": "app.py"})], "tool_calls"
    )


@pytest.mark.parametrize("call_id", ["", "   ", 7])
def test_adapter_rejects_missing_tool_call_id(call_id):
    from examples.advanced.recording_adapter import (
        AdapterResponseError,
        FakeTransport,
        RecordingAdapter,
    )

    fixture = openai_response(
        tool_calls=[
            {"id": call_id, "function": {"name": "read", "arguments": "{}"}}
        ],
        finish_reason="tool_calls",
    )

    with pytest.raises(AdapterResponseError, match="tool call id"):
        asyncio.run(RecordingAdapter(FakeTransport([fixture])).complete(AgentContext()))


@pytest.mark.parametrize("arguments", ["not-json", "[]"])
def test_adapter_rejects_malformed_tool_arguments(arguments):
    from examples.advanced.recording_adapter import (
        AdapterResponseError,
        FakeTransport,
        RecordingAdapter,
    )

    fixture = openai_response(
        tool_calls=[
            {"id": "call-1", "function": {"name": "read", "arguments": arguments}}
        ],
        finish_reason="tool_calls",
    )

    with pytest.raises(AdapterResponseError, match="arguments.*JSON object"):
        asyncio.run(RecordingAdapter(FakeTransport([fixture])).complete(AgentContext()))


def test_adapter_rejects_duplicate_tool_call_ids():
    from examples.advanced.recording_adapter import (
        AdapterResponseError,
        FakeTransport,
        RecordingAdapter,
    )

    fixture = openai_response(
        tool_calls=[
            {"id": "dup", "function": {"name": "read", "arguments": "{}"}},
            {"id": "dup", "function": {"name": "write", "arguments": "{}"}},
        ],
        finish_reason="tool_calls",
    )

    with pytest.raises(AdapterResponseError, match="duplicate tool call id"):
        asyncio.run(RecordingAdapter(FakeTransport([fixture])).complete(AgentContext()))


def test_adapter_retries_transport_failures_with_a_bound():
    from examples.advanced.recording_adapter import FakeTransport, RecordingAdapter

    transport = FakeTransport(
        [TimeoutError("one"), TimeoutError("two"), openai_response(content="ok")]
    )

    result = asyncio.run(
        RecordingAdapter(transport, max_retries=2).complete(AgentContext())
    )

    assert result.content == "ok"
    assert len(transport.requests) == 3


def test_adapter_stops_retrying_after_the_configured_bound():
    from examples.advanced.recording_adapter import FakeTransport, RecordingAdapter

    transport = FakeTransport([TimeoutError("one"), TimeoutError("two")])

    with pytest.raises(TimeoutError, match="two"):
        asyncio.run(
            RecordingAdapter(transport, max_retries=1).complete(AgentContext())
        )

    assert len(transport.requests) == 2


def test_adapter_preserves_length_stop_reason():
    from examples.advanced.recording_adapter import FakeTransport, RecordingAdapter

    fixture = openai_response(content="partial", finish_reason="length")

    result = asyncio.run(
        RecordingAdapter(FakeTransport([fixture])).complete(AgentContext())
    )

    assert result == AssistantMessage("partial", stop_reason="length")


def test_adapter_rejects_malformed_provider_envelope():
    from examples.advanced.recording_adapter import (
        AdapterResponseError,
        FakeTransport,
        RecordingAdapter,
    )

    with pytest.raises(AdapterResponseError, match="provider response"):
        asyncio.run(
            RecordingAdapter(FakeTransport([{"choices": []}])).complete(AgentContext())
        )


def test_cli_runs_fake_model_and_supports_history_and_quit():
    from examples.advanced.interactive_cli import InteractiveCLI

    lines = iter(["hello", "/history", "/quit"])
    output = []
    cli = InteractiveCLI(
        model=FakeModel([AssistantMessage("offline answer")]),
        input_fn=lambda _prompt: next(lines),
        output_fn=output.append,
    )

    asyncio.run(cli.run())

    assert output == [
        "Mini Agent CLI (offline). Type /help for commands.",
        "assistant> offline answer",
        "user> hello",
        "assistant> offline answer",
        "Bye.",
    ]
    assert [message.role for message in cli.context.messages] == ["user", "assistant"]


def test_cli_supports_help_tools_and_cancel_commands():
    from examples.advanced.interactive_cli import InteractiveCLI

    class Tool:
        def __init__(self, name):
            self.name = name
            self.description = name

        async def execute(self, tool_call_id, arguments):
            return None

    lines = iter(["/help", "/tools", "/cancel", "/quit"])
    output = []
    cli = InteractiveCLI(
        model=FakeModel([]),
        tools=ToolRegistry([Tool("write"), Tool("read")]),
        input_fn=lambda _prompt: next(lines),
        output_fn=output.append,
    )

    asyncio.run(cli.run())

    assert output[1] == "Commands: /help /tools /history /cancel /quit"
    assert output[2] == "Tools: read, write"
    assert output[3] == "Cancellation requested."
    assert cli.cancellation.is_cancelled is True


def test_cli_can_start_a_new_turn_after_cancel():
    from examples.advanced.interactive_cli import InteractiveCLI

    lines = iter(["/cancel", "hello", "/quit"])
    output = []
    cli = InteractiveCLI(
        model=FakeModel([AssistantMessage("new turn")]),
        input_fn=lambda _prompt: next(lines),
        output_fn=output.append,
    )

    asyncio.run(cli.run())

    assert "assistant> new turn" in output
    assert cli.cancellation.is_cancelled is False


def test_cli_uses_fake_model_by_default():
    from examples.advanced.interactive_cli import InteractiveCLI

    cli = InteractiveCLI(
        input_fn=lambda _prompt: "/quit",
        output_fn=lambda _line: None,
    )

    assert isinstance(cli.model, FakeModel)


def test_recording_adapter_main_is_deterministic(capsys):
    from examples.advanced.recording_adapter import main

    main()

    assert capsys.readouterr().out == "assistant> Offline adapter response.\nrequests=1\n"
