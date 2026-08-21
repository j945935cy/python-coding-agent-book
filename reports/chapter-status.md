# 章節進度

18 個章節 Markdown 均已建立，並對應可執行原型與自動化驗收。第 1～8 章已完成第一輪出版篇幅擴寫；第 9～18 章仍是不同深度的教學初稿。

| 章節 | 檔案 | 狀態 | 對應驗收 |
|---:|---|---|---|
| 1 | `manuscript/chapters/01-chatbot-vs-agent.md` | 第一輪擴寫完成 | V0／V1、`agent-loop.svg` |
| 2 | `manuscript/chapters/02-seven-modules.md` | 第一輪擴寫完成 | 七模組責任表、`seven-modules.svg` |
| 3 | `manuscript/chapters/03-message-model.md` | 第一輪擴寫完成 | `tests/test_messages.py`、`message-pairing.svg` |
| 4 | `manuscript/chapters/04-agent-context.md` | 第一輪擴寫完成 | `tests/test_messages.py`、`context-lifecycle.svg` |
| 5 | `manuscript/chapters/05-config-hooks-injection.md` | 第一輪擴寫完成 | `tests/test_agent_controls.py`、`dependency-injection.svg` |
| 6 | `manuscript/chapters/06-safe-calculator.md` | 第一輪擴寫完成 | Calculator 成功、未知操作、錯誤型態測試 |
| 7 | `manuscript/chapters/07-tool-registry.md` | 第一輪擴寫完成 | 重複名稱、未知工具分派測試 |
| 8 | `manuscript/chapters/08-tool-validation.md` | 第一輪擴寫完成 | ToolCall Validation、Safety Hook 執行順序測試、`tool-contract-pipeline.svg` |
| 9 | `manuscript/chapters/09-read-tool.md` | 工具章初稿 | `tests/test_safety.py`、`tests/test_tools.py` |
| 10 | `manuscript/chapters/10-write-tool.md` | 工具章初稿 | `tests/test_tools.py` |
| 11 | `manuscript/chapters/11-edit-tool.md` | 工具章初稿；已局部補強 | `tests/test_tools.py` |
| 12 | `manuscript/chapters/12-bash-tool.md` | 工具章初稿 | `tests/test_bash_tool.py` |
| 13 | `manuscript/chapters/13-agent-loop.md` | 教學初稿；已局部補強 | `tests/test_agent_loop.py` |
| 14 | `manuscript/chapters/14-events-and-streaming.md` | 教學初稿；已局部補強 | 事件收尾測試 |
| 15 | `manuscript/chapters/15-parallel-tools.md` | 教學初稿；已局部補強 | 平行工具測試 |
| 16 | `manuscript/chapters/16-cancellation-errors-recovery.md` | 教學初稿 | 取消與逾時測試 |
| 17 | `manuscript/chapters/17-safety-context.md` | 教學初稿；已局部補強 | `tests/test_safety.py`、`tests/test_cancellation.py` |
| 18 | `manuscript/chapters/18-mini-coding-agent.md` | 教學初稿；已局部補強 | 全套原型測試 |

## 本批完成：第 6～8 章

- 第 6 章補齊安全 Calculator 完整實作、可執行成功案例、未知操作、數值型態錯誤、布林值限制說明、檢查清單與分級練習。
- 第 7 章補齊 `AgentTool` Protocol、結構式子型別、註冊與分派、空名稱、重複名稱、未知工具，以及可執行 PingTool 範例。
- 第 8 章補齊 `Validation → Safety Hook → Registry → Tool → ToolResultMessage` 管線、錯誤分類、取消邊界與驗證命令。
- 新增 `manuscript/assets/tool-contract-pipeline.svg`，含替代文字、文字摘要與 EPUB 可存取性標記。
- 新增或補強 Calculator 型態、Registry 邊界、空 call ID 與 Safety Hook 執行順序測試。

## 下一輪：第 9～12 章

1. 擴寫 Workspace 邊界與路徑解析的共同基礎。
2. 補齊 Read、Write、Edit、Bash 的完整可複製程式與失敗案例。
3. 明確區分讀取、覆寫、精確替換與受限命令的副作用。
4. 製作 Workspace 邊界與檔案狀態轉換 SVG。
5. 每章加入檢查清單、三題分級練習、驗收條件與實際測試命令。
