# 階段 2：技術原型測試報告

## 測試環境

- Python 要求：3.11+
- 實際執行：uv 管理的 Python 3.13.15
- 測試命令：`uv run --extra test pytest -q`
- 統一驗證：`uv run --extra test python scripts/verify_all.py .`
- 語法命令：`uv run python -m compileall -q src tests`

## 結果

- 單一驗證入口：8 checks 全部 `PASS`、`valid=True`
- pytest：42 passed
- compileall：passed
- 學習段落稽核：18 章都有非空「練習」與「本章驗收」
- 術語稽核：0 violations，符合繁體中文與台灣用語規範
- API 參考稽核：核心公開 API 全部存在、無失效符號
- 完整範例輸出稽核：V0～V10 全部 `ok`、returncode=0
- Python 程式碼區塊稽核：61 blocks、0 syntax errors
- 章節稽核：18 章、編號 1～18 完整、無重複、無缺號、無失效引用
- 書稿量化：18 個本章目標、18 個練習、18 個本章驗收、13 個本章小結
- 章節 Markdown：共 2,991 行；第 9～18 章均完成第一輪擴寫
- 範例執行：`計算結果是 5。`
- V2 Workspace 範例執行：`print('hello, agent')`
- V3 Agent＋Workspace 範例執行：檔案已建立、修改並讀回。
- V4 事件／平行／取消範例執行：`9`、`events=tool_start,tool_end`
- 章節引用檢查：18 chapters checked; missing=[]
- 核心測試不需要 API Key

## 第 6～8 章擴寫批次驗證

- Calculator、Validation、Registry、Safety Hook 目標測試：14 passed
- 目標測試命令：`uv run --extra test pytest tests/test_calculator.py tests/test_validation.py tests/test_tool_registry.py tests/test_agent_controls.py -q`
- 新增 Calculator 非數值參數測試
- 新增 Registry 重複名稱與未知工具分派測試
- 新增 Registry 空名稱測試
- 新增空 ToolCall ID 測試
- 新增只有空白字元的 ToolCall ID 測試
- 新增 Safety Hook 先於 Tool 執行的順序測試
- 從第 6 章 Markdown 擷取並執行 Calculator 成功範例：`{'result': 42}`
- 從第 7 章 Markdown 擷取並執行 PingTool／Registry 範例：工具清單、`pong` 與 Calculator 42 均符合預期
- `tool-contract-pipeline.svg`：XML 可解析、具 `viewBox`、`title`、`desc`、`role="img"`、`aria-labelledby`，且不含 script
- SVG 點陣預覽的元件、箭頭與行距無重疊；目前 WSL 缺少中文字型，中文字形仍須在 EPUB／閱讀器環境複驗

## 第 9～18 章擴寫批次驗證

- 第 9～18 章均加入章節目標、核心流程、失敗分類、限制、檢查清單、分級練習、小結與驗收。
- 新增 7 張 SVG；全書共 13 張，全部 XML 可解析，具 `viewBox`、`title`、`desc`、`role="img"` 與 `aria-labelledby`，且不含 script。
- 7 張新 SVG 已實際轉成 PNG 接觸表檢查，框線、箭頭、英文文字、間距與裁切無重疊；WSL 缺少中文字型，中文字形仍待 EPUB／閱讀器複驗。
- 第 9～12 章實作與測試命令對應 Read、Write、Edit、Bash 與 Workspace 邊界。
- 第 13～16 章對應 Agent Loop、事件收尾、平行順序、取消、逾時與最大回合測試。
- 第 17～18 章明確標示 Context、秘密、prompt injection、Bash 沙箱與真實 Adapter 尚未完成的限制。
- 從 Markdown 精確擷取並執行第 9、10、11、12、13、15、18 章完整範例，全部 returncode=0；輸出分別涵蓋 Read、Write、Edit、Workspace `pwd`、兩回合 Loop、平行順序與 V10 完整整合。
- 修正 V6 事件消費範例的 Calculator 參數，現在實際輸出 `tool_result=10 error=False`；新增回歸測試，避免腳本式最終回答掩蓋工具失敗。
- 以 TDD 修正 Bash NUL 正規表示式：先證明實際 NUL 未被工具攔截，再修正 `_SHELL_OPERATORS` 並加入回歸測試。

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
