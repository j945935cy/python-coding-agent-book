# 書籍企劃

## 書名

《用 Python 自己寫一個 Coding Agent：從對話迴圈、工具呼叫到可擴充的 AI 程式助手》

## 定位

以可執行、可測試、可擴充的迷你 Python Coding Agent，帶讀者理解模型、Context、訊息、工具與 Agent Loop 的關係。Pi 是研究參考，不是本書的官方 Python 移植版。

## 六篇十八章

### 第一篇：先看懂 Coding Agent

1. 聊天機器人為什麼還不是 Agent
2. 把 Agent Loop 拆成七個模組

### 第二篇：建立 Agent 的資料模型

3. 用 Python 表示對話訊息
4. 建立 Agent Context
5. 設定、Callback 與依賴注入

### 第三篇：讓模型可以呼叫工具

6. 第一個工具：安全計算機
7. 建立通用工具介面與工具註冊表
8. 驗證模型產生的工具參數

### 第四篇：打造 Coding Agent 的四大工具

9. Read：安全讀取檔案
10. Write：建立與覆寫檔案
11. Edit：精確修改程式碼
12. Bash：執行系統指令

### 第五篇：完成 Agent Loop

13. 第一個完整 Agent Loop
14. 串流輸出與事件系統
15. 循序與平行工具
16. 中止、錯誤與恢復

### 第六篇：從範例走向可用系統

17. 安全攔截、權限與 Context 管理
18. 完成迷你 Python Coding Agent

## 階段路線

1. 專案掃描與技術設計
2. 可執行技術原型
3. 六章樣章
4. 逐章完成
5. 全書稽核與出版準備

## 第一輪決策

- Python 3.11+；核心優先使用標準函式庫。
- `ModelClient` 使用 `Protocol` 抽象；前期只使用 `FakeModel`。
- 非同步介面從早期版本建立，避免後期重寫 Agent Loop。
- Pydantic 暫列為選配，不作為第一輪必要依賴。
- 先建立低風險計算機，再建立 Workspace 受限的四項 Coding 工具。