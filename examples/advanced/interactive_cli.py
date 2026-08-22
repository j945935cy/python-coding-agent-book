"""A dependency-injected, offline interactive CLI for ``mini_agent``."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

from mini_agent.agent_loop import run_agent_loop
from mini_agent.cancellation import CancellationToken
from mini_agent.config import AgentConfig
from mini_agent.context import AgentContext
from mini_agent.messages import AssistantMessage, UserMessage
from mini_agent.model_client import FakeModel, ModelClient
from mini_agent.tools.base import ToolRegistry

InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]


class InteractiveCLI:
    def __init__(
        self,
        *,
        model: ModelClient | None = None,
        tools: ToolRegistry | None = None,
        input_fn: InputFn = input,
        output_fn: OutputFn = print,
    ) -> None:
        self.model = (
            model
            if model is not None
            else FakeModel([AssistantMessage("Offline demo response.")] * 100)
        )
        self.tools = tools if tools is not None else ToolRegistry()
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.context = AgentContext()
        self.cancellation = CancellationToken()
        self.config = AgentConfig()

    async def run(self) -> None:
        self.output_fn("Mini Agent CLI (offline). Type /help for commands.")
        while True:
            try:
                line = self.input_fn("you> ").strip()
            except (EOFError, StopIteration):
                line = "/quit"
            if not line:
                continue
            if line == "/quit":
                self.output_fn("Bye.")
                return
            if line == "/help":
                self.output_fn("Commands: /help /tools /history /cancel /quit")
                continue
            if line == "/tools":
                names = sorted(self.tools.names())
                self.output_fn(f"Tools: {', '.join(names) if names else '(none)'}")
                continue
            if line == "/cancel":
                self.cancellation.cancel("cancelled from CLI")
                self.output_fn("Cancellation requested.")
                continue
            if line == "/history":
                for message in self.context.messages:
                    self.output_fn(f"{message.role}> {message.content}")
                continue

            if self.cancellation.is_cancelled:
                self.cancellation = CancellationToken()
            self.context.messages.append(UserMessage(line))
            history = await run_agent_loop(
                self.model,
                self.context,
                self.tools,
                self.config,
                cancellation=self.cancellation,
            )
            self.output_fn(f"assistant> {history[-1].content}")


def main() -> None:
    asyncio.run(InteractiveCLI().run())


if __name__ == "__main__":
    main()
