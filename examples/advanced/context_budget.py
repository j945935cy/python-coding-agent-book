"""Pure message/character context measurement and compaction prototype.

The estimates intentionally are not tokenizer counts, and this module is not wired
into the agent loop.
"""

from __future__ import annotations

import json
from collections.abc import Collection
from dataclasses import dataclass
from typing import Final

from mini_agent.messages import AssistantMessage, Message, ToolCall, ToolResultMessage, UserMessage


DEFAULT_SIDE_EFFECT_TOOLS: Final[frozenset[str]] = frozenset(
    {"write", "edit", "bash", "delete", "move"}
)


@dataclass(frozen=True, slots=True)
class ContextMeasurement:
    message_count: int
    char_count: int
    kind: str = "messages/chars (approximate, not tokens)"


@dataclass(frozen=True, slots=True)
class ContextBudget:
    max_messages: int
    max_chars: int

    def __post_init__(self) -> None:
        if self.max_messages <= 0 or self.max_chars <= 0:
            raise ValueError("context budgets must be positive")


@dataclass(frozen=True, slots=True)
class CompactionResult:
    messages: list[Message]
    before: ContextMeasurement
    after: ContextMeasurement
    removed_message_count: int


class PinnedContentExceedsBudget(ValueError):
    """Raised instead of silently dropping required context."""

    def __init__(self, measurement: ContextMeasurement, budget: ContextBudget) -> None:
        self.measurement = measurement
        self.budget = budget
        super().__init__(
            "pinned content exceeds budget: "
            f"{measurement.message_count}/{budget.max_messages} messages, "
            f"{measurement.char_count}/{budget.max_chars} chars"
        )


def _message_chars(message: Message) -> int:
    return len(
        json.dumps(
            message.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=repr,
        )
    )


def measure_context(messages: list[Message]) -> ContextMeasurement:
    """Measure serialized messages with a deterministic character approximation."""
    return ContextMeasurement(
        message_count=len(messages),
        char_count=sum(_message_chars(message) for message in messages),
    )


def _atomic_groups(messages: list[Message]) -> list[list[int]]:
    """Keep each assistant tool-call message with its contiguous results."""
    groups: list[list[int]] = []
    index = 0
    while index < len(messages):
        group = [index]
        message = messages[index]
        index += 1
        if isinstance(message, AssistantMessage) and message.tool_calls:
            call_ids = {call.id for call in message.tool_calls}
            while index < len(messages):
                result = messages[index]
                if not isinstance(result, ToolResultMessage) or result.tool_call_id not in call_ids:
                    break
                group.append(index)
                index += 1
        groups.append(group)
    return groups


def _fits(messages: list[Message], budget: ContextBudget) -> bool:
    measurement = measure_context(messages)
    return (
        measurement.message_count <= budget.max_messages
        and measurement.char_count <= budget.max_chars
    )


def _group_has_side_effect(
    messages: list[Message], group: list[int], side_effect_tools: Collection[str]
) -> bool:
    for index in group:
        message = messages[index]
        if isinstance(message, AssistantMessage):
            if any(call.name in side_effect_tools for call in message.tool_calls):
                return True
    return False


def compact_context(
    messages: list[Message],
    budget: ContextBudget,
    *,
    side_effect_tools: Collection[str] = DEFAULT_SIDE_EFFECT_TOOLS,
) -> CompactionResult:
    """Select recent atomic groups while always pinning the latest user request."""
    groups = _atomic_groups(messages)
    latest_user_index = next(
        (index for index in range(len(messages) - 1, -1, -1) if isinstance(messages[index], UserMessage)),
        None,
    )
    pinned_groups = {
        group_index
        for group_index, group in enumerate(groups)
        if latest_user_index is not None and latest_user_index in group
    }
    latest_side_effect_group = next(
        (
            group_index
            for group_index in range(len(groups) - 1, -1, -1)
            if _group_has_side_effect(messages, groups[group_index], side_effect_tools)
        ),
        None,
    )
    if latest_side_effect_group is not None:
        pinned_groups.add(latest_side_effect_group)
    pinned_indexes = sorted(index for group_index in pinned_groups for index in groups[group_index])
    pinned_messages = [messages[index] for index in pinned_indexes]
    if not _fits(pinned_messages, budget):
        raise PinnedContentExceedsBudget(measure_context(pinned_messages), budget)
    selected = set(pinned_groups)

    for group_index in range(len(groups) - 1, -1, -1):
        if group_index in selected:
            continue
        candidate_indexes = sorted(
            index
            for selected_group in selected | {group_index}
            for index in groups[selected_group]
        )
        if _fits([messages[index] for index in candidate_indexes], budget):
            selected.add(group_index)

    selected_indexes = sorted(index for group_index in selected for index in groups[group_index])
    compacted = [messages[index] for index in selected_indexes]
    before = measure_context(messages)
    after = measure_context(compacted)
    return CompactionResult(compacted, before, after, before.message_count - after.message_count)


def main() -> None:
    latest_user = UserMessage("inspect current.py")
    messages: list[Message] = [
        UserMessage("stale request"),
        AssistantMessage("stale answer"),
        latest_user,
        AssistantMessage("", [ToolCall("read-1", "read", {"path": "current.py"})]),
        ToolResultMessage("read-1", "read", "print('current')"),
        AssistantMessage("inspection complete"),
    ]
    result = compact_context(messages, ContextBudget(max_messages=4, max_chars=10_000))

    print(f"before={result.before.message_count} messages")
    print(f"after={result.after.message_count} messages")
    print(f"latest_user_kept={latest_user in result.messages}")


if __name__ == "__main__":
    main()
