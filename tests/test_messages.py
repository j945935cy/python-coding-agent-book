from mini_agent.messages import AssistantMessage, ToolCall, ToolResultMessage, UserMessage


def test_messages_serialize_with_explicit_roles():
    messages = [
        UserMessage(content="hello"),
        AssistantMessage(content="hi", tool_calls=[ToolCall("c1", "read", {"path": "a.py"})]),
        ToolResultMessage(tool_call_id="c1", tool_name="read", content="print(1)"),
    ]

    payload = [message.to_dict() for message in messages]

    assert [item["role"] for item in payload] == ["user", "assistant", "tool"]
    assert payload[1]["tool_calls"][0]["name"] == "read"
    assert payload[2]["tool_call_id"] == "c1"
