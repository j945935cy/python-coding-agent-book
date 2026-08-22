# Python Coding Agent 書籍專案

本專案將以繁體中文逐步製作《用 Python 自己寫一個 Coding Agent：從對話迴圈、工具呼叫到可擴充的 AI 程式助手》及其可執行範例。

目前處於：階段 4「全書技術編輯準備」，第 1～18 章均已完成第一輪出版篇幅擴寫。

## 執行技術原型

```bash
uv run --extra test pytest -q
uv run python examples/v00_chatbot_baseline.py
uv run python examples/v01_fake_model_loop.py
uv run python examples/v02_workspace_tools.py
uv run python examples/v03_agent_file_loop.py
uv run python examples/v04_events_parallel_cancel.py
uv run python examples/v05_error_recovery.py
uv run python examples/v06_event_consumer.py
uv run python examples/v07_parallel_order.py
uv run python examples/v08_cooperative_cancel.py
uv run python examples/v09_safety_policy.py
uv run python examples/v10_complete_agent.py
uv run python scripts/audit_chapters.py .
uv run python scripts/audit_code_blocks.py .
uv run python scripts/verify_examples.py .
uv run python scripts/audit_api_references.py .
uv run python scripts/audit_style.py .
uv run python scripts/audit_learning_sections.py .
uv run --extra test python scripts/verify_all.py .
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
- `manuscript/appendices/exercise-solutions.md`：18 章、54 題練習解答與參考方向
- `manuscript/appendices/advanced-production-examples.md`：八個可執行產品化原型
- `examples/advanced/`：Adapter、CLI、授權、Runner、Stream、Context、Checkpoint、Transaction
- `publishing/`：1600×2400 封面、EPUB CSS、metadata、建置與驗證來源
- `dist/python-coding-agent-book.epub`：EPUB 3 發行草稿

## 目前限制

目前已建立第一版可執行 Python 技術原型、100 項測試、19 個可驗證範例、18 章第一輪擴寫稿、54 題練習解答方向、八個進階產品化原型、13 張靜態 SVG、1600×2400 封面與通過 EPUBCheck 的 EPUB 3 發行草稿；尚未完成全書技術／文字編輯、Ace、閱讀器實測、Google Play Books 預覽或真實模型 Adapter。