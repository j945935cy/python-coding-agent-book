# 12. Bash：執行受限系統指令

## 本章目標

理解 Bash 是本書副作用最廣的工具，並用限制模式示範先縮小能力、再逐項開放。讀完本章後，你應能：

- 固定子行程工作目錄為 Workspace；
- 拒絕目前正規表示式涵蓋的組合符號與未知命令；
- 收集 return code、stdout、stderr；
- 在逾時後殺掉並等待子行程；
- 說明限制模式為何仍不是完整沙箱。

## 威脅模型

模型輸出的命令是不可信資料。即使 system prompt 要求「只執行測試」，命令仍可能刪檔、讀取秘密、連線或建立背景行程。控制必須在程式碼與作業系統層執行。

本專案先限制：

- 固定 `cwd`；
- 只允許 `cat`、`echo`、`ls`、`pwd`、`python3`、`sleep`；
- 拒絕 `;`、`&`、`|`、`<`、`>`、反引號與 NUL；
- 使用逾時；
- 回傳完整結構化結果。

## 核心實作

```python
import asyncio
import re
from pathlib import Path


_ALLOWED_COMMANDS = {"cat", "echo", "ls", "pwd", "python3", "sleep"}
_SHELL_OPERATORS = re.compile(r"[;&|<>`]|\x00")


class BashTool:
    name = "bash"
    description = "Run a restricted command inside the workspace."

    def __init__(self, workspace: Path, timeout_seconds: float = 10.0):
        self.workspace = workspace.resolve()
        self.timeout_seconds = timeout_seconds

    async def execute(self, tool_call_id: str, arguments: dict) -> dict:
        command = arguments["command"]
        if not isinstance(command, str) or not command.strip():
            raise ValueError("command must be a non-empty string")
        if _SHELL_OPERATORS.search(command):
            raise PermissionError(
                "Shell composition is disabled in restricted mode"
            )
        executable = command.strip().split(maxsplit=1)[0]
        if executable not in _ALLOWED_COMMANDS:
            raise PermissionError(f"Command is not allowed: {executable}")

        process = await asyncio.create_subprocess_shell(
            command,
            cwd=self.workspace,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), self.timeout_seconds
            )
        except asyncio.TimeoutError as exc:
            process.kill()
            await process.wait()
            raise TimeoutError(
                f"Command timed out after {self.timeout_seconds}s"
            ) from exc
        return {
            "returncode": process.returncode,
            "stdout": stdout.decode(errors="replace"),
            "stderr": stderr.decode(errors="replace"),
        }
```

## 成功、拒絕與逾時

```python
import asyncio
import tempfile
from pathlib import Path

from mini_agent.tools.bash_tool import BashTool


async def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        tool = BashTool(Path(directory), timeout_seconds=1)
        result = await tool.execute("bash-1", {"command": "pwd"})
        print(result["returncode"])
        print(Path(result["stdout"].strip()).resolve() == Path(directory).resolve())


asyncio.run(main())
```

預期輸出：

```text
0
True
```

負向案例：

| 命令 | 結果 | 原因 |
|---|---|---|
| `pwd; rm -rf .` | `PermissionError` | 含分號 |
| `pwd && echo ok` | `PermissionError` | 含 `&` |
| `ls | cat` | `PermissionError` | 含管線 |
| `pytest -q` | `PermissionError` | 不在 allowlist |
| 空字串 | `ValueError` | 無可執行命令 |
| `sleep 1` 配 0.01 秒 | `TimeoutError` | 子行程被 kill 並 wait |

## 為什麼仍不是沙箱

目前仍呼叫 `create_subprocess_shell()`。雖然先攔截常見組合符號，參數本身仍可能改變允許命令的行為；`python3` 尤其能執行任意 Python。Workspace `cwd` 也不會阻止程式讀取絕對路徑或使用網路。

目前已實測可穿過限制的案例包括：

| 輸入 | 現行結果 | 風險 |
|---|---|---|
| `echo $(pwd)` | 允許 | `$()` 指令替換沒有被正規表示式攔截 |
| 命令中加入換行 | 可能執行第二個 shell 指令 | 換行不在封鎖字元集合 |
| `cat /etc/hostname` | 允許 | 固定 `cwd` 不限制絕對路徑讀取 |
| `python3 -c ...` | 允許 | 可執行任意 Python、讀寫 Workspace 外或連網 |
| 非零結束碼 | 正常回傳 dict | 不會自動轉成例外，呼叫端必須檢查 `returncode` |

正規表示式也可能誤拒絕引號內原本只想當資料的 `;` 或 `>`。因此這套機制同時存在漏擋與誤擋，不能視為 shell parser。

正式產品至少要考慮：

- 改用 `create_subprocess_exec()` 與結構化 argv；
- 每個 executable 另設參數規則；
- 容器、低權限使用者、唯讀掛載與網路限制；
- 使用者核准與命令預覽；
- 輸出大小限制與行程樹清理；
- Windows、Linux、macOS 的平台差異。

因此本章只能宣稱「受限教學模式」，不能宣稱「安全執行任意 Bash」。

## 驗證命令

```bash
uv run --extra test pytest tests/test_bash_tool.py -q
```

測試實際驗證 Workspace `pwd`、分號、實際 NUL 與逾時。它們沒有證明 `$()`、換行、絕對路徑、`python3 -c` 或完整行程樹已被隔離。

## 檢查清單

- [ ] 命令是非空字串。
- [ ] executable 必須在 allowlist。
- [ ] 已列出的封鎖字元在啟動行程前拒絕，但不誤稱為完整 shell composition 防禦。
- [ ] `cwd` 固定為 Workspace。
- [ ] stdout、stderr、return code 都保留。
- [ ] 逾時後目前的 shell 行程會 kill 並 wait；衍生行程樹仍是已知限制。
- [ ] 檔案不把限制模式誤稱為完整沙箱。

## 練習

1. **基礎：未知命令。** 新增測試確認 `pytest -q` 目前被拒絕。
2. **進階：結構化 argv。** 以 `create_subprocess_exec()` 取代 shell 字串，先為含空格參數寫測試。
3. **挑戰：命令政策。** 為 `python3` 設計可允許的參數集合，並說明為何單靠 executable allowlist 不夠。

## 本章小結

Bash 的安全性來自能力限制、行程生命週期與作業系統隔離，不來自模型承諾。這個最小工具示範 fail-closed 與逾時清理，但仍保留 `shell=True` 類型的廣泛風險，正式產品必須再加一層隔離。

## 本章驗收

- `pwd` 的實際路徑是 Workspace。
- 組合符號與未知 executable 在啟動前被拒絕。
- 能說明目前逾時會停止並等待 shell 行程，但未保證清除所有衍生行程。
- 能列出目前限制模式至少三項不足。
