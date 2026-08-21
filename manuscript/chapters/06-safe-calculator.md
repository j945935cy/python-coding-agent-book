# 6. 第一個工具：安全計算機

## 本章目標

先完成一個低風險工具，理解工具介面、參數驗證與「不要把模型輸出當成 Python 程式執行」。

## 為什麼不用 `eval()`

把模型輸出的算式直接交給 `eval()`，等於把執行權交給不可信輸入。即使目前只想做加法，輸入也可能混入檔案操作或其他副作用。

`CalculatorTool` 改用固定操作表：

```python
_operations = {
    "add": operator.add,
    "subtract": operator.sub,
    "multiply": operator.mul,
}
```

工具只接受操作名稱與兩個數字，未知操作直接拒絕。這種設計雖然不像完整數學解析器，但責任清楚、測試容易，適合第一個垂直切片。

## 執行與測試

```bash
uv run pytest tests/test_calculator.py -q
```

測試同時確認正常結果與未知操作錯誤。錯誤路徑不是附加功能，而是工具契約的一部分。

## 練習

1. 加入 `divide`，並處理除以零。
2. 禁止布林值被當成數字使用。
3. 為 Calculator 加入一個不會執行任意程式碼的百分比操作。

## 本章驗收

- 不使用 `eval()`。
- 未知 operation 會失敗。
- 工具可獨立測試，也可由 Agent Loop 呼叫。
