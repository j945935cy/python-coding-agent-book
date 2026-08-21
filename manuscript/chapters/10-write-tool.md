# 10. Write：建立與覆寫檔案

## 本章目標

讓 Agent 在 Workspace 內建立或覆寫 UTF-8 文字檔，並把副作用、回傳證據與安全政策分開。讀完本章後，你應能：

- 在寫入前驗證 Workspace 路徑；
- 建立不存在的父目錄；
- 說明覆寫語意及其風險；
- 使用 bytes 數與再次讀回驗證結果；
- 分辨工具能力與是否核准本次寫入。

## 寫入順序不能顛倒

Write 的正確順序是：

```text
驗證相對路徑
→ 解析 Workspace 內目標
→ 建立父目錄
→ 以 UTF-8 寫入
→ 回傳路徑與 bytes
→ Read／測試驗證
```

若先建立目錄或開啟檔案，再檢查路徑，副作用可能已經發生。Safety Hook 也必須在 Agent Loop 呼叫工具之前執行。

## 完整實作

```python
from pathlib import Path

from mini_agent.safety import ensure_workspace_path


class WriteTool:
    name = "write"
    description = "Write a UTF-8 text file inside the workspace."

    def __init__(self, workspace: Path):
        self.workspace = workspace

    async def execute(self, tool_call_id: str, arguments: dict) -> dict:
        path = ensure_workspace_path(self.workspace, arguments["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        content = arguments["content"]
        path.write_text(content, encoding="utf-8")
        return {
            "path": arguments["path"],
            "bytes": len(content.encode("utf-8")),
        }
```

`bytes` 使用 UTF-8 編碼後的長度，不等於 Python 字元數。中文字通常佔多個 bytes；報告 bytes 比只回報字元數更接近實際寫入量。

## 建立檔案並讀回

```python
import asyncio
import tempfile
from pathlib import Path

from mini_agent.tools.file_tools import ReadTool, WriteTool


async def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        workspace = Path(directory)
        write = WriteTool(workspace)
        read = ReadTool(workspace)
        result = await write.execute(
            "write-1",
            {"path": "src/hello.py", "content": "print('哈囉')\n"},
        )
        content = await read.execute("read-1", {"path": "src/hello.py"})
        print(result)
        print(content, end="")


asyncio.run(main())
```

預期輸出中的 bytes 由 UTF-8 實際計算；不要把固定數值寫成跨內容的通則。驗收重點是回傳 bytes 與 `len(content.encode("utf-8"))` 相同，且 Read 得到原內容。

## 覆寫不是隱含小事

目前 API 使用 `Path.write_text()`，目標存在時會完整覆寫。這適合教學原型與明確重建的檔案，但正式產品通常還需要：

- `overwrite=False` 的安全預設；
- 寫入前顯示 diff 或要求核准；
- Git 狀態檢查或備份；
- 原子寫入，避免中途失敗留下半個檔案；
- 寫入大小上限。

工具「可以覆寫」不代表政策「應自動核准覆寫」。前者是能力，後者由 Safety Hook 或呼叫端決定。

## 常見失敗

| 失敗 | 目前行為 | 改進方向 |
|---|---|---|
| 路徑越界 | `WorkspaceViolation`，不建立父目錄 | 保持 fail-closed |
| `content` 缺失 | `KeyError` | 加入具體欄位驗證 |
| `content` 非字串 | `TypeError` | 回報清楚的輸入錯誤 |
| 目標已存在 | 直接覆寫 | 正式版加入核准或條件寫入 |
| 磁碟／權限失敗 | 保留原始 I/O 例外 | Agent Loop 轉成錯誤結果 |

## 驗證命令

```bash
uv run --extra test pytest tests/test_tools.py tests/test_safety.py -q
```

另外，任何教學範例都應在暫存 Workspace 執行，避免測試修改讀者的真實專案。

## 檢查清單

- [ ] 路徑檢查在所有副作用之前。
- [ ] 父目錄只建立在 Workspace 內。
- [ ] 明確使用 UTF-8。
- [ ] 回傳相對路徑與 UTF-8 bytes。
- [ ] 寫入後能以 Read 或測試讀回。
- [ ] 檔案明確說明目前會覆寫既有檔案。

## 練習

1. **基礎：bytes 測試。** 使用中文內容，驗證 bytes 與 UTF-8 編碼後長度一致。
2. **進階：條件覆寫。** 先寫測試，再加入 `overwrite=False`；既有檔案不得被改動。
3. **挑戰：原子寫入。** 先寫暫存檔，再以原子替換完成提交，並設計失敗清理測試。

## 本章小結

Write 的主要風險是副作用。路徑、內容與政策必須在寫入前確定；寫入後則以結構化結果與 Read 驗證，不能只相信工具呼叫沒有拋出例外。

## 本章驗收

- 能建立巢狀父目錄並寫入 UTF-8 內容。
- Workspace 外路徑不會建立任何檔案或目錄。
- 能說明 bytes 與字元數的差異。
- 能指出目前直接覆寫的限制。
