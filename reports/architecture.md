# Python 架構草圖

## 分層

```text
CLI／main.py
    ↓
Agent Runtime／agent_loop.py
    ├── Context／context.py
    ├── Messages／messages.py
    ├── Events／events.py
    ├── ModelClient／model_client.py
    ├── Tool Registry／tools/base.py
    ├── Validation／validation.py
    └── Safety Hooks／safety.py
              ↓
       Read / Write / Edit / Bash
```

## 核心責任

| 模組 | 責任 |
|---|---|
| `messages.py` | 定義 User、Assistant、ToolResult、ToolCall 與序列化。 |
| `context.py` | 管理 system prompt、訊息、工具清單及模型邊界轉換。 |
| `config.py` | 最大回合數、逾時、Workspace、工具執行模式與模型設定。 |
| `events.py` | 定義 agent、turn、message、tool execution 的事件型別。 |
| `model_client.py` | 定義 `ModelClient` Protocol 與 `FakeModel`；不綁定供應商。 |
| `validation.py` | 工具名稱、必要欄位、型態、額外欄位與截斷狀態驗證。 |
| `safety.py` | Workspace 路徑檢查、危險 Bash 攔截、before/after Hook。 |
| `tools/base.py` | `AgentTool` Protocol 與工具註冊表。 |
| `tools/read_tool.py` | Workspace 內安全讀取。 |
| `tools/write_tool.py` | Workspace 內建立／覆寫。 |
| `tools/edit_tool.py` | 唯一匹配的精確修改。 |
| `tools/bash_tool.py` | 限制模式、工作目錄、逾時、取消與命令攔截。 |

## 對應設計

| Pi 研究概念 | 本書 Python 設計 | 分類 |
|---|---|---|
| AgentMessage 與 LLM Message 分離 | `AgentMessage`、`transform_context()`、`convert_to_llm()` | Python 重新設計，受原始概念啟發 |
| 低階 agent loop | `run_agent_loop()` | 教學簡化 |
| 狀態化 `Agent` 包裝 | 第 17–18 章的 `AgentRuntime` | 本書自行擴充的教學模型 |
| `beforeToolCall`／`afterToolCall` | `before_tool_call()`／`after_tool_call()` | 概念對應，介面重新設計 |
| EventStream | `AsyncIterator[AgentEvent]` | Python 慣例改寫 |
| 平行工具 | `asyncio.gather()` 並依原呼叫順序收集 | Python 實作選擇 |
| AbortSignal | `asyncio.Event`／task cancellation | Python 重新設計 |
| CLI session runtime | `main.py` 薄層入口 | 教學簡化 |

## Protocol 草圖

```python
from collections.abc import AsyncIterator
from typing import Protocol

class ModelClient(Protocol):
    async def stream(self, context: "AgentContext") -> AsyncIterator["ModelEvent"]:
        ...

class AgentTool(Protocol):
    name: str
    description: str

    async def execute(
        self,
        tool_call_id: str,
        arguments: dict,
    ) -> "ToolResult":
        ...
```

## 最小迴圈邊界

- 先將使用者訊息加入 Context。
- 呼叫模型並收集完整 Assistant 訊息。
- 若模型輸出被截斷，所有工具呼叫一律轉為錯誤結果，不執行。
- 若沒有工具呼叫，正常結束。
- 若有工具呼叫，逐一或平行驗證、執行並加入 ToolResult。
- 若達到最大回合數，產生明確錯誤並結束。
