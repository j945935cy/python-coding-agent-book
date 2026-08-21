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

## 權限決策表

| 工具或情況 | 預設政策 | 是否需要核准 | 原因 |
|---|---|---|---|
| Calculator | 允許 | 否 | 無 Workspace 副作用 |
| Read | 限定 Workspace | 視敏感資料而定 | 可能讀到秘密或大型檔案 |
| Write／Edit | 限定 Workspace | 建議 | 會改變專案狀態 |
| Bash 測試命令 | allowlist | 視環境而定 | 仍可能產生檔案或耗用資源 |
| Bash 未知命令 | 拒絕 | 是 | 副作用與權限範圍不明 |

政策應先給出安全預設，再由呼叫端明確擴權；不要讓模型自行把未知操作解釋成允許。

## Context 的安全與成本

Context 可能包含檔案內容、工具錯誤與使用者資料。應限制讀取大小、避免重複注入秘密、在長回合中摘要舊訊息，並保留能解釋目前決策的最小證據。

第一版可以先使用可測量的雙重預算，而不是等供應商回報 token 才處理：

```python
def within_context_budget(messages, max_messages=40, max_chars=60_000):
    if len(messages) > max_messages:
        return False
    return sum(len(str(message)) for message in messages) <= max_chars
```

這不是精準 token 計算，但能先阻止無限制成長。超過預算時應保留 system prompt、最近工具結果與目前任務證據，再摘要較舊訊息；不要直接刪掉尚未配對的 tool call 與 tool result。

## 練習

1. 寫一個只允許 Calculator 與 Read 的 Hook。
2. 讓 ReadTool 限制單次讀取 bytes。
3. 列出 Bash 工具需要 approval 的三種情況。

## 本章驗收

能指出每個安全檢查所在的層級，並能說明為什麼「模型答應不做危險事」不是安全控制。
