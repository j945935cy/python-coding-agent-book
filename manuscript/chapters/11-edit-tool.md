# 11. Edit：精確修改程式碼

## 本章目標

建立比整檔覆寫更保守的修改工具。讀完本章後，你應能：

- 把 `old` 視為可驗證前置條件；
- 只在唯一匹配時修改；
- 分辨零匹配、多匹配與 I/O 錯誤；
- 使用 Read → Edit → Read 的流程驗證修改；
- 說明 Edit 與 Write 的取捨。

## 為什麼不用整檔重寫

模型重建完整檔案時，容易遺漏未出現在 Context 的區段。Edit 只宣告局部替換：目前檔案必須包含一段唯一的舊文字，條件成立才換成新文字。

這不是模糊搜尋，也不是自動套用補丁。失敗是安全訊號：Context 可能過時，或指定範圍不夠精確。

## 完整實作

```python
from pathlib import Path

from mini_agent.safety import ensure_workspace_path


class EditTool:
    name = "edit"
    description = "Replace one unique text occurrence inside a workspace file."

    def __init__(self, workspace: Path):
        self.workspace = workspace

    async def execute(self, tool_call_id: str, arguments: dict) -> dict:
        path = ensure_workspace_path(self.workspace, arguments["path"])
        text = path.read_text(encoding="utf-8")
        old = arguments["old"]
        new = arguments["new"]
        count = text.count(old)
        if count != 1:
            raise ValueError(f"Expected exactly one match, found {count}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        return {"path": arguments["path"], "replacements": 1}
```

修改前先讀取全文並計數。只有 `count == 1` 才寫回，因此零匹配與多匹配都不會改動檔案。

## 可執行狀態轉換

```python
import asyncio
import tempfile
from pathlib import Path

from mini_agent.tools.file_tools import EditTool, ReadTool, WriteTool


async def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        workspace = Path(directory)
        write = WriteTool(workspace)
        edit = EditTool(workspace)
        read = ReadTool(workspace)
        await write.execute(
            "write-1",
            {"path": "app.py", "content": "print('draft')\n"},
        )
        result = await edit.execute(
            "edit-1",
            {"path": "app.py", "old": "draft", "new": "ready"},
        )
        content = await read.execute("read-1", {"path": "app.py"})
        print(result)
        print(content, end="")


asyncio.run(main())
```

預期輸出：

```text
{'path': 'app.py', 'replacements': 1}
print('ready')
```

## 匹配數就是決策

| 匹配數 | 意義 | 正確行為 |
|---:|---|---|
| 0 | Context 過時、路徑錯誤或原文已改變 | 停止，重新 Read |
| 1 | 修改位置明確 | 替換一次並回報證據 |
| 2 以上 | `old` 不夠精確 | 停止，增加周邊內容 |

失敗後的恢復順序是：

```text
Read 最新內容
→ 重新選擇更精確的 old/new
→ 再次 Edit
→ Read 驗證
→ 執行測試
```

工具不應自動退回模糊比對，否則「可恢復失敗」會變成「靜默改錯位置」。

## 重要限制

- 讀取到寫回之間沒有檔案鎖，其他行程可能同時修改檔案；
- 多檔修改沒有交易或回滾；
- 空字串 `old` 通常會產生多個匹配而被拒絕；但空檔案的 `"".count("") == 1`，目前反而會在開頭插入 `new` 並回報成功。這是必須揭露並以測試修正的邊界漏洞；
- 寫回不是原子操作；
- 工具只處理文字，不理解 AST 或語法。

這些限制不否定最小工具的價值，但不能把它宣稱為完整 patch engine。

## 驗證命令

```bash
uv run --extra test pytest tests/test_tools.py -q
```

目前整合測試驗證 Write → Edit，並確認結果與實際檔案一致。正式擴充時應補零匹配、多匹配與檔案未改動測試。

## 檢查清單

- [ ] Workspace 邊界在讀檔前檢查。
- [ ] 只有唯一匹配才寫回。
- [ ] 失敗時原檔保持不變。
- [ ] 回傳 `replacements: 1`。
- [ ] 修改後以 Read 與測試驗證。
- [ ] 不宣稱支援模糊比對、交易或 AST 編輯。

## 練習

1. **基礎：負向測試。** 分別測試零匹配與兩次匹配，並確認檔案內容未變。
2. **進階：拒絕空 old。** 先寫失敗測試，再回傳清楚錯誤。
3. **挑戰：多檔交易。** 設計先驗證全部前置條件、再一次提交的策略；說明失敗時如何回滾。

## 本章小結

Edit 把模型的修改意圖轉成可驗證前置條件。它寧可因 Context 過時而停止，也不猜測修改位置。對 Coding Agent 而言，可觀察失敗比靜默破壞安全。

## 本章驗收

- 唯一匹配才修改，零或多匹配都不改檔。
- 能完成 Write → Edit → Read 的驗證閉環。
- 能說明重新 Read 是恢復流程的一部分。
- 能列出競態、原子性與多檔交易限制。
