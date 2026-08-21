# 13. 第一個完整 Agent Loop

## 本章目標

把訊息、FakeModel、工具 Registry 與 ToolResult 串成一個可重複測試的完整迴圈。

## Loop 的最小演算法

```text
1. 檢查取消訊號
2. 將 Context 交給模型
3. 保存 assistant message
4. 沒有工具呼叫：完成
5. 有工具呼叫：驗證、執行、保存結果
6. 回到第 1 步，直到完成或超過 max_turns
```

`run_agent_loop()` 保持這個流程可讀，工具的具體行為則由 Registry 注入。這樣測試可以用 `FakeModel` 控制模型行為，而不必模擬網路。

## 兩個重要停止條件

第一是正常完成：assistant 沒有 tool calls。第二是保護性停止：模型輸出被截斷、收到取消訊號，或超過 `max_turns`。任何一條都應有測試，因為「停止」本身就是 Agent 的功能。

## 事件收尾

工具開始前加入 `tool_start`，結束時在 `finally` 加入 `tool_end`。因此即使工具丟出例外，觀測端仍能配對事件，避免 UI 一直顯示「執行中」。

## 練習

1. 將 `max_turns` 設為 1，觀察持續工具呼叫如何停止。
2. 將工具改成拋出例外，確認模型可以收到錯誤結果並繼續。
3. 為每回合加入 turn number 事件資料。

## 本章驗收

- `tests/test_agent_loop.py` 通過。
- 工具呼叫後模型能取得 ToolResult。
- 正常結束、截斷、錯誤與最大回合數都有測試。
