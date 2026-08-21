# 名詞表（第一輪草案）

| 中文 | 英文 | 定義 |
|---|---|---|
| Agent | Agent | 能依目標持續觀察、決策並採取工具行動的程式系統。 |
| Agent Loop | Agent Loop | 模型回應、工具執行、結果回傳與下一輪推理所形成的循環。 |
| Context | Context | 模型在目前請求可使用的系統提示、訊息與工具資訊。 |
| 訊息 | Message | 對話中的使用者、模型或工具結果資料。 |
| 工具呼叫 | Tool Call | 模型要求程式執行特定工具及參數的結構化請求。 |
| 工具結果 | Tool Result | 工具執行後回傳給模型的成功或錯誤資訊。 |
| 串流 | Streaming | 模型或工具逐步產生事件，而非一次回傳完整結果。 |
| Steering message | Steering message | 在目前回合結束後插入、引導 Agent 繼續處理的訊息。 |
| Follow-up message | Follow-up message | Agent 原本準備停止後，要求它再繼續處理的訊息。 |
| Workspace | Workspace | 工具可操作的明確目錄邊界。 |
| FakeModel | FakeModel | 用於可預測、自動化測試的假模型實作。 |
| Hook | Hook | 在工具執行前或後介入檢查、阻擋或修改結果的擴充點。 |