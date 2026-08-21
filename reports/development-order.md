# 開發順序

## 階段 2：技術原型

1. 建立 `pyproject.toml`、`src/mini_agent/`、`tests/` 與 `examples/`。
2. 先實作 `messages.py` 與 `context.py`。
3. 實作 `config.py`、`events.py` 與 `model_client.py`。
4. 實作工具 Protocol、Registry 與參數驗證。
5. 先加入安全計算機與 `FakeModel`。
6. 加入基本 `run_agent_loop()`。
7. 加入 Workspace 安全層與 Read、Write、Edit、Bash。
8. 加入 Hook、逾時、取消與最大回合數。
9. 加入循序／平行工具執行與事件收尾。
10. 執行完整 pytest，產生 `reports/test-report.md`。

## 階段 3：樣章

依序撰寫第 1、3、6、8、13、18 章。每章先核對對應程式版本，再撰寫教學與練習。

## 階段 4：逐章

依目錄順序，每批只處理一章；完成程式、測試、書稿與 `reports/chapter-status.md` 後才進入下一章。

## 階段 5：出版

來源稽核 → 程式／書稿一致性 → EPUB／PDF／HTML 建置 → 結構驗證 → 視覺檢查 → 發行封裝。