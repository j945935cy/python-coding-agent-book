from __future__ import annotations

import asyncio

from mini_agent.context import AgentContext
from mini_agent.messages import AssistantMessage, UserMessage
from mini_agent.model_client import FakeModel


async def main() -> None:
    model = FakeModel([AssistantMessage("這只是一次模型回應。")])
    context = AgentContext([UserMessage("請回答，但不要使用工具")])
    response = await model.complete(context)
    print(response.content)


if __name__ == "__main__":
    asyncio.run(main())
