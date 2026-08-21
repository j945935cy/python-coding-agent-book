# 7. 建立通用工具介面與工具註冊表

## 本章目標

讓 Agent Loop 只依賴工具協定與 Registry，而不需要知道每個工具的類別實作。

## 工具協定

每個工具提供 name、description 與 async execute：

```python
class ToolRegistry:
    registry = ToolRegistry([CalculatorTool(), ReadTool(workspace)])
```

實際程式使用 `register()` 與 `execute()`，Registry 以工具名稱查找實例。重複名稱在註冊時立即失敗，避免模型看到的工具描述與實際執行對象不一致。

## Registry 的責任邊界

Registry 負責查找與分派，不負責解讀每個工具的業務參數。通用的工具名稱與 arguments 型態由 validation 層檢查，具體欄位則由工具自己驗證。

## 練習

1. 寫一個回傳固定文字的 `PingTool`。
2. 測試重複工具名稱會失敗。
3. 讓 Registry 輸出工具描述，思考如何交給 ModelClient。

## 本章驗收

- 可註冊多個工具。
- 未知工具不會被執行。
- Loop 不需要 import 每一個具體工具類別。
