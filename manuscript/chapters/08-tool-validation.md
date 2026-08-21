# 8. 驗證模型產生的工具參數

## 本章目標

理解工具名稱與參數驗證為什麼必須在 Registry 與實際執行之間再做一次。

## 不可信的不是只有使用者

即使模型供應商宣稱回傳結構化工具呼叫，仍可能出現未知工具、缺少 ID、參數不是 JSON object，或參數型態錯誤。`validate_tool_call()` 先檢查最基本的契約，再交給具體工具處理業務規則。

```python
validate_tool_call(call, tools.names())
```

這一層不假裝自己是完整 Schema 系統。它只負責通用不變條件，讓 Calculator、Read、Edit 等工具保留自己的細節驗證。

## 錯誤應該回到模型

Agent Loop 將工具執行例外包裝成 `ToolResultMessage(is_error=True)`，讓模型有機會修正下一步，而不是讓一次工具錯誤摧毀整個程序。這裡仍須搭配最大回合數，避免模型在錯誤上無限重試。

## 練習

1. 為參數加入 JSON Schema 選配層，但不要讓核心依賴它。
2. 測試未知工具與非 object arguments。
3. 設計一個「不可恢復」錯誤，討論它是否應直接終止 Agent。

## 本章驗收

- `tests/test_validation.py` 通過。
- 未知工具不會被執行。
- 工具錯誤有明確 `is_error` 標記。
