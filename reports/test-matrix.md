# 測試矩陣（階段 1 規劃）

| 區域 | 必測行為 | 測試替身 |
|---|---|---|
| Messages | 角色、內容、序列化與反序列化 | 純資料測試 |
| Context | 新增、複製、轉換與工具清單 | 純資料測試 |
| ModelClient | `FakeModel` 回應、工具呼叫、串流事件 | FakeModel |
| Validation | 缺欄位、錯型態、未知工具、截斷狀態 | 固定 payload |
| Registry | 查找、重複名稱、空名稱 | 純資料測試 |
| Agent Loop | 無工具結束、工具結果後繼續、最大回合數 | FakeModel |
| Read | 正常讀取、Workspace 外路徑、越界 | 臨時目錄 |
| Write | 建立、覆寫、Workspace 限制 | 臨時目錄 |
| Edit | 零匹配、唯一匹配、多重匹配 | 臨時檔案 |
| Bash | 成功、失敗、逾時、取消、危險命令 | 隔離 Workspace |
| Hooks | before 阻擋、after 修改結果 | 固定 Hook |
| Parallel | 結果維持原工具呼叫順序 | Fake tools |
| Events | 成功、錯誤、取消都有收尾事件 | Event collector |

## 發行前負向案例

- 截斷且可解析的工具參數不得執行。
- `../`、絕對路徑與符號連結逃逸不得讀寫 Workspace 外部。
- Bash 超過逾時必須停止並回傳可辨識錯誤。
- Agent 不得無限循環。
- 真實 API 不得出現在核心單元測試路徑。