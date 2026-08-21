# 全書圖解規劃

## 原則

圖解只用於降低理解負擔，不以裝飾或增加頁數為目的。優先呈現：

- 資料如何流動
- 模組責任如何分界
- 狀態何時轉換
- 安全檢查在哪裡攔截
- 循序、平行、取消等時間關係

所有正式圖解使用靜態 SVG，正文保留替代文字與文字摘要；EPUB 不依賴 JavaScript 或執行 Mermaid。

## 圖解清單

| 優先級 | 章節 | 圖解 | 教學目的 | 狀態 |
|---|---:|---|---|---|
| P0 | 1 | Agent 行動閉環 | 分辨聊天回答與工具回饋閉環 | 已完成：`manuscript/assets/agent-loop.svg` |
| P0 | 2 | 七模組資料流 | 看懂責任、資料方向與攔截點 | 已完成：`manuscript/assets/seven-modules.svg` |
| P0 | 3 | ToolCall／ToolResult 配對 | 解釋平行完成時為何必須使用 ID | 已完成：`manuscript/assets/message-pairing.svg` |
| P1 | 4～5 | Context 生命週期與依賴注入 | 分辨狀態、設定、Hook 與物件依賴 | 待製作 |
| P1 | 6～8 | 工具契約與驗證管線 | 從具體 Calculator 過渡到 Registry、Validation | 待製作 |
| P0 | 9～12 | Workspace 邊界與檔案狀態轉換 | 顯示 Read／Write／Edit／Bash 的副作用與路徑限制 | 待製作 |
| P0 | 13 | Agent Loop 狀態機 | 呈現完成、工具、截斷、錯誤、最大回合分支 | 待製作 |
| P1 | 14 | 事件生命週期時間軸 | 配對 start／end，解釋失敗仍須收尾 | 待製作 |
| P1 | 15 | 循序與平行時間軸 | 分辨完成順序、回傳順序與資料相依 | 待製作 |
| P0 | 16 | 取消與錯誤恢復狀態圖 | 區分取消、逾時、可恢復錯誤與終止 | 待製作 |
| P0 | 17 | 三層安全防線與 Context 預算 | 顯示 Validation、Workspace、Safety Hook 的責任 | 待製作 |
| P1 | 18 | V10 完整架構 | 收束 Model、Loop、Registry、Workspace、事件與政策 | 待製作 |

## 製作規格

- 使用 `viewBox`，避免只依賴固定像素尺寸。
- 每張 SVG 包含 `<title>`、`<desc>`、`role="img"` 與 `aria-labelledby`。
- 文字在手機縮放後仍能辨識；避免塞入完整程式碼。
- 顏色之外仍以框線、標籤或線型區分狀態。
- 正文圖片語法必須有具體替代文字。
- 圖後提供一段能獨立理解的文字摘要。

## EPUB 前驗收

1. 所有 Markdown 圖片引用存在。
2. 所有 SVG 可由 XML parser 讀取。
3. SVG 不含 script、外部字型或遠端資源。
4. EPUB 打包後資源路徑不失效。
5. 以手機尺寸預覽，確認文字與箭頭可辨識。
