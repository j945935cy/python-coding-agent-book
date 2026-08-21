# 16. 中止、錯誤與恢復

## 本章目標

建立「可停止」的 Agent，而不是只能等待它完成或強制殺掉整個程序。

## 合作式取消

`CancellationToken` 由呼叫端持有：

```python
token = CancellationToken()
token.cancel("user requested stop")
```

Agent Loop 在每回合與工具開始前檢查 Token。這是合作式取消：正在執行的同步函式不一定能立刻停止，但下一個安全邊界不會再啟動新的模型或工具工作。

## 錯誤不是一種

工具輸入錯誤通常可以回傳 `ToolResultMessage(is_error=True)`，讓模型修正參數。使用者主動取消則應拋出 `AgentCancelled`，不應假裝成一般工具錯誤。逾時則必須中止子程序或 await，避免背景工作繼續修改 Workspace。

## 恢復的最小策略

第一版只做三件事：保存已完成訊息、把可恢復工具錯誤交回模型、用 `max_turns` 阻止無限重試。重試、斷點恢復與 Context 壓縮留到後續版本，避免一開始把控制流程做成不可測試的狀態機。

## 練習

1. 在工具執行前取消 Token，確認工具不會被呼叫。
2. 模擬工具失敗後由 FakeModel 回覆修正答案。
3. 設計一個恢復檔案，記錄最後一個完成的 tool call ID。

## 本章驗收

- 取消後不會請求下一次模型回應。
- 工具錯誤與使用者取消有不同語意。
- `max_turns` 能阻止持續失敗的模型無限循環。
