# 進階產品化範例

本附錄把第 18 章列出的產品化缺口轉成八個可執行原型。它們全部位於 `examples/advanced/`，使用標準函式庫，預設不連網、不需要 API Key，也不修改穩定的 `run_agent_loop()`。

這些範例的定位是「可測試的下一步」，不是宣稱核心已經具備所有產品能力。每個原型都有獨立測試；需要整合進正式套件時，仍應先定義 API、版本與遷移策略。

## 執行全部進階測試

```bash
uv run --frozen --extra test pytest \
  tests/test_advanced_adapter_cli.py \
  tests/test_advanced_registry_sandbox.py \
  tests/test_advanced_stream_context.py \
  tests/test_advanced_checkpoint_transaction.py \
  -q
```

目前共 56 項進階測試；連同既有測試，全套為 98 passed。

---

## 無金鑰 Model Adapter

檔案：

```text
examples/advanced/recording_adapter.py
tests/test_advanced_adapter_cli.py
```

`RecordingAdapter` 透過 `FakeTransport` 接收 provider-like fixture，把回應轉成核心 `AssistantMessage` 與 `ToolCall`。它不匯入供應商 SDK，也不需要 API Key。

涵蓋的邊界：

- 一般文字回應；
- 一個或多個工具呼叫；
- `finish_reason=length` 映射；
- arguments JSON 解析；
- 缺失、空白或重複 ToolCall ID；
- 畸形 provider envelope；
- 可重試 transport 錯誤；
- 有上限的 retry exhaustion。

執行：

```bash
uv run python examples/advanced/recording_adapter.py
```

預期輸出：

```text
assistant> Offline adapter response.
requests=1
```

這個範例證明 Adapter 可以在不修改核心 Loop 的情況下轉換供應商格式。它沒有發出真實 HTTP，也沒有處理特定供應商的完整 usage、streaming 或認證流程。

---

## 互動式 CLI

檔案：

```text
examples/advanced/interactive_cli.py
tests/test_advanced_adapter_cli.py
```

`InteractiveCLI` 以注入的 input／output 函式測試，不需要真的操控終端機。預設模型仍是離線 `FakeModel`。

支援命令：

```text
/help
/tools
/history
/cancel
/quit
```

執行：

```bash
uv run python examples/advanced/interactive_cli.py
```

確定性 smoke output：

```text
Mini Agent CLI (offline). Type /help for commands.
you> Bye.
```

CLI 不直接偷看 Loop 區域變數；它使用公開 history、工具清單與 CancellationToken。真實互動模式若換成 Provider Adapter，仍應保留 FakeModel 測試路徑。

---

## 完整 Registry 與授權政策

檔案：

```text
examples/advanced/full_registry.py
tests/test_advanced_registry_sandbox.py
```

此範例同時註冊：

```text
Calculator
Read
Write
Edit
Bash
```

授權與註冊分開：

| 工具 | 預設政策 |
|---|---|
| calculator | allow |
| read | allow |
| write | require_approval |
| edit | require_approval |
| bash | deny |
| unknown | deny |

執行：

```bash
uv run python examples/advanced/full_registry.py
```

預期輸出：

```text
registered=bash,calculator,edit,read,write
bash=deny
calculator=allow
edit=require_approval
read=allow
write=require_approval
```

重點是 Registry capability 不等於使用者 authorization。即使 Bash 已註冊，政策仍可預設拒絕。

---

## Structured Command Runner

檔案：

```text
examples/advanced/sandbox_runner.py
tests/test_advanced_registry_sandbox.py
```

名稱中的 runner 不是 OS sandbox。`StructuredCommandRunner` 使用 `asyncio.create_subprocess_exec()` 與結構化 argv，不經 shell；目前只允許非常小的命令與參數集合。

控制內容：

- 拒絕空 argv、非字串項目與 NUL；
- 拒絕 shell operator、換行及命令替換字串；
- 拒絕 Python interpreter；
- 拒絕絕對路徑與 Workspace 外路徑；
- 路徑解析包含 symlink containment；
- 逾時後 kill 並 await 目前子行程。

執行：

```bash
uv run python examples/advanced/sandbox_runner.py
```

預期輸出：

```text
structured argv
```

這比字串 shell 安全，但仍不是容器、權限隔離或完整 process-group sandbox。正式產品仍需要低權限使用者、檔案系統掛載、網路限制與資源上限。

---

## EventStream Condition／deque 原型

檔案：

```text
examples/advanced/event_stream.py
tests/test_advanced_stream_context.py
```

`EventStream` 是獨立原型，沒有替換目前核心的 list collector。它示範：

- 單一 `asyncio.Condition` 與內部 `deque`，維持有界事件容量；
- async iterator；
- 明確 end-of-stream sentinel；
- `BLOCK` backpressure；
- `DROP_OLDEST` 策略；
- graceful close；
- consumer cancellation 與 blocked publisher 清理。
- 直接取消 blocked publisher 時清理內部等待，不讓事件在 closed stream 中殘留；
- publish／abort 共用單一 Condition 原子化生命週期，兩種排程交錯後都要求 deque buffer 為空、pending count 為 0。
- blocked close task 即使被直接取消，也會留下終止 sentinel；消費端讀完既有事件後不會永久等待。

執行：

```bash
uv run python examples/advanced/event_stream.py
```

預期輸出：

```text
events=0,1,2
dropped=0 closed=True
```

這個事件流傳送的是 `AgentEvent`，不是模型 token delta 的完整協定。若整合核心，還要定義事件版本、不可丟棄事件與慢消費端政策。

---

## Context 預算與壓縮

檔案：

```text
examples/advanced/context_budget.py
tests/test_advanced_stream_context.py
```

此範例提供純函式：

```text
measure_context()
compact_context()
```

預算依訊息數與字元數近似，不宣稱是精準 token 計算。壓縮時會：

- 保留最新 UserMessage；
- 將 Assistant ToolCall 與連續 ToolResult 視為不可拆群組；
- 保留最近副作用證據；
- 當 pinned content 本身超出預算時拋出 `PinnedContentExceedsBudget`；
- 不直接修改核心 Context。

執行：

```bash
uv run python examples/advanced/context_budget.py
```

預期輸出：

```text
before=6 messages
after=4 messages
latest_user_kept=True
```

正式整合仍需供應商 tokenizer、摘要模型、秘密遮罩與重播契約。

---

## SQLite Checkpoint 與冪等操作

檔案：

```text
examples/advanced/checkpoint_sqlite.py
tests/test_advanced_checkpoint_transaction.py
```

`CheckpointStore` 保存：

- schema version；
- run ID；
- operation ID；
- canonical payload hash；
- status；
- result。

相同 operation ID 與相同 payload 在重新開啟 SQLite 後回傳既有結果；同一 ID 搭配不同 payload 會拒絕。

執行：

```bash
uv run python examples/advanced/checkpoint_sqlite.py
```

預期輸出：

```text
result=checkpointed replay_equal=True calls=1
guarantee=completed-record replay; not exactly-once across crash windows
```

此範例沒有宣稱 exactly-once。若副作用已成功、但完成紀錄尚未提交，仍存在 crash window；真正外部服務應優先使用原生 idempotency key 或交易。

---

## 多檔交易與回滾

檔案：

```text
examples/advanced/multi_file_transaction.py
tests/test_advanced_checkpoint_transaction.py
```

流程：

```text
複製 Workspace 到 staging
→ 驗證所有相對路徑
→ 在 staging 套用寫入／刪除
→ 執行注入的 validator
→ 全部成功才 commit
→ 失敗則保留原 Workspace
```

驗證失敗時，原始 Workspace 必須 byte-identical。Commit 失敗會嘗試 rollback；若 rollback 也失敗，例外會保留 recovery backup 路徑，而不是假裝已恢復。

執行：

```bash
uv run python examples/advanced/multi_file_transaction.py
```

預期輸出：

```text
committed=true files=config.txt,notes.txt
version=2
```

這是單機檔案 staging 原型，不是跨資料庫、網路服務與多行程的分散式交易。

---

## 與 V10 的關係

V10 維持小型、確定性、FakeModel-only 的核心組裝，不直接納入以上八種產品化能力。這些進階範例各自建立測試邊界，讓讀者先理解契約，再決定是否整合核心。

建議順序：

```text
V10 核心整合
→ Recording Adapter
→ CLI／Registry Policy
→ EventStream／Context Budget
→ Checkpoint／Multi-file Transaction
→ Structured Runner／OS 隔離設計
```

完成這些原型後，仍不能跳過真實 Adapter 的供應商測試、容器隔離、秘密管理、Reader／EPUB 驗證與部署監控。
