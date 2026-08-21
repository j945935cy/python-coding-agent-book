# 14. 串流輸出與事件系統

## 本章目標

理解為什麼使用者介面不應直接猜測 Agent 狀態，以及如何用事件把模型回應、工具開始、工具結束與錯誤傳出去。

## 事件是觀測邊界

目前原型以 `AgentEvent` 表示事件：

```python
AgentEvent("tool_start", {"id": call.id, "name": call.name})
AgentEvent("tool_end", {"id": call.id, "name": call.name})
```

這個事件不是完整 UI 協定，而是核心迴圈與外部觀測端之間的邊界。日後加入串流模型時，可以新增文字增量事件，而不必讓工具本身知道終端機或 WebSocket。

## 事件時間軸與消費端

一次正常工具呼叫的最小時間軸是：

```text
model response → tool_start(call-1) → tool executes → tool_end(call-1) → next model response
```

消費端只依賴事件名稱與 payload，不直接讀取 Agent Loop 內部變數：

```python
def render_event(event):
    if event.kind == "tool_start":
        return f"開始：{event.data['name']}"
    if event.kind == "tool_end":
        return f"結束：{event.data['name']}"
    return None
```

同一個 `call.id` 讓消費端配對開始與結束。未來平行工具同時執行時，不能只靠事件出現順序判斷哪一個工具完成。

## 為什麼一定要 finally

工具可能成功、失敗或逾時。若只在成功路徑送出 `tool_end`，介面就可能永遠顯示執行中。本專案把收尾放在 `finally`，並用測試驗證失敗工具仍有成對事件。

## 練習

1. 新增 `model_start` 與 `model_end` 事件。
2. 為事件加入 turn number。
3. 設計一個事件消費者，把事件轉成純文字 CLI 輸出。

## 本章驗收

- 能列出工具執行的生命週期事件。
- 能說明串流文字與狀態事件的差異。
- 工具失敗時仍能收到結束事件。
