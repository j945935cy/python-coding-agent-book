# V0～V10 版本能力對照

| 版本 | 範例檔案 | 新增能力 | 主要安全邊界 | 驗證輸出 |
|---|---|---|---|---|
| V0 | `examples/v00_chatbot_baseline.py` | 單次模型回應 | 不執行工具 | `這只是一次模型回應。` |
| V1 | `examples/v01_fake_model_loop.py` | FakeModel 與 Calculator Loop | 固定操作表，不用 `eval()` | `計算結果是 5。` |
| V2 | `examples/v02_workspace_tools.py` | Write、Edit、Read | TemporaryDirectory 與 Workspace 路徑 | `print('hello, agent')` |
| V3 | `examples/v03_agent_file_loop.py` | 模型驅動檔案工具 | Registry、工具參數與 Workspace | `檔案已建立、修改並讀回。` |
| V4 | `examples/v04_events_parallel_cancel.py` | 事件與平行執行基礎 | 工具逾時、事件收尾 | `events=tool_start,tool_end` |
| V5 | `examples/v05_error_recovery.py` | 錯誤回傳模型、最大回合數 | 工具例外轉成錯誤結果 | `max_turns_guard=True` |
| V6 | `examples/v06_event_consumer.py` | CLI 事件消費端 | 依事件契約觀測，不讀 Loop 內部狀態 | `tool_start:calculator` |
| V7 | `examples/v07_parallel_order.py` | 平行工具與穩定結果順序 | 僅平行互不相依工作 | `results=slow,fast` |
| V8 | `examples/v08_cooperative_cancel.py` | 合作式取消 | 工具開始前檢查 Token | `cancelled=operator stop` |
| V9 | `examples/v09_safety_policy.py` | Safety Hook 拒絕工具 | 預設拒絕並回傳可觀察錯誤 | `denied=True` |
| V10 | `examples/v10_complete_agent.py` | Workspace、事件、取消、安全政策整合 | allowlist、Workspace、逾時與事件 | `完整 Agent 已完成。` |

## 建議閱讀方式

1. 先比較 V0 與 V1，確認「模型回答」和「模型決定工具後繼續推理」的差別。
2. V2 先獨立操作工具，V3 再交給 Agent Loop，避免同時學兩個抽象。
3. V4～V7 聚焦可觀察性、錯誤與非同步控制。
4. V8～V10 才加入取消、權限與完整整合。

## 自動驗證

```bash
uv run python scripts/verify_examples.py .
```

驗證器會逐一啟動 11 個版本，檢查 return code、逾時與預期輸出。
