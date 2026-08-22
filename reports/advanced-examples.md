# 進階產品化範例報告

## 範圍

V10 維持 FakeModel-only 的核心整合；八個進階原型放在 `examples/advanced/`，不直接改變穩定 Agent Loop API。

| 範例 | 主要能力 | 目前限制 | 測試群組 |
|---|---|---|---|
| `recording_adapter.py` | 無金鑰 provider fixture 轉換、bounded retry | 不連真實供應商 | Adapter／CLI |
| `interactive_cli.py` | 可注入 input／output、五個 slash commands | 預設 FakeModel | Adapter／CLI |
| `full_registry.py` | 五種工具註冊與獨立授權政策 | 不自動核准副作用 | Registry／Runner |
| `sandbox_runner.py` | 結構化 argv、無 shell、極小 allowlist | 不是 OS sandbox | Registry／Runner |
| `event_stream.py` | Condition＋deque 有界事件流、async iterator、背壓與取消清理 | 未整合核心 list collector | Stream／Context |
| `context_budget.py` | 訊息／字元預算、配對群組與 pinned evidence | 不是精準 token 計算 | Stream／Context |
| `checkpoint_sqlite.py` | schema version、payload hash、reopen-safe replay | 不保證所有 crash window exactly-once | Checkpoint／Transaction |
| `multi_file_transaction.py` | staging、validator、commit／rollback | 非分散式交易 | Checkpoint／Transaction |

## TDD 與執行結果

四組工作均先觀察 RED，再完成 GREEN。獨立複審後另以 RED→GREEN 補上 duplicate ToolCall ID、blocked publisher cancellation、publish／abort 兩種排程交錯，以及 blocked close cancellation 的回歸測試。進階測試共 56 項；連同既有測試，全套結果為：

```text
98 passed
```

`verify_examples.py` 已納入 V0～V10 與八個進階範例，共 19 個可執行範例，全部 returncode=0 且輸出符合 manifest。

## 確定性輸出

```text
recording_adapter.py       assistant> Offline adapter response. / requests=1
interactive_cli.py         Mini Agent CLI (offline). / you> Bye.
full_registry.py           registered=... / bash=deny
sandbox_runner.py          structured argv
event_stream.py            events=0,1,2 / dropped=0 closed=True
context_budget.py          before=6 / after=4 / latest_user_kept=True
checkpoint_sqlite.py       result=checkpointed replay_equal=True calls=1
multi_file_transaction.py  committed=true files=config.txt,notes.txt / version=2
```

## 出版整合

- 第 18 章新增「從限制清單到可執行原型」。
- `manuscript/appendices/advanced-production-examples.md` 提供八個範例的用途、命令、輸出、邊界與整合建議。
- EPUB 建置腳本會把進階附錄納入「附錄」導覽。

## 尚未宣稱完成

- 真實 Provider Adapter 與 API Key 流程
- token-level 模型串流
- OS／Container sandbox
- 核心 Context compactor
- 所有 crash window 的 exactly-once
- 分散式交易
