# 階段 2：技術原型測試報告

## 測試環境

- Python 要求：3.11+
- 實際執行：uv 管理的 Python 3.14.6
- 測試命令：`uv run --with pytest --with pytest-asyncio pytest -q`
- 語法命令：`uv run python -m compileall -q src tests`

## 結果

- 單一驗證入口：8 checks 全部 `PASS`、`valid=True`
- pytest：33 passed
- compileall：passed
- 學習段落稽核：18 章都有非空「練習」與「本章驗收」
- 術語稽核：0 violations，符合繁體中文與台灣用語規範
- API 參考稽核：核心公開 API 全部存在、無失效符號
- 完整範例輸出稽核：V0～V10 全部 `ok`、returncode=0
- Python 程式碼區塊稽核：21 blocks、0 syntax errors
- 章節稽核：18 章、編號 1～18 完整、無重複、無缺號、無失效引用
- 範例執行：`計算結果是 5。`
- V2 Workspace 範例執行：`print('hello, agent')`
- V3 Agent＋Workspace 範例執行：檔案已建立、修改並讀回。
- V4 事件／平行／取消範例執行：`9`、`events=tool_start,tool_end`
- 六章樣章引用檢查：6 chapters checked; missing=[]
- 核心測試不需要 API Key

## 已完成

- 訊息資料類別與序列化
- AgentContext 複製與 LLM payload 轉換
- AgentConfig 最大回合數、逾時與工具執行模式
- ModelClient Protocol
- FakeModel
- AgentTool Protocol 與 ToolRegistry
- 工具名稱與參數基本驗證
- 基本 Agent Loop
- 循序與平行工具執行
- 同步／非同步 before-tool safety hook
- 截斷模型輸出時拒絕工具執行
- Workspace 路徑邊界
- Calculator 工具，不使用 `eval()`
- Read、Write、Edit 工具
- Bash 限制模式、命令限制、Workspace、逾時
- 最大回合數防護
- 合作式 `CancellationToken` 與 `AgentCancelled`
- 工具事件在成功與失敗時都有收尾

## 已完成工具

- `src/mini_agent/chapter_audit.py`
- `scripts/audit_chapters.py`
- `tests/test_chapter_audit.py`
- `src/mini_agent/code_audit.py`
- `scripts/audit_code_blocks.py`
- `tests/test_code_audit.py`
- `src/mini_agent/example_audit.py`
- `scripts/verify_examples.py`
- `tests/test_example_audit.py`
- `src/mini_agent/api_audit.py`
- `scripts/audit_api_references.py`
- `tests/test_api_audit.py`
- `src/mini_agent/style_audit.py`
- `scripts/audit_style.py`
- `tests/test_style_audit.py`
- `src/mini_agent/learning_audit.py`
- `scripts/audit_learning_sections.py`
- `tests/test_learning_audit.py`
- `src/mini_agent/verification.py`
- `scripts/verify_all.py`
- `tests/test_verification.py`

## 已知限制

- 尚未加入完整事件串流 API；目前以事件收集器驗證工具開始／結束事件。
- 工具參數 Schema 目前是基本型態檢查，尚未加入 Pydantic 選配層。
- 尚未連接任何真實模型供應商。
