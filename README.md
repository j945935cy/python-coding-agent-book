# Python Coding Agent 書籍專案

本專案將以繁體中文逐步製作《用 Python 自己寫一個 Coding Agent：從對話迴圈、工具呼叫到可擴充的 AI 程式助手》及其可執行範例。

目前處於：階段 3「六章樣章」。

## 執行技術原型

```bash
uv run --with pytest --with pytest-asyncio pytest -q
uv run python examples/v01_fake_model_loop.py
uv run python examples/v02_workspace_tools.py
uv run python examples/v03_agent_file_loop.py
uv run python examples/v04_events_parallel_cancel.py
```

完整範例程式、測試、逐版本範例與補充檔案，統一發布於：

https://github.com/j945935cy/python-coding-agent-book

正式出版版本應優先使用該 Repository 的 Git tag 或 GitHub Release；`main` 分支保留為持續維護中的開發版本。

## 第一輪閱讀

- `BOOK_PLAN.md`：全書定位、目錄與階段路線
- `STYLE_GUIDE.md`：文字與程式碼規範
- `GLOSSARY.md`：統一名詞
- `FACTS.md`：已查證來源與研究界線
- `reports/project-scan.md`：專案掃描與第一輪驗收
- `reports/architecture.md`：Python 架構草圖
- `reports/test-matrix.md`：測試矩陣
- `reports/risk-register.md`：風險清單
- `reports/development-order.md`：開發順序

## 目前限制

目前已建立第一版可執行 Python 技術原型、18 項測試與六章樣章初稿；尚未完成完整 V0～V10 範例、付費模型 Adapter 或出版輸出。