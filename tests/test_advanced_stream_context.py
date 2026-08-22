import asyncio
import os
import subprocess
import sys
from pathlib import Path

import pytest

from examples.advanced.event_stream import BackpressurePolicy, EventStream, consume_events
from examples.advanced.context_budget import (
    ContextBudget,
    PinnedContentExceedsBudget,
    compact_context,
    measure_context,
)
from mini_agent.events import AgentEvent
from mini_agent.messages import AssistantMessage, ToolCall, ToolResultMessage, UserMessage


@pytest.mark.asyncio
async def test_block_policy_applies_backpressure_at_the_buffer_bound():
    stream = EventStream(maxsize=1, policy=BackpressurePolicy.BLOCK)
    first = AgentEvent("first", {})
    second = AgentEvent("second", {})

    await stream.publish(first)
    blocked_publish = asyncio.create_task(stream.publish(second))
    await asyncio.sleep(0)

    assert not blocked_publish.done()
    assert await anext(stream) == first
    await blocked_publish
    assert await anext(stream) == second


@pytest.mark.asyncio
async def test_close_delivers_buffered_events_then_explicit_end_of_stream():
    stream = EventStream(maxsize=2)
    event = AgentEvent("ready", {})
    await stream.publish(event)

    await stream.close()

    assert [item async for item in stream] == [event]
    with pytest.raises(RuntimeError, match="closed"):
        await stream.publish(AgentEvent("late", {}))


@pytest.mark.asyncio
async def test_drop_oldest_policy_never_blocks_and_reports_loss():
    stream = EventStream(maxsize=2, policy=BackpressurePolicy.DROP_OLDEST)
    events = [AgentEvent(str(index), {}) for index in range(3)]

    for event in events:
        await stream.publish(event)

    assert stream.dropped_count == 1
    assert await anext(stream) == events[1]
    assert await anext(stream) == events[2]


@pytest.mark.asyncio
async def test_consumer_cancellation_closes_and_drains_the_stream():
    stream = EventStream(maxsize=2)
    handler_started = asyncio.Event()

    async def stalled_handler(_event: AgentEvent) -> None:
        handler_started.set()
        await asyncio.Event().wait()

    consumer = asyncio.create_task(consume_events(stream, stalled_handler))
    await stream.publish(AgentEvent("in-flight", {}))
    await handler_started.wait()
    await stream.publish(AgentEvent("buffered", {}))

    consumer.cancel()
    with pytest.raises(asyncio.CancelledError):
        await consumer

    assert stream.closed
    assert stream.pending_count == 0
    with pytest.raises(StopAsyncIteration):
        await anext(stream)


@pytest.mark.asyncio
async def test_consumer_cancellation_releases_a_close_blocked_by_backpressure():
    stream = EventStream(maxsize=1)
    handler_started = asyncio.Event()

    async def stalled_handler(_event: AgentEvent) -> None:
        handler_started.set()
        await asyncio.Event().wait()

    consumer = asyncio.create_task(consume_events(stream, stalled_handler))
    await stream.publish(AgentEvent("in-flight", {}))
    await handler_started.wait()
    await stream.publish(AgentEvent("buffered", {}))
    blocked_close = asyncio.create_task(stream.close())
    await asyncio.sleep(0)
    assert not blocked_close.done()

    consumer.cancel()
    with pytest.raises(asyncio.CancelledError):
        await consumer

    await asyncio.wait_for(blocked_close, timeout=0.2)
    assert stream.pending_count == 0


@pytest.mark.asyncio
async def test_direct_cancellation_of_blocked_close_still_terminates_iteration():
    stream = EventStream(maxsize=1)
    event = AgentEvent("buffered-before-close", {})
    await stream.publish(event)
    blocked_close = asyncio.create_task(stream.close())
    await asyncio.sleep(0)
    assert not blocked_close.done()

    blocked_close.cancel()
    with pytest.raises(asyncio.CancelledError):
        await blocked_close

    assert stream.closed
    assert await anext(stream) == event
    with pytest.raises(StopAsyncIteration):
        await asyncio.wait_for(anext(stream), timeout=0.2)


@pytest.mark.asyncio
async def test_consumer_cancellation_rejects_blocked_publishers_without_leaking_events():
    stream = EventStream(maxsize=1)
    handler_started = asyncio.Event()

    async def stalled_handler(_event: AgentEvent) -> None:
        handler_started.set()
        await asyncio.Event().wait()

    consumer = asyncio.create_task(consume_events(stream, stalled_handler))
    await stream.publish(AgentEvent("in-flight", {}))
    await handler_started.wait()
    await stream.publish(AgentEvent("buffered", {}))
    blocked_publish = asyncio.create_task(stream.publish(AgentEvent("blocked", {})))
    await asyncio.sleep(0)
    assert not blocked_publish.done()

    consumer.cancel()
    with pytest.raises(asyncio.CancelledError):
        await consumer
    with pytest.raises(RuntimeError, match="closed"):
        await asyncio.wait_for(blocked_publish, timeout=0.2)

    assert stream.pending_count == 0


@pytest.mark.asyncio
async def test_direct_publisher_cancellation_cleans_up_blocked_put_task():
    stream = EventStream(maxsize=1)
    await stream.publish(AgentEvent("buffered", {}))
    blocked_publish = asyncio.create_task(
        stream.publish(AgentEvent("cancelled", {}))
    )
    await asyncio.sleep(0)
    assert not blocked_publish.done()

    blocked_publish.cancel()
    with pytest.raises(asyncio.CancelledError):
        await blocked_publish
    await stream.abort()
    await asyncio.sleep(0)

    assert stream.pending_count == 0
    assert stream.buffer_size == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("scheduling_yields", [1, 2])
async def test_abort_racing_new_publisher_leaves_no_event_or_negative_count(
    scheduling_yields,
):
    stream = EventStream(maxsize=1)
    publisher = asyncio.create_task(stream.publish(AgentEvent("racing", {})))
    for _ in range(scheduling_yields):
        await asyncio.sleep(0)

    await stream.abort()
    result = (await asyncio.gather(publisher, return_exceptions=True))[0]

    assert result is None or isinstance(result, RuntimeError)
    assert stream.pending_count == 0
    assert stream.buffer_size == 0


def test_measure_context_reports_messages_and_approximate_characters():
    messages = [UserMessage("hello"), AssistantMessage("world")]

    measurement = measure_context(messages)

    assert measurement.message_count == 2
    assert measurement.char_count >= len("helloworld")
    assert measurement.kind == "messages/chars (approximate, not tokens)"


def test_compaction_preserves_latest_request_and_atomic_tool_pair():
    latest_request = UserMessage("please inspect current.py")
    tool_call = AssistantMessage("", [ToolCall("read-1", "read", {"path": "current.py"})])
    tool_result = ToolResultMessage("read-1", "read", "current contents")
    final_answer = AssistantMessage("inspection complete")
    messages = [
        UserMessage("stale request"),
        AssistantMessage("stale answer"),
        latest_request,
        tool_call,
        tool_result,
        final_answer,
    ]

    result = compact_context(messages, ContextBudget(max_messages=4, max_chars=10_000))

    assert result.messages == [latest_request, tool_call, tool_result, final_answer]
    assert result.removed_message_count == 2
    assert result.after.message_count == 4


def test_compaction_pins_the_most_recent_side_effect_evidence():
    request = UserMessage("update the file")
    write_call = AssistantMessage("", [ToolCall("write-1", "write", {"path": "a.py"})])
    write_result = ToolResultMessage("write-1", "write", "wrote a.py")
    later_comment = AssistantMessage("a later but disposable comment")

    result = compact_context(
        [request, write_call, write_result, later_comment],
        ContextBudget(max_messages=3, max_chars=10_000),
    )

    assert result.messages == [request, write_call, write_result]


def test_compaction_rejects_when_pinned_content_alone_exceeds_budget():
    messages = [
        UserMessage("keep this request"),
        AssistantMessage("", [ToolCall("edit-1", "edit", {"path": "a.py"})]),
        ToolResultMessage("edit-1", "edit", "edited a.py"),
    ]

    with pytest.raises(PinnedContentExceedsBudget) as error:
        compact_context(messages, ContextBudget(max_messages=2, max_chars=10_000))

    assert error.value.measurement.message_count == 3
    assert "pinned content" in str(error.value)


@pytest.mark.parametrize(
    ("example", "expected_lines"),
    [
        ("event_stream.py", ["events=0,1,2", "dropped=0 closed=True"]),
        ("context_budget.py", ["before=6 messages", "after=4 messages", "latest_user_kept=True"]),
    ],
)
def test_advanced_examples_have_deterministic_executable_mains(example, expected_lines):
    root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(root / "src")

    completed = subprocess.run(
        [sys.executable, str(root / "examples" / "advanced" / example)],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.splitlines() == expected_lines
