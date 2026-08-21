# 12. Bash：執行系統指令

## 本章目標

理解 Bash 是風險最高的工具，並以限制模式示範「先限制能力，再逐步增加權限」。

## 目前限制模式

本專案的 `BashTool`：

- 固定工作目錄為 Workspace
- 只允許有限命令名稱
- 拒絕 `;`、`&&`、管線、重新導向與反引號
- 使用逾時中止子行程
- 回傳 return code、stdout、stderr

```python
async def demo(bash):
    result = await bash.execute("call-1", {"command": "pwd"})
    return result
```

這不是完整的沙箱，也不是宣稱 Bash 已經安全。它是教學用的最小風險邊界，提醒讀者：黑名單很容易漏掉，真正產品應考慮容器、作業系統權限與 approval。

## 為什麼不直接開放 shell

模型輸出不是可信的管理員指令。即使提示詞要求「只執行測試」，模型仍可能產生超出預期的命令。命令限制、工作區限制與逾時必須在程式碼層強制執行。

## 練習

1. 加入 `pytest` 但限制參數只能是測試路徑。
2. 讓 Bash 以 `create_subprocess_exec` 取代 shell 字串。
3. 設計需要使用者核准的命令類別。

## 本章驗收

- `pwd` 只能在 Workspace 執行。
- shell composition 會被拒絕。
- `sleep 1` 在短逾時設定下會停止。
