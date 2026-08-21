# 10. Write：建立與覆寫檔案

## 本章目標

讓 Agent 能在 Workspace 內建立檔案，並理解建立父目錄、編碼與覆寫都是明確的工具行為。

## 最小 Write 工具

`WriteTool` 接收相對路徑與文字內容，先通過 Workspace 邊界，再建立父目錄，最後以 UTF-8 寫入。

```python
await write.execute(
    "call-1",
    {"path": "src/hello.py", "content": "print('hello')\n"},
)
```

工具結果回傳相對路徑與 bytes 數，讓模型與使用者知道實際寫入了什麼。不要把完整檔案內容重複塞回 Context，否則大型檔案會迅速增加成本。

## 覆寫是高風險動作

第一版 API 明確允許覆寫，這讓範例簡單，但實際產品通常需要 approval、版本備份或 `if_exists` 選項。安全設計要把「可以做」與「應該直接做」分開。

## 練習

1. 新增 `overwrite=False` 選項。
2. 寫入前保留 `.bak` 備份。
3. 為空內容與非字串內容加入測試。

## 本章驗收

- 可建立不存在的父目錄。
- 檔案內容使用 UTF-8。
- Workspace 外路徑不能寫入。
