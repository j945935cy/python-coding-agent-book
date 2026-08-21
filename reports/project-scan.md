# 階段 1：專案掃描報告

## 完成摘要

- 任務類型：專案掃描與技術設計
- 掃描時間：2026-08-21
- 目標專案：`/home/j945935/python-coding-agent-book`
- 初始狀態：目標目錄不存在，依指引建立最小骨架
- 原始規格：`/mnt/c/Users/j945935/Downloads/HERMES_PYTHON_CODING_AGENT_BOOK.md`

## 已檢查項目

- 工作區根目錄規範：`/home/j945935/AGENTS.md`
- 目標專案既有檔案：不存在，因此無既有內容可保留或覆蓋
- Pi repository：已取得研究快照
- Pi Commit：`5cd93f688aaab89dbb6dfa4aca535f21796ae185`
- 參考檔案：`packages/agent/src/agent-loop.ts`、`packages/agent/src/agent.ts`、`packages/coding-agent/src/main.ts`

## 研究觀察

1. Pi 的低階迴圈將 Agent 訊息保留到模型呼叫邊界才轉換成 LLM 訊息；本書採用 `transform_context()` 與 `convert_to_llm()` 分工。
2. 工具呼叫流程包含查找、參數驗證、`before_tool_call`、中止檢查、執行、`after_tool_call` 與工具結果事件；本書分階段重建此控制閉環。
3. 截斷模型輸出時，工具呼叫不得執行；本書把它列為不可繞過的安全測試。
4. 狀態化 Agent 需要管理 Transcript、串流狀態、AbortController、事件訂閱、Steering 與 Follow-up 佇列；這些內容後移到第 15–18 章。
5. CLI 入口應與核心 Agent Loop 分離，先完成可測試核心，再建立終端機介面。

## 第一輪驗收

- [x] 書名與副標題建立
- [x] 六篇十八章目錄建立
- [x] Pi 原始設計與本書 Python 重新設計的界線建立
- [x] `FakeModel` 測試策略建立
- [x] 核心 Protocol 草圖方向建立
- [x] 安全界線與風險清單建立
- [x] 下一階段檔案與開發順序建立
- [x] 尚未展開全書初稿

## 本批產物

- `AGENTS.md`
- `BOOK_PLAN.md`
- `STYLE_GUIDE.md`
- `GLOSSARY.md`
- `FACTS.md`
- `README.md`
- `reports/project-scan.md`
- `reports/architecture.md`
- `reports/test-matrix.md`
- `reports/risk-register.md`
- `reports/development-order.md`

## 未完成與待作者確認

- 是否使用 Pydantic 作為選配的 Schema 驗證示範
- Bash 工具允許的命令白名單與限制模式細節
- 最終 CLI 介面名稱與互動格式
- 是否需要在出版版加入實際模型 Adapter 範例
- Pi 授權文字與書中引用篇幅的最終審核

## 建議下一批

下一步進行全目錄逐章 API 核對與教學深化，建立章節程式碼片段的自動驗證，再進入完整版本範例與出版前稽核。章節結構、Python 語法與 V1～V4 完整範例輸出稽核已完成，下一批聚焦逐章內容品質與 API 名稱一致性。