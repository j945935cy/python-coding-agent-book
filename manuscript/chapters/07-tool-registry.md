# 7. 建立通用工具介面與工具註冊表

## 本章目標

把上一章的具體 Calculator 放進通用工具架構。讀完本章後，你應能：

- 使用 `Protocol` 描述 Agent Tool 的最小介面；
- 說明結構式子型別與類別繼承的差異；
- 註冊、查找與執行多個工具；
- 在註冊階段拒絕空名稱與重複名稱；
- 在分派階段拒絕未知工具；
- 說明為什麼 Agent Loop 不應匯入每一個具體工具類別。

本章延續第 6 章的 `CalculatorTool`，並以無副作用的 `PingTool` 示範第二個工具。

## 失敗情境：Agent Loop 寫滿工具名稱

若沒有通用介面，Loop 很容易逐漸長成這樣：

```python
# 錯誤示範：工具愈多，Loop 愈難維護
async def execute_with_branches(call):
    if call.name == "calculator":
        return await calculator.execute(call.id, call.arguments)
    if call.name == "read":
        return await read_tool.execute(call.id, call.arguments)
    if call.name == "write":
        return await write_tool.execute(call.id, call.arguments)
    raise ValueError("unknown tool")
```

這段程式把兩種責任混在一起：Loop 應負責控制回合，卻同時知道所有工具名稱與實例。每增加一個工具都要修改核心流程，也更容易在測試、正式環境或不同產品組合中漏掉分支。

我們要把呼叫方向固定為：

```text
Agent Loop → ToolRegistry → AgentTool
```

Loop 只把 ID、名稱與 arguments 交給 Registry。Registry 查找實例並執行；具體工具只處理自己的參數與業務行為。

## 用 Protocol 定義最小工具契約

`src/mini_agent/tools/base.py` 使用 `Protocol` 描述工具：

```python
from typing import Any, Protocol


class AgentTool(Protocol):
    name: str
    description: str

    async def execute(
        self,
        tool_call_id: str,
        arguments: dict[str, Any],
    ) -> Any:
        ...
```

這個協定只有三項要求：

| 成員 | 用途 |
|---|---|
| `name` | 工具呼叫與 Registry 查找使用的穩定識別名稱 |
| `description` | 向模型或使用者說明工具用途 |
| `execute()` | 以 call ID 與 arguments 執行非同步工作 |

`Protocol` 採結構式子型別。具體工具不必繼承 `AgentTool`；只要提供相同成員，型別檢查器就能把它視為符合協定。第 6 章的 `CalculatorTool` 沒有寫 `class CalculatorTool(AgentTool)`，仍可交給 Registry。

這項設計避免框架基底類別滲入每個工具，同時保留一致簽章。若未來某個工具需要自己的建構參數、內部狀態或額外輔助方法，也不必修改協定。

## 建立 Registry

Registry 內部使用名稱到工具實例的字典：

```python
from collections.abc import Iterable


class ToolRegistry:
    def __init__(self, tools: Iterable[AgentTool] = ()):
        self._tools: dict[str, AgentTool] = {}
        for tool in tools:
            self.register(tool)

    def register(self, tool: AgentTool) -> None:
        if not tool.name:
            raise ValueError("Tool name is required")
        if tool.name in self._tools:
            raise ValueError(f"Duplicate tool name: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> AgentTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {name}") from exc

    def names(self) -> set[str]:
        return set(self._tools)

    async def execute(
        self,
        tool_call_id: str,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        return await self.get(name).execute(tool_call_id, arguments)
```

`__init__()` 與 `register()` 共用同一條驗證路徑，因此建立時傳入的工具與稍後加入的工具會遵守相同規則。

## 註冊兩個不同工具

先建立一個最小 `PingTool`：

```python
from typing import Any


class PingTool:
    name = "ping"
    description = "Return a fixed health-check response."

    async def execute(
        self,
        tool_call_id: str,
        arguments: dict[str, Any],
    ) -> dict[str, str]:
        return {"reply": "pong", "tool_call_id": tool_call_id}
```

接著把它和 Calculator 放進同一個 Registry：

```python
import asyncio

from mini_agent.tools.base import ToolRegistry
from mini_agent.tools.calculator import CalculatorTool


async def main() -> None:
    registry = ToolRegistry([CalculatorTool()])
    registry.register(PingTool())

    print(sorted(registry.names()))
    print(await registry.execute("call-1", "ping", {}))
    print(
        await registry.execute(
            "call-2",
            "calculator",
            {"operation": "add", "left": 20, "right": 22},
        )
    )


asyncio.run(main())
```

預期輸出：

```text
['calculator', 'ping']
{'reply': 'pong', 'tool_call_id': 'call-1'}
{'result': 42}
```

範例對 `names()` 的 set 排序後才輸出，避免把 set 的顯示順序誤當成穩定契約。Registry 的責任是依名稱查找，不承諾註冊順序就是顯示順序。

## 註冊時拒絕重複名稱

名稱是工具呼叫的分派鍵。同一名稱若對應兩個實例，模型看到的描述與實際執行對象可能不一致。Registry 因此在註冊當下停止：

```python
registry = ToolRegistry([CalculatorTool()])
registry.register(CalculatorTool())
```

預期例外：

```text
ValueError: Duplicate tool name: calculator
```

這裡不採「後註冊覆蓋前註冊」。靜默覆蓋會讓組裝錯誤延後到執行階段才被發現，而且不同環境可能執行到不同實例。

空字串名稱也會被拒絕：

```text
ValueError: Tool name is required
```

名稱格式目前只檢查非空，尚未限制大小寫、字元集合或長度。若供應商 API 對名稱另有規則，應在 Adapter 或後續驗證層明確處理，不要假設這個最小 Registry 已涵蓋所有供應商限制。

## 分派時拒絕未知工具

直接查找未註冊名稱：

```python
registry = ToolRegistry([CalculatorTool()])
registry.get("delete_everything")
```

預期例外：

```text
KeyError: 'Unknown tool: delete_everything'
```

`execute()` 先呼叫 `get()`，因此未知工具不會落到任何具體工具。Agent Loop 還會在 Registry 之前呼叫 `validate_tool_call()`；下一章會說明為什麼仍保留這兩道檢查，以及兩者的錯誤語意有何不同。

## Registry 做什麼、不做什麼

| Registry 負責 | Registry 不負責 |
|---|---|
| 保存名稱與實例的對應 | 判斷 Calculator 的 `left` 是否為數字 |
| 拒絕空名稱與重複名稱 | 判斷 Read 的路徑是否離開 Workspace |
| 依名稱查找工具 | 決定這位使用者是否獲准執行工具 |
| 把 ID 與 arguments 原樣交給工具 | 把例外轉成 `ToolResultMessage` |
| 提供已知名稱集合 | 管理模型回合與最大回合數 |

Registry 不應逐一理解每個工具的 arguments。否則每新增一個工具，Registry 又會變成另一串 `if`。通用結構由 Validation 檢查；具體欄位由工具檢查；政策由 Safety Hook 判斷。

## 如何讓測試替換工具

由於 Loop 只依賴協定與 Registry，測試可以注入很小的工具，不需要真的讀檔或啟動 Shell：

```python
class AddTool:
    name = "add"
    description = "Add two integers."

    async def execute(self, tool_call_id: str, arguments: dict) -> dict:
        return {"sum": arguments["a"] + arguments["b"]}


registry = ToolRegistry([AddTool()])
```

這也是依賴注入的實際收益：測試與正式環境可以組裝不同工具集合，而 `run_agent_loop()` 不需要分支判斷目前是哪一種環境。

## 執行相關測試

Registry 已被 Calculator、檔案工具與 Agent Loop 測試間接使用。可執行：

```bash
uv run --extra test pytest \
  tests/test_calculator.py \
  tests/test_tool_registry.py \
  tests/test_tools.py \
  tests/test_agent_loop.py \
  -q
```

驗收以命令結束碼為 `0` 且測試全部通過為準，不以固定耗時為準。

## 檢查清單

- [ ] 每個工具都有非空且唯一的 `name`。
- [ ] 每個工具都有用途明確的 `description`。
- [ ] 每個工具提供相同形式的非同步 `execute()`。
- [ ] Agent Loop 只依賴 Registry，不匯入具體工具類別。
- [ ] 重複名稱在組裝階段立即失敗。
- [ ] 未知名稱不會分派到任何工具。
- [ ] Registry 不解讀各工具的業務欄位。
- [ ] 測試能注入無副作用的替身工具。

## 練習

1. **基礎：實作 PingTool。** 使用本章協定建立 `PingTool`，註冊後透過 `registry.execute()` 呼叫，確認 call ID 能出現在結果中。
2. **進階：補 Registry 邊界測試。** 分別測試空名稱、重複名稱與未知名稱。每個測試只驗證一種行為，並比對清楚的錯誤訊息。
3. **挑戰：產生模型工具描述。** 在不暴露 `_tools` 可變字典的前提下，設計一個回傳工具名稱與說明的方法。先定義穩定輸出順序與回傳資料形狀，再寫測試和實作。

## 本章小結

`AgentTool` Protocol 定義最小結構，`ToolRegistry` 管理實例與名稱分派。這讓 Agent Loop 不必知道 Calculator、Read 或 Bash 的類別，也讓測試能注入小型工具。Registry 只守住註冊與查找邊界；下一章會在工具真正執行前加入 ToolCall Validation 與 Safety Hook。

## 本章驗收

- 能把 Calculator 與 PingTool 同時註冊並分別執行。
- 能實際觸發空名稱、重複名稱與未知工具錯誤。
- 能說明 `Protocol` 為何不要求具體工具繼承基底類別。
- 能畫出 `Agent Loop → ToolRegistry → AgentTool` 的呼叫方向。
- 能指出 Registry、Validation 與具體工具各自檢查什麼。
