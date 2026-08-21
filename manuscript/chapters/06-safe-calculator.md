# 6. 第一個工具：安全計算機

## 本章目標

完成第一個低風險工具，並建立後續所有工具都會沿用的思考方式。讀完本章後，你應能：

- 說明為什麼不能把模型產生的算式直接交給 `eval()`；
- 看懂工具名稱、說明、輸入參數與非同步 `execute()` 的基本契約；
- 實作只允許固定操作的 `CalculatorTool`；
- 分辨未知操作與數值型態錯誤；
- 用自動化測試驗收成功與失敗路徑。

本章使用 Python 3.11 以上版本。範例不需要模型 API Key，也不需要網路服務。

## 從最小副作用開始

Coding Agent 最終會讀寫檔案、執行測試，甚至啟動子行程。若第一個工具就碰觸這些副作用，當結果錯誤時，很難判斷問題究竟在 Agent Loop、路徑邊界、Shell，還是工具協定。

計算機只有輸入與回傳值，不修改 Workspace，因此適合當第一個垂直切片。我們可以先回答四個問題：

| 問題 | Calculator 的答案 | 後續章節的抽象 |
|---|---|---|
| 如何識別工具？ | `name = "calculator"` | Registry 以名稱查找工具 |
| 如何向模型描述能力？ | `description` | ModelClient 取得工具描述 |
| 如何執行？ | `execute(id, arguments)` | 所有工具共用 `AgentTool` 協定 |
| 如何失敗？ | 拒絕未知操作與錯誤型態 | Validation、Registry 與工具各守一層 |

先讓一個具體工具可執行、可失敗、可測試，再抽出共通介面，會比一開始設計龐大的工具框架更容易驗證。

## 失敗情境：把模型輸出當成程式碼

最短的計算機看起來可能是這樣：

```python
# 錯誤示範：不要執行
result = eval(model_generated_expression)
```

問題不只在算錯。`eval()` 接受的是 Python 運算式，不是單純數學資料。只要輸入來源不可信，攻擊者或失控模型就可能讀取程式可接觸的物件、消耗大量資源，或組合出原本沒有打算開放的行為。

提示詞中的「只能做數學運算」不是安全邊界。真正的邊界必須由程式碼強制：列出允許的操作，其他一律拒絕。

## 用固定操作表建立允許清單

本專案只開放加、減、乘三種操作：

```python
_operations = {
    "add": operator.add,
    "subtract": operator.sub,
    "multiply": operator.mul,
}
```

這是允許清單，不是封鎖清單。程式不必猜測哪些危險字串需要禁止；只有表內名稱可以對應到可執行函式。

完整工具如下，對應 `src/mini_agent/tools/calculator.py`：

```python
from __future__ import annotations

import operator
from typing import Any


class CalculatorTool:
    name = "calculator"
    description = "Perform one basic arithmetic operation without evaluating arbitrary Python."
    _operations = {
        "add": operator.add,
        "subtract": operator.sub,
        "multiply": operator.mul,
    }

    async def execute(
        self,
        tool_call_id: str,
        arguments: dict[str, Any],
    ) -> dict[str, int | float]:
        operation = arguments.get("operation")
        if operation not in self._operations:
            raise ValueError(f"Unsupported operation: {operation}")

        left = arguments.get("left")
        right = arguments.get("right")
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise TypeError("left and right must be numbers")

        return {"result": self._operations[operation](left, right)}
```

`tool_call_id` 在這個工具內尚未使用，但仍保留在簽章中。所有工具採相同呼叫形式後，Registry 與 Agent Loop 才不需要針對 Calculator 寫特例。稍後產生 `ToolResultMessage` 時，Loop 會使用相同 ID 配對工具請求與結果。

## 一次成功呼叫

以下程式可直接執行：

```python
import asyncio

from mini_agent.tools.calculator import CalculatorTool


async def main() -> None:
    tool = CalculatorTool()
    result = await tool.execute(
        "call-1",
        {"operation": "multiply", "left": 6, "right": 7},
    )
    print(result)


asyncio.run(main())
```

預期輸出：

```text
{'result': 42}
```

回傳物件保留 `result` 欄位，而不是只回傳數字。結構化結果比較容易加入單位、警告或其他 metadata，也方便測試精確比對。

## 失敗案例一：未知操作

若模型要求尚未開放的 `divide`：

```python
async def request_unsupported_operation(tool: CalculatorTool) -> None:
    await tool.execute(
        "call-2",
        {"operation": "divide", "left": 8, "right": 2},
    )
```

工具會拋出：

```text
ValueError: Unsupported operation: divide
```

未知操作必須失敗，而不是猜測模型想做什麼。若要支援除法，應明確把它加入允許清單，並另外定義除以零的行為與測試。

## 失敗案例二：數值型態錯誤

模型產生的 JSON object 不代表每個欄位型態都正確。例如：

```python
async def request_with_wrong_type(tool: CalculatorTool) -> None:
    await tool.execute(
        "call-3",
        {"operation": "add", "left": "2", "right": 3},
    )
```

目前工具不會偷偷把字串轉成數字，而是拋出：

```text
TypeError: left and right must be numbers
```

自動轉型看似方便，卻會增加模糊情況，例如空字串、千分位、不同小數點格式或科學記號。第一版工具選擇明確拒絕，讓模型在下一回合修正參數。

### Python 的布林值陷阱

Python 中 `bool` 是 `int` 的子類別，因此目前的 `isinstance(True, (int, float))` 會得到 `True`。也就是說，這個最小版本仍會把布林值當成 `1` 或 `0`。這是已知限制，不應誤寫成已被拒絕。

若產品契約要求布林值不是數字，可以在型態判斷中再明確排除 `bool`，並先加入失敗測試。章末練習會要求你完成這個變更。

## 驗證成功與失敗路徑

既有測試位於 `tests/test_calculator.py`。成功案例驗證加法結果，失敗案例驗證未知操作不會被執行：

```python
import pytest

from mini_agent.tools.calculator import CalculatorTool


@pytest.mark.asyncio
async def test_calculator_supports_basic_arithmetic_without_eval():
    result = await CalculatorTool().execute(
        "1",
        {"operation": "add", "left": 2, "right": 3},
    )
    assert result == {"result": 5}


@pytest.mark.asyncio
async def test_calculator_rejects_unknown_operation():
    with pytest.raises(ValueError, match="Unsupported operation"):
        await CalculatorTool().execute(
            "1",
            {"operation": "divide", "left": 2, "right": 3},
        )
```

在專案根目錄執行：

```bash
uv run --extra test pytest tests/test_calculator.py -q
```

時間不是驗收條件；應以命令結束碼為 `0`，且測試全部通過為準。

## 錯誤應由哪一層處理

Calculator 只知道自己的業務規則：允許哪些 operation，以及 `left`、`right` 是否可計算。它不應負責：

- 判斷工具名稱是否已註冊；
- 檢查 `ToolCall.id` 是否為空；
- 決定使用者是否允許這次操作；
- 把例外轉成對話歷史中的錯誤訊息。

這些責任會分別交給 Registry、Validation、Safety Hook 與 Agent Loop。每一層只做自己能一致判斷的工作，錯誤才容易定位。

## 檢查清單

- [ ] 工具沒有使用 `eval()` 或 `exec()`。
- [ ] 可執行操作來自明確允許清單。
- [ ] 未知 operation 會停止並回報錯誤。
- [ ] 非數值的 `left` 或 `right` 不會被偷偷轉型。
- [ ] 成功結果採穩定、可測試的結構。
- [ ] 成功與失敗路徑都有自動化測試。
- [ ] 工具本身不承擔 Registry、Safety Hook 或訊息轉換責任。

## 練習

1. **基礎：補數值型態測試。** 先新增一個測試，傳入 `left="2"`，確認它以 `TypeError` 失敗；再執行 Calculator 測試檔。
2. **進階：拒絕布林值。** 先寫一個會失敗的測試，要求 `left=True` 被拒絕；確認測試確實因現有行為而失敗後，再修改型態判斷使測試通過。
3. **挑戰：加入安全除法。** 加入 `divide`，定義除以零時的例外與訊息。至少測試正常除法、整數結果、小數結果及除以零，而且仍不得使用 `eval()`。

## 本章小結

安全工具的起點不是更聰明地解析模型文字，而是縮小可執行範圍。Calculator 以固定操作表取代 `eval()`，用明確型態錯誤拒絕模糊輸入，並以測試記錄成功與失敗契約。下一章會把這個具體工具放進通用 `AgentTool` 協定與 `ToolRegistry`，讓 Agent Loop 不必知道每個工具的類別。

## 本章驗收

- 能從專案根目錄執行 Calculator 測試，命令以結束碼 `0` 完成。
- 能說明 `eval()` 的風險，以及允許清單如何縮小執行範圍。
- 能實際觸發未知操作與錯誤數值型態兩種失敗。
- 能指出布林值仍會被目前版本接受，且不把它誤報為已修正。
- 能說明 Calculator、Registry、Validation 與 Agent Loop 各自負責哪一類錯誤。
