# 階段 2：技術原型測試報告

## 測試環境

- Python 要求：3.11+
- 實際執行：uv 管理的 Python 3.14.6
- 測試命令：`uv run --with pytest --with pytest-asyncio pytest -q`
- 語法命令：`uv run python -m compileall -q src tests`

## 結果

- pytest：18 passed
- compileall：passed
- 範例執行：`計算結果是 5。`
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

## 已知限制

- 尚未加入完整事件串流 API；目前以事件收集器驗證工具開始／結束事件。
- 工具參數 Schema 目前是基本型態檢查，尚未加入 Pydantic 選配層。
- 尚未建立完整 V0～V10 範例。
- 尚未連接任何真實模型供應商。
