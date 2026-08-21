# 章節進度

18 個章節均已完成第一輪出版篇幅擴寫，並對應可執行原型、自動化驗收或明確的已知限制。這代表正文已從初稿骨架進入全書技術編輯階段；尚未代表文字編輯、練習解答或 EPUB 生產完成。

| 章節 | 主題 | 狀態 | 主要驗收／圖解 |
|---:|---|---|---|
| 1 | 聊天機器人與 Agent | 第一輪擴寫完成 | V0／V1、`agent-loop.svg` |
| 2 | 七個 Agent 模組 | 第一輪擴寫完成 | `seven-modules.svg` |
| 3 | 訊息資料模型 | 第一輪擴寫完成 | `tests/test_messages.py`、`message-pairing.svg` |
| 4 | Agent Context | 第一輪擴寫完成 | `context-lifecycle.svg` |
| 5 | Config、Hook、依賴注入 | 第一輪擴寫完成 | `dependency-injection.svg` |
| 6 | 安全 Calculator | 第一輪擴寫完成 | Calculator 負向測試 |
| 7 | AgentTool 與 Registry | 第一輪擴寫完成 | Registry 邊界測試 |
| 8 | ToolCall Validation | 第一輪擴寫完成 | `tool-contract-pipeline.svg` |
| 9 | Read Tool | 第一輪擴寫完成 | Workspace 測試、`workspace-boundary.svg` |
| 10 | Write Tool | 第一輪擴寫完成 | Write → Read 驗證 |
| 11 | Edit Tool | 第一輪擴寫完成 | 唯一匹配與狀態轉換 |
| 12 | Bash Tool | 第一輪擴寫完成 | `tests/test_bash_tool.py` |
| 13 | Agent Loop | 第一輪擴寫完成 | `agent-loop-state.svg` |
| 14 | 事件與串流 | 第一輪擴寫完成 | `event-lifecycle.svg` |
| 15 | 平行工具 | 第一輪擴寫完成 | `parallel-timeline.svg` |
| 16 | 取消、錯誤與恢復 | 第一輪擴寫完成 | `cancellation-recovery.svg` |
| 17 | 安全政策與 Context | 第一輪擴寫完成 | `safety-layers-context.svg` |
| 18 | 完整 Mini Coding Agent | 第一輪擴寫完成 | V10、`complete-agent-architecture.svg` |

## 第 9～18 章本批成果

- 第 9～12 章補齊 Workspace 邊界、Read／Write／Edit／Bash 完整實作、失敗分類、安全限制、檢查清單與分級練習。
- 第 13～16 章補齊 Agent Loop 停止條件、事件生命週期、平行結果契約、取消／逾時／恢復邊界。
- 第 17 章補齊安全分層、權限決策、Context 預算、秘密與提示注入限制。
- 第 18 章補齊 V10 完整組裝、V0～V10 能力矩陣、真實 Model Adapter 邊界與上線前差距。
- 新增 7 張靜態 SVG；全書現有 13 張 SVG。

## 下一階段

1. 為練習題加入解答方向與參考實作。
2. 執行全書第一輪技術編輯，統一重複警告、術語與章節銜接。
3. 執行第二輪文字編輯與反 AI 腔檢查。
4. 建立 EPUB 生產目錄、metadata、封面與建置腳本。
5. 執行 EPUBCheck、Ace by DAISY、閱讀器與 Google Play Books 預覽。
