"""Bounded asynchronous event stream prototype.

This example deliberately adapts events outside ``run_agent_loop``; the core loop's
existing list collector remains unchanged. A single ``asyncio.Condition`` owns the
deque buffer and lifecycle state so publish/close/abort cannot leave orphaned tasks.
"""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import AsyncIterator, Final

from mini_agent.events import AgentEvent


class BackpressurePolicy(str, Enum):
    """Behavior when a producer reaches the bounded event-buffer capacity."""

    BLOCK = "block"
    DROP_OLDEST = "drop_oldest"


END_OF_STREAM: Final = object()
"""Explicit buffer sentinel used to distinguish closure from an event."""


class EventStream(AsyncIterator[AgentEvent]):
    """A bounded, single-consumer stream with atomic lifecycle transitions."""

    def __init__(self, maxsize: int, policy: BackpressurePolicy = BackpressurePolicy.BLOCK) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        self.maxsize = maxsize
        self.policy = policy
        self._items: deque[AgentEvent | object] = deque()
        self._condition = asyncio.Condition()
        self._closed = False
        self._aborted = False
        self._ended = False
        self._dropped_count = 0
        self._pending_count = 0

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def dropped_count(self) -> int:
        return self._dropped_count

    @property
    def pending_count(self) -> int:
        return self._pending_count

    @property
    def buffer_size(self) -> int:
        """Number of buffered event/sentinel items, exposed for lifecycle tests."""
        return len(self._items)

    def __aiter__(self) -> EventStream:
        return self

    async def __anext__(self) -> AgentEvent:
        async with self._condition:
            while not self._items:
                if self._ended or self._aborted:
                    raise StopAsyncIteration
                await self._condition.wait()

            item = self._items.popleft()
            if item is END_OF_STREAM:
                self._ended = True
                self._condition.notify_all()
                raise StopAsyncIteration

            assert isinstance(item, AgentEvent)
            self._pending_count -= 1
            self._condition.notify_all()
            return item

    async def publish(self, event: AgentEvent) -> None:
        async with self._condition:
            if self._closed:
                raise RuntimeError("event stream is closed")

            if self.policy is BackpressurePolicy.DROP_OLDEST:
                if self._pending_count >= self.maxsize:
                    dropped = self._items.popleft()
                    assert isinstance(dropped, AgentEvent)
                    self._pending_count -= 1
                    self._dropped_count += 1
            else:
                while self._pending_count >= self.maxsize and not self._closed:
                    await self._condition.wait()
                if self._closed:
                    raise RuntimeError("event stream is closed")

            self._items.append(event)
            self._pending_count += 1
            self._condition.notify_all()

    async def close(self) -> None:
        """Normally close, retaining buffered events ahead of the sentinel."""
        async with self._condition:
            if self._closed:
                return
            self._closed = True
            self._condition.notify_all()  # Reject blocked/new publishers.

            try:
                while self._pending_count >= self.maxsize and not self._aborted:
                    await self._condition.wait()
            except asyncio.CancelledError:
                if not self._aborted and END_OF_STREAM not in self._items:
                    # Cancellation must not strand consumers on a closed stream.
                    # The control sentinel may temporarily exceed event capacity.
                    self._items.append(END_OF_STREAM)
                    self._condition.notify_all()
                raise
            if self._aborted:
                return

            self._items.append(END_OF_STREAM)
            self._condition.notify_all()

    async def abort(self) -> None:
        """Atomically close and discard every pending event."""
        async with self._condition:
            self._closed = True
            self._aborted = True
            self._ended = True
            self._items.clear()
            self._pending_count = 0
            self._condition.notify_all()


async def consume_events(
    stream: EventStream,
    handler: Callable[[AgentEvent], Awaitable[None]],
) -> None:
    """Consume events and abort pending work if the consumer is cancelled."""
    try:
        async for event in stream:
            await handler(event)
    except asyncio.CancelledError:
        await stream.abort()
        raise


async def main() -> None:
    stream = EventStream(maxsize=2)
    seen: list[str] = []

    async def record(event: AgentEvent) -> None:
        seen.append(event.type)

    consumer = asyncio.create_task(consume_events(stream, record))
    for index in range(3):
        await stream.publish(AgentEvent(str(index), {}))
    await stream.close()
    await consumer

    print("events=" + ",".join(seen))
    print(f"dropped={stream.dropped_count} closed={stream.closed}")


if __name__ == "__main__":
    asyncio.run(main())
