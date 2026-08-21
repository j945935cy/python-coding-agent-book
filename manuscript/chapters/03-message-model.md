# 3. 用 Python 表示對話訊息

## 本章目標

本章建立 `UserMessage`、`AssistantMessage`、`ToolResultMessage` 與 `ToolCall`，讓對話不再只是散落的字串。

## 為什麼要有明確角色

模型需要知道一段內容是使用者要求、助手回答，還是工具執行結果。若只把所有內容串成一個字串，後續很難驗證：哪一段可以由模型產生？哪一段必須保留工具 ID？哪一段是錯誤？

本專案以 dataclass 表示訊息：

```python
from mini_agent.messages import ToolCall, UserMessage

message = UserMessage(content="讀取 README")
call = ToolCall(id="call-1", name="read", arguments={"path": "README.md"})
```

每種訊息都提供 `to_dict()`，把內部模型轉成供 ModelClient 使用的 payload。這個邊界讓內部測試不必依賴某家供應商的 SDK。

## 工具呼叫不是文字猜謎

`ToolCall` 至少需要三個欄位：唯一 ID、工具名稱、物件型參數。工具結果必須帶回同一個 ID，否則平行工具執行時，模型無法知道哪個結果屬於哪個呼叫。

## 練習

1. 新增一個 `SystemMessage`，思考它是否需要進入公開 `Message` Union。
2. 為空的工具 ID 加入測試。
3. 將一組訊息轉成 dict，檢查角色順序是否保持不變。

## 本章驗收

- `tests/test_messages.py` 通過。
- 能說明 assistant message 與 tool result message 的差異。
- 不使用位置猜測配對工具結果。
