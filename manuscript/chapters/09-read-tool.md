# 9. Read：安全讀取檔案

## 本章目標

建立第一個 Coding 工具，讓 Agent 能讀取 Workspace 內的文字檔案，同時拒絕透過 `..` 走出工作區。

## 工具的責任

`ReadTool` 不負責理解 Python，也不負責決定模型下一步。它只做三件事：接收相對路徑、把路徑交給 Workspace 安全層、以 UTF-8 讀取文字。

```python
read = ReadTool(workspace)
content = await read.execute("call-1", {"path": "src/main.py"})
```

路徑安全集中在 `ensure_workspace_path()`。所有檔案工具共用同一個邊界，避免每個工具各自實作一份容易不一致的檢查。

## 錯誤與測試

不存在的檔案會產生錯誤；Workspace 外的路徑會產生 `WorkspaceViolation`。這兩種錯誤都應該有測試，因為安全功能不能只靠人工操作驗證。

## 練習

1. 加入最大讀取位元組數，防止一次載入巨大檔案。
2. 對二進位檔案回傳清楚錯誤。
3. 設計讀取行號範圍的選配參數。

## 本章驗收

- 能讀取 Workspace 內文字檔。
- `../outside.txt` 會被拒絕。
- 工具不會自行執行檔案內容。
