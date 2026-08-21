from mini_agent.agent_loop import run_agent_loop
from mini_agent.config import AgentConfig
from mini_agent.context import AgentContext
from mini_agent.messages import AssistantMessage, ToolCall, UserMessage
from mini_agent.model_client import FakeModel
from mini_agent.tools import CalculatorTool, ToolRegistry


async def main() -> None:
    model = FakeModel([
        AssistantMessage(
            content="",
            tool_calls=[ToolCall("calc-1", "calculator", {"operation": "add", "left": 2, "right": 3})],
        ),
        AssistantMessage(content="計算結果是 5。"),
    ])
    context = AgentContext(messages=[UserMessage("2 加 3 是多少？")])
    result = await run_agent_loop(model, context, ToolRegistry([CalculatorTool()]), AgentConfig())
    print(result[-1].content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
