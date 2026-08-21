# 樣章進度

本批建立六章樣章第一版，對應既有可執行原型：

| 章節 | 檔案 | 狀態 | 對應驗收 |
|---|---|---|---|
| 1 | `manuscript/chapters/01-chatbot-vs-agent.md` | 初稿 | V1 FakeModel Loop |
| 3 | `manuscript/chapters/03-message-model.md` | 初稿 | `tests/test_messages.py` |
| 6 | `manuscript/chapters/06-safe-calculator.md` | 初稿 | `tests/test_calculator.py` |
| 8 | `manuscript/chapters/08-tool-validation.md` | 初稿 | `tests/test_validation.py` |
| 13 | `manuscript/chapters/13-agent-loop.md` | 初稿 | `tests/test_agent_loop.py` |
| 18 | `manuscript/chapters/18-mini-coding-agent.md` | 初稿 | 全套原型測試 |
| 14 | `manuscript/chapters/14-events-and-streaming.md` | 教學初稿 | 事件收尾測試 |
| 15 | `manuscript/chapters/15-parallel-tools.md` | 教學初稿 | 平行工具測試 |
| 16 | `manuscript/chapters/16-cancellation-errors-recovery.md` | 教學初稿 | 取消測試 |
| 9 | `manuscript/chapters/09-read-tool.md` | 工具章初稿 | `tests/test_safety.py`、`tests/test_tools.py` |
| 10 | `manuscript/chapters/10-write-tool.md` | 工具章初稿 | `tests/test_tools.py` |
| 11 | `manuscript/chapters/11-edit-tool.md` | 工具章初稿 | `tests/test_tools.py` |
| 12 | `manuscript/chapters/12-bash-tool.md` | 工具章初稿 | `tests/test_bash_tool.py` |

本批在六章樣章之外，補上第 9～12、14～16 章的教學初稿，並加入 `examples/v02_workspace_tools.py` 與 `examples/v03_agent_file_loop.py`。目前共有 13 個章節 Markdown 檔案，其中六章為主要樣章、七章為後續主題的教學初稿。

## 下一輪樣章審查

1. 逐章核對 API 名稱與目前程式碼。
2. 為每章補至少一個完整可複製的程式區塊。
3. 加入章末延伸練習解答或驗收提示。
4. 檢查繁體中文術語、章節銜接與難度梯度。
5. 建立第 14～16 章所需的事件、串流與取消教學素材。
