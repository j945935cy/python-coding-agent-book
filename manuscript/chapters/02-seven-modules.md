# 2. 把 Agent Loop 拆成七個模組

## 本章目標

把看似神奇的 Agent 拆成可替換的責任：訊息、Context、模型、工具、驗證、安全、控制流程。

## 七個模組

1. Message：描述對話與工具結果。
2. Context：保存目前回合需要的狀態。
3. ModelClient：把 Context 交給模型並取得下一個 assistant message。
4. Tool：執行一個明確、有限的能力。
5. Registry：依名稱找到工具，避免 Loop 知道所有具體類別。
6. Validation／Safety：在執行前檢查名稱、參數、路徑與權限。
7. Agent Loop：決定何時呼叫模型、工具與停止。

## 為什麼要拆開

拆分不是為了檔案數量，而是為了替換成本。FakeModel 可以換成真正 Adapter，Calculator 可以換成 Read，不必重寫 Loop。每個模組也能有自己的失敗測試。

## 資料流

```text
AgentContext → ModelClient → AssistantMessage
AssistantMessage → Validation → Safety Hook → ToolRegistry
ToolResultMessage → AgentContext → 下一回合
```

## 練習

1. 指出哪個模組應該知道 API Key。
2. 指出哪個模組應該負責 Workspace 邊界。
3. 把 `max_turns` 放進 Config 而不是寫死在工具中，說明原因。

## 本章驗收

能畫出七個模組與資料流，並能說明每個模組的單一責任。
