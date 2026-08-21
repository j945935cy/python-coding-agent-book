# 5. 設定、Callback 與依賴注入

## 本章目標

把最大回合數、工具逾時、循序／平行模式與安全 Hook 放到可測試的設定與依賴中。

## Config 不是全域變數

`AgentConfig` 是不可變 dataclass，建立 Agent 時注入。這讓測試可以用短逾時或 `max_turns=1`，而不會污染其他測試。

```python
config = AgentConfig(max_turns=4, tool_timeout_seconds=2)
```

## Callback 的位置

`before_tool_call` 位於參數驗證之後、實際工具執行之前。它可以做 approval、記錄、政策判斷或取消檢查。Callback 可以是同步函式，也可以是 async 函式，Loop 會統一處理。

## 依賴注入

Model、ToolRegistry、Config、事件收集器與取消 Token 都由呼叫端提供。這讓核心 Loop 不必建立網路連線、讀取全域設定或偷偷寫檔案。

## 練習

1. 寫一個只允許 Read、不允許 Bash 的安全 Hook。
2. 測試同步與非同步 Hook 都能阻擋工具。
3. 為 Config 增加不可接受值的測試。

## 本章驗收

能建立一個不依賴全域狀態的 Agent Loop，並在測試中替換模型、工具與安全政策。
