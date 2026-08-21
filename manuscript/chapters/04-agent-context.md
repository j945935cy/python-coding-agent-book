# 4. 建立 Agent Context

## 本章目標

理解 Context 是模型下一次決策所需的狀態集合，而不是永遠增長的聊天紀錄。

## 最小 Context

本專案的 `AgentContext` 包含 messages、system prompt 與 metadata，並提供 `convert_to_llm()` 將內部訊息轉成模型 payload。

```python
context = AgentContext(messages=[UserMessage("讀取 README")])
payload = context.convert_to_llm()
```

Context 的重要規則是：Loop 修改它，ModelClient 讀取它，工具結果回到它。工具不應直接修改模型 client 的內部狀態。

## Context 管理

短範例可以保存全部訊息；長時間 Agent 則需要截斷、摘要、保留最近工具錯誤或依優先級選擇內容。這些策略應放在 Context 層，不能散落在每個工具裡。

## 練習

1. 使用 metadata 記錄 workspace 路徑。
2. 實作只保留最近 N 個 tool result 的原型。
3. 討論 system prompt 是否應進入 `convert_to_llm()` 的回傳值。

## 本章驗收

- 能把訊息轉成穩定 payload。
- 能區分對話歷史與本回合必要 Context。
- 不讓工具直接依賴特定模型 SDK。
