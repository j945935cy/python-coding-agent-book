# 已查證事實

## Pi 研究來源

- Repository：https://github.com/earendil-works/pi
- 查證日期：2026-08-21
- 參考 Commit SHA：`5cd93f688aaab89dbb6dfa4aca535f21796ae185`
- 本次以該 Commit 的來源檔案作為研究快照。
- `packages/agent/src/agent-loop.ts`：796 行；包含低階 Agent Loop、事件發送、Context 轉換、工具準備、參數驗證、截斷工具呼叫拒絕、工具執行與前後 Hook。
- `packages/agent/src/agent.ts`：592 行；提供狀態化 Agent 包裝、訊息佇列、訂閱事件、AbortController、steering/follow-up 與工具執行模式。
- `packages/coding-agent/src/main.ts`：CLI 入口，負責模式判定、輸入處理與 Session Runtime 組裝。

## 引用界線

- 本書不是 Pi 官方 Python 版本。
- 早期版本的行數不可代表目前完整 Pi 專案的規模。
- 發行前仍須重新查證上游 Commit、授權與引用內容。