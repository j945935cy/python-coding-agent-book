# 17. 安全攔截、權限與 Context 管理

## 本章目標

把工具安全從「提示詞要求」提升為程式碼能強制執行的政策。

## 三道邊界

第一道是參數驗證：工具名稱、ID、arguments 形狀必須正確。第二道是 Workspace：檔案路徑必須落在根目錄內。第三道是 Safety Hook：在執行前依工具名稱、使用者核准與環境政策決定是否允許。

```python
async def allow_read_only(_id, name, _args):
    return name == "read"
```

這些邊界不能只放在 system prompt。提示詞可以協助模型，但不能替代權限檢查。

## Context 的安全與成本

Context 可能包含檔案內容、工具錯誤與使用者資料。應限制讀取大小、避免重複注入秘密、在長回合中摘要舊訊息，並保留能解釋目前決策的最小證據。

## 練習

1. 寫一個只允許 Calculator 與 Read 的 Hook。
2. 讓 ReadTool 限制單次讀取 bytes。
3. 列出 Bash 工具需要 approval 的三種情況。

## 本章驗收

能指出每個安全檢查所在的層級，並能說明為什麼「模型答應不做危險事」不是安全控制。
