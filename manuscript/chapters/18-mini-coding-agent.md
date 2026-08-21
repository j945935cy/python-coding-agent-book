# 18. 完成迷你 Python Coding Agent

## 本章目標

把本書的核心零件組合成一個小而完整、可以繼續擴充的 Python Coding Agent。

## 目前組合出的邊界

本專案已具備：

- `ModelClient` Protocol 與 `FakeModel`
- 可序列化訊息與 AgentContext
- ToolRegistry 與 Calculator、Read、Write、Edit、Bash
- Workspace 路徑限制
- 工具參數驗證
- 循序／平行執行
- 逾時、最大回合數、安全 Hook
- 合作式 `CancellationToken`

這些元件刻意保持小型。可用系統不是把所有功能塞進一個巨大類別，而是讓每個責任都有清楚的測試邊界。

## 從 FakeModel 到真正模型

下一個 Adapter 只需要實作：

```python
class ModelClient(Protocol):
    async def complete(self, context: AgentContext) -> AssistantMessage:
        ...
```

真正供應商的差異應停留在 Adapter：認證、HTTP、供應商格式與重試。核心 Loop 不應知道 API Key 或特定 SDK。

## 上線前清單

- [ ] 所有工具都有限制與錯誤測試。
- [ ] 所有外部模型輸入都經過驗證。
- [ ] 工具逾時與取消不會留下未完成狀態。
- [ ] Context 不會無限制成長。
- [ ] 測試、書稿與範例版本一致。
- [ ] 發行時使用 Git tag，而不是未驗證的 main。

## 練習

請新增一個 `list_files` 工具，限制只能列出 Workspace 內的相對路徑，並以測試證明它不能走出 Workspace。

## 本章驗收

能從公開 Repository 安裝並執行 V1 範例，能閱讀測試理解 Agent Loop，並能在不改動核心 Loop 的前提下替換 ModelClient。
