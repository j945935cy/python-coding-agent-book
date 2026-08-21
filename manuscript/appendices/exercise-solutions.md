# 練習解答與參考方向

本附錄對應正文 18 章、共 54 題練習。建議先自行完成題目並保存測試結果，再閱讀解題方向。

解答採以下結構：

- **解題方向**：應先做的判斷與實作順序。
- **起始狀態**：使用哪些章節程式、測試或暫存 Workspace。
- **預期產物**：完成後應新增或修改什麼。
- **驗證方法**：用哪些命令或斷言判定完成。
- **常見錯誤**：容易造成誤判、安全漏洞或不可重現結果的做法。

本附錄提供的是可驗證參考方向，不鼓勵直接複製答案。涉及 Bash、檔案寫入、真實模型或外部服務時，請先在暫存 Workspace 執行；核心測試維持不需要 API Key。

---
## 第 1 章

### 練習 1：把 V1 的加法改成乘法，先寫出預期輸出再執行

- **解題方向**： 在 `examples/v01_fake_model_loop.py` 同時修改使用者問題、`ToolCall.arguments` 與 `FakeModel` 的最終回答。例如把 operation 改為 `multiply`，運算元改為 2 與 3，並先寫下預期輸出 `計算結果是 6。`。這個範例的模型是預先排定回應的 `FakeModel`，不會自行根據工具結果重寫最後一句，因此三處必須保持一致。
- **起始狀態**： V1 目前要求 `calculator` 執行 `add(2, 3)`，第二個假模型回應固定為 `計算結果是 5。`；Calculator 已支援 `multiply`。
- **預期產物**： 一個仍可離線執行的 V1 範例；Context 中依序出現 User、帶乘法 ToolCall 的 Assistant、內容為 `{"result": 6}` 的 ToolResult，以及最終 Assistant 回應。
- **驗證方法**： 從專案根目錄執行 `uv run python examples/v01_fake_model_loop.py`，確認結束碼為 0，標準輸出與事先寫下的預期完全相同。再執行 `uv run --extra test pytest tests/test_agent_loop.py -q`，確認既有 Loop 行為未被破壞。
- **常見錯誤**： 只改 `operation` 卻保留「5」；誤以為 FakeModel 會讀取計算結果並自行生成答案；直接改 Calculator 的全域行為；為這個離線練習加入 API Key。

### 練習 2：在測試中加入未知工具，觀察錯誤如何成為 `ToolResultMessage`

- **解題方向**： 建立第一個 `AssistantMessage`，其中放入名稱未註冊（例如 `missing`）的 ToolCall，再提供一個最終 Assistant 回應。以空的或只含其他工具的 Registry 執行 Loop，斷言未知工具沒有被執行，倒數第二筆歷史是 `ToolResultMessage`、`is_error is True`、ID 與名稱原樣保留，且 content 含 `Unknown tool`。
- **起始狀態**： `validate_tool_call()` 會對未知名稱拋出 `ToolValidationError`；`run_agent_loop()` 會捕捉工具路徑中的例外並轉成錯誤 ToolResult。`tests/test_validation.py` 已直接測未知工具，但 `tests/test_agent_loop.py` 尚未覆蓋「經 Loop 回填 Context」這條整合路徑。
- **預期產物**： 一個非網路、可重複的非同步測試，證明錯誤結果的 `tool_call_id`、`tool_name`、`is_error` 與訊息內容，而不是只檢查最終自然語言回答。
- **驗證方法**： 執行新增測試所在檔案；建議命令為 `uv run --extra test pytest tests/test_agent_loop.py -q`。測試必須以結束碼 0 完成，且歷史中的錯誤結果應對應原 ToolCall ID。
- **常見錯誤**： 直接呼叫 Registry 而沒有測到 Loop 的錯誤轉換；只斷言模型最後說「失敗」；把未知工具先註冊，導致測試不再走錯誤路徑；斷言完整例外字串而讓測試過度脆弱。

### 練習 3：畫出正常完成、最大回合數與取消三條停止路徑

- **解題方向**： 以同一個起點「Loop 進入回合並先檢查取消」畫三條分支：① Model 回傳無 ToolCall 的 Assistant，立即回傳 history；② 每回合都有 ToolCall，耗盡 `max_turns` 後拋出 `RuntimeError`；③ CancellationToken 在模型呼叫前或 Hook 後的取消檢查拋出 `AgentCancelled`。標出工具副作用前仍有一次取消檢查。
- **起始狀態**： `run_agent_loop()` 已實作正常完成、最大回合與取消；`tests/test_agent_controls.py` 和 `tests/test_cancellation.py` 有對應證據。最大回合不是一筆 ToolResult，而是 Loop 離開 for 迴圈後拋出例外。
- **預期產物**： 一張含「模型決策、驗證／Hook、工具執行、結果回填、停止」主要狀態的流程圖，三個終點分別註明「回傳 history」、「RuntimeError」與「AgentCancelled」。
- **驗證方法**： 逐一用現有測試對照每條箭頭：`uv run --extra test pytest tests/test_agent_loop.py tests/test_agent_controls.py tests/test_cancellation.py -q`。圖中不得把取消畫成只能在工具完成後發生，也不得把最大回合畫成正常答案。
- **常見錯誤**： 把「無 ToolCall」畫成錯誤；漏掉回合起點與工具前的取消檢查；聲稱目前有獨立的整體 Agent 逾時計時器（現有 Config 只有每次工具逾時）；把截斷輸出等同於正常完成。

## 第 2 章

### 練習 1：指出哪個模組可以知道 API Key，並說明其他模組為何不需要

- **解題方向**： 把 API Key 限定在具體模型供應商 Adapter（ModelClient 的實作）或其建立位置；組裝根可從環境取得憑證並傳給 Adapter，但不應把值放入 Message、Context、Tool、Registry、Validation／Safety 或 Agent Loop。其他模組只依賴本書的資料契約與抽象介面即可工作。
- **起始狀態**： 本書前六章使用 `FakeModel`，測試與 V0／V1 不需要 API Key；核心 `ModelClient` 邊界與訊息型態未綁定供應商 SDK。
- **預期產物**： 一份七模組責任表或架構圖，在 ModelClient Adapter 邊界標示「可持有憑證」，並為其餘每層寫出不需要憑證的理由，例如 Tool 只執行有限能力、Loop 只協調流程。
- **驗證方法**： 搜尋自己的設計或範例，確認 API Key 不出現在 `AgentContext.messages`、metadata、工具 arguments、事件或測試 fixture；以 FakeModel 執行核心測試時不應讀取環境憑證。
- **常見錯誤**： 把 Key 放進 system prompt 或 metadata；讓每個工具都讀環境變數；在 import 時建立真實網路 client；誤稱抽象 `ModelClient` 本身必須知道某家供應商的 Key 格式。

### 練習 2：為「列出 Workspace 檔案」標出 Message、Tool、Registry、Validation 各自的工作

- **解題方向**： Message 表示請求與結果（含 ToolCall ID）；Tool 實際列出受限 Workspace 內的檔案並處理檔案系統錯誤；Registry 依名稱找到並分派該 Tool；Validation 檢查通用呼叫格式、名稱是否已知及 arguments 是否為 dict。路徑是否逃出 Workspace 屬於 Workspace／具體 Tool 的業務安全檢查，不要只靠通用 Validation。
- **起始狀態**： 前六章已有 Message、Registry 與通用 Validation；「列出 Workspace 檔案」是責任切分題，不代表目前已有名為 list-files 的正式工具。
- **預期產物**： 一張四欄表或序列圖，至少包含 `ToolCall(id, name, arguments)`、Registry lookup、Tool 的 Workspace 邊界檢查與 `ToolResultMessage` 回填；每項工作只有一個主要負責層。
- **驗證方法**： 用三個反例檢查圖：未知名稱應在 Validation／Registry 停止，非 dict arguments 應在 Validation 停止，`../../` 越界應在 Workspace／Tool 停止。任何一例都不應需要模型文字自行判斷。
- **常見錯誤**： 宣稱 Registry 解析每個工具的 `path` 欄位；讓 Message 直接存取檔案系統；把路徑越界留給 prompt；把尚未實作的列檔工具寫成既有功能。

### 練習 3：把寫死在 Tool 的 `max_turns` 改成 Config 注入，列出測試簡化之處

- **解題方向**： 從設計上移除 Tool 內的回合計數與全域常數，改由呼叫端建立 `AgentConfig(max_turns=...)` 並傳給 `run_agent_loop()`；Loop 擁有回合控制，Tool 每次只處理一次 `execute()`。列出測試可各自建立 Config、使用小回合數快速觸發停止、互不污染，也不必製造特殊 Tool 子類。
- **起始狀態**： 專案目前已採目標設計：`AgentConfig` 是 frozen dataclass，`run_agent_loop()` 讀取 `config.max_turns`，Calculator 等 Tool 不知道最大回合數。因此此題可用重構前後的設計草圖或小型假例說明，不應重複搬動既有程式。
- **預期產物**： 一個「前：Tool／全域狀態控制回合；後：組裝根 → Config → Loop」的差異說明，以及至少三項測試改善：隔離性、可設定極小界線、同一 Tool 可重用。
- **驗證方法**： 以 `AgentConfig(max_turns=1)` 搭配持續要求工具的 FakeModel，確認 `tests/test_agent_controls.py::test_agent_stops_at_max_turns` 所代表的行為；再確認 Tool 的 `execute()` 簽章不含 Config 或回合參數。
- **常見錯誤**： 把 Config 做成可變 singleton；把 `max_turns` 傳給每個 Tool；只縮短 FakeModel 回應列表而沒有驗證 Loop 的界線；誤把回合上限當成工具逾時。

## 第 3 章

### 練習 1：新增 `SystemMessage`，並說明是否應進入公開 `Message` Union

- **解題方向**： 先決定契約再寫類別。依目前架構，建議把 system 指令留在 `AgentContext.system_prompt`，由供應商 Adapter 明確轉換，因此即使為 Adapter 建立 `SystemMessage`，也不要在沒有改變 Context 公開契約與測試的情況下把它加入 `Message` Union。若產品決定允許呼叫端把 system 訊息直接放入 `messages`，則必須一併把 `"system"` 加入 `Role`、將類別加入 Union，並測試 `convert_to_llm()` 的送出行為；這是另一個明確契約，不能只改型別別名。
- **起始狀態**： `Role` 只有 `user`、`assistant`、`tool`；公開 `Message` Union 只有三種訊息；`AgentContext` 另有 `system_prompt`，且 `convert_to_llm()` 目前不送出該欄位。
- **預期產物**： 一個清楚記錄取捨的設計決定，以及與決定一致的類別、型別與測試。推薦解答應保持現有「system_prompt 由 Adapter 處理」邊界，不讓 system 指令因加入 messages 而被無意送出兩次。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_messages.py -q`；若選擇公開 SystemMessage，新增測試應精確驗證 role、序列化與 Context payload。若選擇 Adapter 私有，測試應證明公開 Message／Context 行為未改變，並在說明中記錄原因。
- **常見錯誤**： 只新增 dataclass 卻忘記 `Role`；加入 Union 後沒注意 `convert_to_llm()` 會自動序列化所有 messages；同時送出 `system_prompt` 與 SystemMessage 造成重複；把設計選擇誤寫成 Python 唯一正解。

### 練習 2：為空工具 ID 與非 dict arguments 加入失敗測試

- **解題方向**： 直接測 `validate_tool_call()` 的通用邊界：空字串與只有空白的 ID 應匹配 `ToolValidationError` 的 ID 訊息；list、字串等非 dict arguments 應匹配 arguments 訊息。由於 dataclass 在執行期不會強制型別，可故意傳入 list 來驗證 Validation。
- **起始狀態**： 這些測試已存在於 `tests/test_validation.py`，實作也會先拒絕非 dict arguments，再以 `call.id.strip()` 拒絕空白 ID。`tests/test_messages.py` 只驗證正常序列化，不負責通用 ToolCall 驗證。
- **預期產物**： 若目前 checkout 不需再改，產物是對既有三個測試的驗證紀錄；若作為獨立練習重建，應有空 ID、空白 ID與非 object arguments 三個小測試。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_validation.py -q`。還可暫時移除對應檢查以確認測試會失敗，再復原；不要把故意的失敗版本留在最終程式。
- **常見錯誤**： 以為型別註記會在 runtime 自動拒絕 list；只測 `id=""` 而放過空白字串；期待建構 `ToolCall` 當下拋錯（目前是在 Validation 階段）；重複新增與既有測試完全相同的案例。

### 練習 3：建立兩個 ToolCall 與反向完成的結果，證明配對不依賴位置

- **解題方向**： 建立 ID 不同的兩個呼叫，例如 `read-1`、`test-1`，再以相反順序建立 ToolResult。用 `tool_call_id` 建立 mapping，斷言每個結果仍能找到原呼叫；不要以 `zip(calls, results)` 配對。若測 Loop 的平行模式，要注意 `asyncio.gather()` 目前會按輸入順序回傳結果，因此「真實完成先後」與「history 排列順序」是兩件事。
- **起始狀態**： `ToolResultMessage` 已保留 `tool_call_id`；`tests/test_agent_controls.py` 證明平行工具即使 B 先完成，寫入 history 仍維持模型呼叫順序。現有訊息測試尚未直接用反向結果列表證明 ID 配對。
- **預期產物**： 一個純訊息層測試或小型示例，結果列表順序與呼叫列表相反，但以 ID 查找後內容仍正確；同時保留 `tool_name` 供觀察，配對依據則是 ID。
- **驗證方法**： 執行新增測試與既有平行控制測試：`uv run --extra test pytest tests/test_messages.py tests/test_agent_controls.py -q`。交換結果順序後，測試仍應通過。
- **常見錯誤**： 以工具名稱配對（同一工具可被呼叫多次）；用列表索引或 `zip`；把 history 的穩定輸入順序誤稱為實際完成順序；重複使用相同 ToolCall ID。

## 第 4 章

### 練習 1：用 metadata 記錄 Workspace 標籤，並證明 `convert_to_llm()` 不會送出 metadata

- **解題方向**： 建立帶有一般標籤（例如 `{"workspace_label": "demo"}`）的 AgentContext，messages 放一筆 UserMessage；呼叫 `convert_to_llm()` 後斷言 payload 只有訊息的 role/content，不含 `metadata`、`workspace_label` 或 API Key。標籤應是非秘密識別，不是憑證。
- **起始狀態**： `AgentContext.metadata` 是本機 dict；`convert_to_llm()` 只逐一呼叫 `message.to_dict()`，所以目前不會送出 metadata 或 `system_prompt`。尚無專門的 Context 測試檔覆蓋此契約。
- **預期產物**： 一個針對 Context 的測試，明確分開「本機可讀 metadata」與「模型 payload」兩個斷言；測試資料中不要放真實 API Key，即使只是為了證明不外洩。
- **驗證方法**： 執行新增的 Context 測試；另可斷言 `context.metadata["workspace_label"] == "demo"` 且 payload 等於 `[{"role": "user", "content": ...}]`。
- **常見錯誤**： 用真實秘密當測試資料；只檢查頂層沒有 `metadata`，卻不檢查標籤是否被拼進 content；把絕對 Workspace 路徑當成一定可外送的標籤；修改 `to_dict()` 來讀 Context metadata。

### 練習 2：測試 `copy()` 的分支隔離與巢狀 metadata 共享

- **解題方向**： 先建立原 Context，再 `branch = original.copy()`。向 `branch.messages` append 新訊息，斷言 original 長度不變；新增 branch 的 metadata 頂層 key，斷言 original 沒有該 key。接著把原 metadata 設為 `{"labels": ["base"]}`，對 branch 內同一 list append，斷言 original 也看得到新元素，以記錄目前是淺拷貝。
- **起始狀態**： `copy()` 使用 `list(self.messages)` 與 `dict(self.metadata)`：兩個外層容器是新的，但訊息物件與巢狀 metadata value 仍共享。
- **預期產物**： 至少兩個測試：一個證明外層 messages／metadata 隔離，一個刻意證明巢狀可變值共享。後者是現況契約的警示，不是深拷貝已完成的證明。
- **驗證方法**： 執行新增測試並檢查物件關係：`branch.messages is not original.messages`、`branch.metadata is not original.metadata`，但 `branch.metadata["labels"] is original.metadata["labels"]`。
- **常見錯誤**： 把淺拷貝描述成完整隔離；因巢狀共享測試通過就誤認為安全；直接改成 `deepcopy` 而沒有評估訊息／metadata 成本；只比對相等值，沒有觸發可觀察的 mutation。

### 練習 3：實作只計算訊息數與字元數的 Context 預算函式，超過預算時回傳明確狀態

- **解題方向**： 寫一個無副作用 helper，從 `len(context.messages)` 取得訊息數，並以章內定義 `sum(len(str(item.to_dict())) ...)` 計算供應商無關的字元指標。函式接收明確的 `max_messages`、`max_characters`，回傳包含兩個實際值與 `exceeded` 的穩定結構；邊界應先決定是 `>` 還是 `>=`，建議「等於上限仍允許，超過才 True」。
- **起始狀態**： 章內只有 `context_size()` 示意；`src/mini_agent/context.py` 尚未提供正式預算函式，也沒有精準 token 計算。不可宣稱目前會自動摘要或截斷 Context。
- **預期產物**： 一個命名清楚的 helper 與至少三組測試：低於上限、恰好等於上限、任一維度超過上限。回傳值應讓呼叫端知道是哪個數值超限，而不是只有模糊字串。
- **驗證方法**： 用固定訊息建立測試，計算預期值時採與函式相同且公開的序列化定義；執行專注測試，確認函式不修改 messages。若將 helper 放入正式模組，再跑完整測試套件。
- **常見錯誤**： 把 Python `str(dict)` 字元數誤稱為 token 數；在計數函式內自動刪訊息；未定義等於上限的行為；只回傳 `False` 而無法診斷實際大小；破壞 ToolCall／ToolResult 配對。

## 第 5 章

### 練習 1：同步 Hook 只允許 Read、不允許 Bash，並證明被拒 Tool 未執行

- **解題方向**： 建立具 `called = False` 的 Bash 假工具，讓 FakeModel 先要求 Bash、再回傳最終訊息；同步 Hook 以 `return name == "read"` 決定允許。執行後同時斷言 `tool.called is False`，以及對應 ToolResult 的 `is_error is True`、content 含 safety hook 拒絕訊息。可另加 Read 假工具正向案例，避免 Hook 永遠回 False 也通過測試意圖。
- **起始狀態**： Loop 支援同步／非同步 Hook，拒絕會轉為 PermissionError 再成為錯誤 ToolResult。`tests/test_agent_controls.py::test_sync_safety_hook_can_block_tool` 已證明一般拒絕，但工具名稱是 `danger`，尚未呈現 Read-only 政策的正反兩例。
- **預期產物**： 一個不執行真實 shell 的測試，證明政策判斷、零副作用與可觀察錯誤結果；若加正向案例，Read 假工具應確實被呼叫。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_agent_controls.py -q`。驗收核心是 `called is False`，不是最終 Assistant 聲稱「已阻擋」。
- **常見錯誤**： 使用真實 BashTool 測拒絕；Hook 只記錄卻回 True；只看最後自然語言；把名稱比較寫成大小寫模糊允許；在 Hook 中自行呼叫工具。

### 練習 2：非同步 Hook 模擬 10 毫秒核准延遲，確認 Loop 會 await

- **解題方向**： 定義 `async def hook(...)`，先 `await asyncio.sleep(0.01)`，再設定可觀察旗標或把 `"approved"` 加入順序 list 並回 True；Tool 執行時加入 `"tool"`。執行 Loop 後斷言順序是 `approved`、`tool`。以順序與狀態證明 await，不要用總耗時作主要斷言。
- **起始狀態**： `run_agent_loop()` 會呼叫 Hook，使用 `inspect.isawaitable()` 判斷後 await；現有測試有同步順序與一個會取消的 async Hook，但沒有專門的 10 ms 核准案例。
- **預期產物**： 一個快速、無網路的 pytest-asyncio 測試，證明工具只能在非同步核准完成後執行。
- **驗證方法**： 執行新增測試；如果暫時移除 Hook 內的 `return True` 或讓它回 False，工具應不執行。正式斷言使用事件／旗標順序，10 ms 只用來模擬 await 點。
- **常見錯誤**： 呼叫 `asyncio.sleep(0.01)` 卻忘記 await；只斷言經過至少 10 ms，造成慢機或排程下的脆弱測試；在同步測試中直接呼叫 coroutine；核准前先改變 Tool 的 `called`。

### 練習 3：為無效 Config（`max_turns=0`、逾時 0、未知模式）加入失敗測試

- **解題方向**： 用三個小型同步測試或參數化測試，在建構 `AgentConfig` 當下使用 `pytest.raises(ValueError, match=...)`：`max_turns=0` 應匹配 `at least 1`，`tool_timeout_seconds=0` 應匹配 `positive`，未知 `tool_execution` 應匹配 `sequential or parallel`。
- **起始狀態**： `AgentConfig.__post_init__()` 已實作三項檢查，但目前讀到的測試未直接覆蓋這三個建構失敗案例。Config 是 frozen dataclass，錯誤在執行 Loop 之前即可發現。
- **預期產物**： 三個可精確定位欄位契約的單元測試；可再補負數回合、負逾時，但不要讓額外案例取代題目指定的三個值。
- **驗證方法**： 執行新增的 Config 測試，確認每個案例都在物件建構時拋出 ValueError。再執行 `uv run --extra test pytest tests/test_agent_controls.py -q`，確認合法 Config 的控制流程仍通過。
- **常見錯誤**： 建構 Config 後才期待 Loop 報錯；只測負數而漏掉零；接受任意字串後在 Loop 默認成 sequential；斷言整段完整錯誤文字導致無謂脆弱性。

## 第 6 章

### 練習 1（基礎）：補 `left="2"` 的數值型態失敗測試

- **解題方向**： 使用 `pytest.mark.asyncio` 與 `pytest.raises(TypeError, match="left and right must be numbers")` 呼叫 Calculator，arguments 為 `{"operation": "add", "left": "2", "right": 3}`。此題只驗證拒絕，不應加入自動字串轉數字。
- **起始狀態**： 目前 checkout 已在 `tests/test_calculator.py::test_calculator_rejects_non_numeric_operands` 完整實作此測試，Calculator 也會拋出指定 TypeError。因此不需要再新增重複測試；應先辨識題目要求已滿足。
- **預期產物**： 一筆通過的既有測試驗證紀錄；若在教學分支從頭實作，則是一個最小失敗路徑測試，且正式 Calculator 行為保持拒絕字串。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_calculator.py -q`，確認命令結束碼為 0。要練習 TDD 時，可在獨立分支先暫時移除型態檢查觀察測試失敗，再恢復；不要提交故意失敗版本。
- **常見錯誤**： 再加入一個完全重複的測試；把 `"2"` 轉為 2 而改變安全契約；只測右運算元且聲稱完成指定案例；捕捉過寬的 `Exception`。

### 練習 2（進階）：先寫失敗測試，再修改 Calculator 拒絕布林值

- **解題方向**： 先新增 `left=True` 應拋 TypeError 的測試並執行，確認目前它會失敗（因結果會被當成 1 加 3）。再把型態判斷改為同時要求是 int／float 且不是 bool；左右運算元都應套用相同規則。最後讓新測試與既有測試全部通過。
- **起始狀態**： Python 的 `bool` 是 `int` 子類；目前 Calculator 使用 `isinstance(value, (int, float))`，所以會接受 True／False。現有 `tests/test_calculator.py` 尚無布林值案例；本書也明確把這點列為已知限制。
- **預期產物**： 一個先紅後綠的布林拒絕測試，以及最小型態檢查修改。建議至少參數化測 `left=True` 與 `right=False`，錯誤契約沿用 `TypeError("left and right must be numbers")`。
- **驗證方法**： 保存或記錄第一次測試確實因「沒有拋 TypeError」而失敗；修改後執行 `uv run --extra test pytest tests/test_calculator.py -q`，再跑完整套件。可額外直接確認一般 int、float 仍成功。
- **常見錯誤**： 未先觀察紅燈就宣稱完成 TDD；用 `type(value) in (int, float)` 卻未評估是否刻意排除其他數值子類；只拒絕 left 不拒絕 right；誤報現有版本已經拒絕 bool。

### 練習 3（挑戰）：加入安全除法與完整測試

- **解題方向**： 明確將 `divide` 加入 `_operations` 的允許清單，建議對應 `operator.truediv`，不要解析字串或使用 `eval()`。先定義契約：例如 `8 / 2` 回傳 `{"result": 4.0}`、`3 / 2` 回傳 `{"result": 1.5}`，除數為 0 時保留 Python 的 `ZeroDivisionError` 與 `division by zero` 訊息，或自行轉成另一個已寫入測試的明確例外；兩種都可以，但程式與測試必須一致。
- **起始狀態**： Calculator 允許清單只有 add、subtract、multiply；`divide` 目前會拋 `ValueError("Unsupported operation: divide")`，既有測試正驗證這件事。加入 divide 後，該既有「未知操作」測試必須改用真正未知名稱，不能仍期待 divide 被拒絕。
- **預期產物**： Calculator 的一項 allowlist 擴充，以及至少四類測試：正常除法、可整除輸入、小數結果、除以零。若「正常除法」與另兩項重疊，仍應讓測試名稱清楚呈現題目要求；未知操作測試要繼續存在並改用例如 `power`。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_calculator.py -q`，再執行完整測試套件。另搜尋 Calculator 實作，確認沒有 `eval(` 或 `exec(`，且只有允許清單中的名稱能分派到函式。
- **常見錯誤**： 加入 divide 後忘記更新原本期待其失敗的測試；用整數除法 `floordiv` 導致 `3 / 2` 得到 1；對零偷偷回傳 Infinity 或字串而未定義契約；捕捉所有例外後偽裝成成功結果；為方便而使用 `eval()`。
## 第 7 章

### 練習 1：實作 `PingTool`

- **解題方向**： 在測試檔內先建立符合 `AgentTool` 結構式協定的 `PingTool`：提供非空的 `name = "ping"`、清楚的 `description`，以及非同步 `execute(tool_call_id, arguments)`。把它交給 `ToolRegistry`，再透過 `registry.execute()` 分派；不要直接呼叫 `PingTool.execute()`，否則沒有驗證 Registry 的責任。
- **起始狀態**： `src/mini_agent/tools/base.py` 已定義 `AgentTool` Protocol 與 `ToolRegistry`；專案目前沒有正式的 `PingTool` 類別。Protocol 採結構式子型別，因此不必繼承任何基底類別。
- **預期產物**： 一個回傳 `{"reply": "pong", "tool_call_id": tool_call_id}` 的最小工具，以及一個非同步測試，證明 `registry.execute("call-ping", "ping", {})` 保留原 call ID。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_tool_registry.py -q`；另外斷言 Registry 名稱包含 `ping`，且結果精確等於預期 dict。
- **常見錯誤**： 忘記 `async def`；直接呼叫工具而沒有經過 Registry；回傳固定 ID；為了符合 Protocol 強迫所有工具繼承基底類別；依賴 `set` 的顯示順序。

### 練習 2：補 Registry 邊界測試

- **解題方向**： 以三個獨立測試覆蓋空名稱、重複名稱、未知名稱；使用 `pytest.raises(..., match=...)` 比對可理解的錯誤。未知名稱應透過 `registry.execute()` 測試，證明錯誤發生在分派前。
- **起始狀態**： `ToolRegistry.register()` 會以 `ValueError("Tool name is required")` 拒絕空名稱，以 `ValueError("Duplicate tool name: ...")` 拒絕重複名稱；`get()` 會以 `KeyError("Unknown tool: ...")` 拒絕未知名稱。`tests/test_tool_registry.py` 目前已涵蓋這三個案例，可作為參考答案。
- **預期產物**： 三個各自只驗證一項邊界的測試；未知名稱案例不得讓任何替身工具的 `execute()` 被呼叫。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_tool_registry.py -q`。本次基線驗證中，此檔與第 7–12 章相關測試合併執行後通過。
- **常見錯誤**： 把三種錯誤塞進同一測試；只檢查例外型別、不檢查訊息；期待後註冊工具靜默覆蓋前一個；把 `KeyError` 的字串引號差異誤當成業務行為。

### 練習 3：產生模型工具描述

- **解題方向**： 先定義不可變且穩定的公開形狀，例如 `descriptions() -> tuple[dict[str, str], ...]`，每項只有 `name`、`description`，並以名稱排序。方法應建立新資料，不回傳 `_tools`，也不回傳可讓呼叫端改寫 Registry 的內部 dict。
- **起始狀態**： Registry 只有 `names() -> set[str]`；它刻意回傳副本，但沒有描述輸出 API，且 `_tools` 是內部可變字典。
- **預期產物**： 一個穩定排序的描述方法，以及測試：不同註冊順序得到相同輸出、資料形狀固定、呼叫端修改回傳容器不會改變 Registry。
- **驗證方法**： 先寫失敗測試，再加入最小實作；執行 `uv run --extra test pytest tests/test_tool_registry.py -q`。可額外重複呼叫兩次並精確比對結果，避免只看集合相等。
- **常見錯誤**： 直接回傳 `self._tools` 或其可變 view；把 dict/set 的偶然迭代順序當成契約；把供應商專屬 JSON Schema 硬塞進最小 Registry；讓描述方法同時修改註冊狀態。

## 第 8 章

### 練習 1：補空 ID 測試

- **解題方向**： 建立名稱與 arguments 都有效、只有 ID 無效的 `ToolCall`，分別測試 `""` 與只有空白的字串，期待 `ToolValidationError` 且訊息含 `id is required`。如此可避免前面的未知名稱或 arguments 檢查先失敗。
- **起始狀態**： `validate_tool_call()` 已以 `if not call.id.strip()` 拒絕兩種 ID；`tests/test_validation.py` 目前已有空字串與空白字串測試。
- **預期產物**： 兩個聚焦測試，證明無效 ID 在工具執行前被拒絕。不要宣稱錯誤結果能可靠配對：目前 Agent Loop 若沿用空 ID，只能稽核，不能建立可靠 ToolCall/ToolResult 對應。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_validation.py -q`；確認測試不是因未知工具先失敗。
- **常見錯誤**： 使用未知名稱導致測到錯誤的檢查分支；只測 `""`、漏掉空白；替模型捏造新 ID；把空 ID 的錯誤結果描述成可可靠配對。

### 練習 2：證明執行順序

- **解題方向**： 用共用 `order: list[str]` 記錄事件。允許案例讓 hook append `"hook"` 並回傳 `True`，工具 append `"tool"`；拒絕案例讓 hook 回傳 `False`，並確認工具完全未執行。
- **起始狀態**： `run_agent_loop()` 已依 `Validation → Safety Hook → Registry → Tool` 執行。`tests/test_agent_controls.py` 已有允許順序測試與拒絕時 `tool.called is False` 的測試。
- **預期產物**： 允許時 `order == ["hook", "tool"]`；拒絕時 `order == ["hook"]`，且產生 `is_error=True` 的結果。同步與非同步 hook 至少選一種清楚覆蓋，若兩者都支援則各補一例更完整。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_agent_controls.py::test_safety_hook_runs_before_tool_execution tests/test_agent_controls.py::test_sync_safety_hook_can_block_tool -q`。
- **常見錯誤**： 只檢查最後結果、沒有觀察順序；拒絕後仍先執行工具再回報錯誤；把政策判斷放進 Registry；用具有真實副作用的工具測試順序。

### 練習 3：加入選配 Schema 層

- **解題方向**： 保持 `AgentTool` 最小協定相容，可另定一個可選能力，例如工具若提供 `validate_arguments(arguments)` 就在 Safety Hook 前呼叫；或由獨立 `SchemaValidator` 對有 schema 的工具驗證。核心應使用 duck typing／額外 Protocol，而不是強迫所有工具安裝第三方套件。Schema 失敗應拋出明確的一般驗證例外，讓具有有效 ID 的呼叫被 Agent Loop 轉成 `ToolResultMessage(is_error=True)`。
- **起始狀態**： 共通 Validation 只檢查名稱、dict 外形、非空 ID；具體工具自行處理業務欄位，核心沒有 JSON Schema 相依套件。
- **預期產物**： 一個選配 schema 契約、至少一個有 schema 的工具、一個沒有 schema 的既有最小工具，以及測試：有效參數可執行、無效參數不執行工具且回傳可配對錯誤、無 schema 工具仍能註冊與執行。
- **驗證方法**： 執行新增的聚焦測試，再執行 `uv run --extra test pytest tests/test_validation.py tests/test_agent_controls.py tests/test_tool_registry.py -q`。最後可跑 `uv run --extra test python scripts/verify_all.py .` 檢查整體相容性。
- **常見錯誤**： 讓核心 import 非必要第三方 schema 套件；把 schema 驗證放在工具副作用之後；捕捉 `BaseException` 而誤吞取消；對無效 ID 仍宣稱錯誤可配對；讓 Registry 理解每個工具的業務欄位。

## 第 9 章

> **安全前提：** Workspace containment（解析後路徑位於根目錄內）不等於 relative-path enforcement（輸入格式必須是相對路徑）。目前 `ensure_workspace_path()` 會接受 Workspace 內的絕對路徑；若題目要強制相對路徑，必須另加 `Path(value).is_absolute()` 檢查。`resolve()`／`relative_to()` 也不是完整檔案沙箱，仍有符號連結 TOCTOU 等競態。

### 練習 1：不存在檔案

- **解題方向**： 使用 `tmp_path` 建立空 Workspace，呼叫 `ReadTool(tmp_path).execute(..., {"path": "missing.txt"})`，期待 `FileNotFoundError`。路徑必須位於 Workspace 內，才能只測「不存在」而非「越界」。
- **起始狀態**： `ReadTool` 先呼叫 `ensure_workspace_path()`，再以 UTF-8 `read_text()`；目前沒有專門的不存在檔案測試。
- **預期產物**： 一個非同步負向測試，證明 Workspace 內缺檔保留 `FileNotFoundError`，且沒有建立檔案或父目錄。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_tools.py -q`，並斷言目標仍不存在。必要時另跑 `tests/test_safety.py`，確保越界仍是不同的 `WorkspaceViolation`。
- **常見錯誤**： 使用 `../missing.txt` 而測到越界；為了讓測試通過自動建立空檔；把 `FileNotFoundError` 統一包成模糊 `ValueError`；誤稱工具只接受相對路徑。

### 練習 2：限制讀取量

- **解題方向**： 先定義 `max_bytes` 的來源與邊界，例如建構參數必須為正整數。不要先 `read_text()` 再檢查長度，因為全文已載入；可用 binary mode 最多讀 `max_bytes + 1` bytes，超過就關檔並拋出清楚錯誤，未超過再以 UTF-8 嚴格解碼。若只用 `stat().st_size`，需揭露檢查與讀取間的競態。
- **起始狀態**： 現有 `ReadTool` 會一次載入完整檔案，沒有大小上限。
- **預期產物**： 可設定的 `max_bytes`、剛好等於上限成功與超過一 byte 失敗的測試；超限結果不得包含截斷全文，並應維持 UTF-8 解碼錯誤可區分。
- **驗證方法**： 用暫存檔建立邊界資料；先觀察超限測試失敗，再實作並執行 `uv run --extra test pytest tests/test_tools.py tests/test_safety.py -q`。可用替身檔案物件或 monkeypatch 證明沒有無界限的 `read()`。
- **常見錯誤**： 讀完全文後才比較 bytes；用字元數代替 UTF-8 bytes；切在多位元字元中間後把解碼錯誤誤判成原檔壞掉；回傳部分內容卻沒有標示截斷；忽略檔案在檢查後變大的競態。

### 練習 3：行號範圍

- **解題方向**： 先固定契約，例如 `start_line` 採 1-based 正整數、`limit` 採非負整數；`start_line` 超過末行回傳空字串，空檔永遠回傳空字串，`limit=0` 回傳空字串。以逐行迭代或 `itertools.islice()` 讀取，避免為了小範圍先載入全文；同時決定是否保留原換行（建議保留）。
- **起始狀態**： `ReadTool` 只接受 `path` 並回傳全文，沒有行號參數。
- **預期產物**： 明確記錄參數語意與測試矩陣：第一行、中間範圍、超出末行、空檔、無結尾換行、`limit=0`、負值／零起始行。
- **驗證方法**： 對每個案例精確比對字串；執行新增聚焦測試與 `uv run --extra test pytest tests/test_tools.py tests/test_safety.py -q`。若 `max_bytes` 與行範圍同時存在，另測兩者的優先順序。
- **常見錯誤**： 0-based 與 1-based 混用；`splitlines()` 遺失換行；把超出範圍錯誤與空結果語意混在一起；行號功能繞過 Workspace 驗證；仍先讀取全文。

## 第 10 章

> **安全前提：** Write 共用的 Workspace 檢查只保證解析後目標受根目錄包含，不強制輸入必須是相對路徑；Workspace 內絕對路徑目前會通過。所有路徑與政策檢查都必須發生在建立目錄、暫存檔或覆寫之前。

### 練習 1：bytes 測試

- **解題方向**： 選用含中文的內容，呼叫 `WriteTool` 後，將回傳的 `bytes` 與 `len(content.encode("utf-8"))` 精確比較，再讀回原文。不要把 `len(content)` 當 bytes。
- **起始狀態**： 現有 `WriteTool` 已以 UTF-8 寫入，並以編碼後長度回報 bytes；現有 `tests/test_tools.py` 尚未直接驗證中文 bytes。
- **預期產物**： 一個非同步測試，同時證明回傳路徑、UTF-8 bytes 與磁碟內容正確。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_tools.py -q`；斷言 `result == {"path": ..., "bytes": len(content.encode("utf-8"))}`，並以 `read_text(encoding="utf-8")` 讀回。
- **常見錯誤**： 用字元數當 bytes；依賴平台預設編碼；只檢查工具沒有拋例外、未讀回；硬編一個與測試內容脫鉤的 bytes 常數。

### 練習 2：條件覆寫

- **解題方向**： 先決定參數預設：題意可採 `overwrite=False` 為安全預設。既有目標且不允許覆寫時，在任何寫入前拋出 `FileExistsError` 或專用清楚錯誤，並確認原文不變。若要降低「先 exists 再 write」競態，可在禁止覆寫模式使用 exclusive create（`x` 模式）；單純 `exists()` 不是原子保證。
- **起始狀態**： 現有 `Path.write_text()` 會無條件覆寫既有檔案，也會先建立父目錄。
- **預期產物**： `overwrite` 契約與測試：新檔成功、既有檔在預設／False 時拒絕且不變、明確 True 時可覆寫。越界路徑仍須在任何父目錄副作用前拒絕。
- **驗證方法**： 先建立含 sentinel 內容的檔案，呼叫拒絕案例後重新讀回 sentinel；執行 `uv run --extra test pytest tests/test_tools.py tests/test_safety.py -q`。
- **常見錯誤**： 先清空檔案再檢查；拒絕後原檔已變；把工具能力的 `overwrite=True` 當成政策已核准；只做 `exists()` 卻宣稱完全沒有競態；為越界目標先建立目錄。

### 練習 3：原子寫入

- **解題方向**： 在目標的同一父目錄建立具唯一名稱的暫存檔，寫入 UTF-8、flush，必要時 `os.fsync()`，最後以 `os.replace()` 提交；同目錄可避免跨檔案系統替換問題。用 `try/finally` 在提交前失敗時清除暫存檔。原子替換只保證讀者看到舊版或新版，不等於多檔交易，也不自動保留權限／metadata。
- **起始狀態**： 現有 `write_text()` 直接寫目標，途中失敗可能留下部分內容。
- **預期產物**： 同目錄暫存＋原子替換實作，以及成功、寫入失敗、replace 失敗的測試；失敗時舊目標保持原內容，暫存檔被清理。
- **驗證方法**： monkeypatch 寫入或 `os.replace` 讓提交前失敗，確認 sentinel 原檔不變且目錄無殘留暫存檔；成功案例再以 Read 驗證。執行 `uv run --extra test pytest tests/test_tools.py tests/test_safety.py -q`。
- **常見錯誤**： 暫存檔放在系統 `/tmp` 導致跨檔案系統 replace；失敗後遺留暫存檔；先刪目標再 rename；把單檔原子替換誤稱為 durable transaction；暫存檔路徑未受 Workspace 邊界控制。

## 第 11 章

> **安全前提：** Edit 目前的 Workspace containment 不強制 relative-path 格式；Workspace 內絕對路徑仍可通過。另有關鍵 empty-old edge：一般非空檔的 `text.count("")` 會大於一而被拒絕，但空檔的 `"".count("") == 1`，現行實作會把 `new` 插入空檔並誤報成功；必須明確修正，不能說目前已安全拒絕所有空 `old`。

### 練習 1：負向測試

- **解題方向**： 用參數化測試或兩個獨立案例建立零匹配與兩次匹配；呼叫前保存原文，期待 `ValueError` 的匹配數分別為 0、2，呼叫後重新讀檔並精確比較原文。
- **起始狀態**： `EditTool` 已要求 `count == 1`，但 `tests/test_tools.py` 目前只覆蓋唯一匹配成功案例。
- **預期產物**： 兩個失敗案例，證明錯誤不只是被拋出，而且檔案沒有被改動。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_tools.py -q`；斷言錯誤訊息與原文。多匹配案例應使用完全相同的 `old` 出現兩次。
- **常見錯誤**： 只測例外、未讀回原檔；讓兩次匹配其實因空白差異只匹配一次；失敗後自動退回模糊比對；測試零匹配時誤用空 `old`，混入另一個漏洞。

### 練習 2：拒絕空 `old`

- **解題方向**： 先以空檔建立必然失敗的回歸測試：`old=""`、`new="injected"` 必須拋出清楚錯誤且空檔仍空。然後在 `count()` 與任何寫入之前加入明確型別／非空檢查，例如 `if not isinstance(old, str) or old == "": raise ValueError("old must be a non-empty string")`。
- **起始狀態**： 現行程式沒有顯式空值檢查；空檔會因 `"".count("") == 1` 通過唯一匹配條件並插入新內容。這是已知且目前存在的 edge，不可省略。
- **預期產物**： 一個可重現現行漏洞的失敗測試、最小防護實作，以及空檔／非空檔都拒絕空 `old` 且內容不變的測試。
- **驗證方法**： 先在未修正程式觀察測試失敗，再修正並執行 `uv run --extra test pytest tests/test_tools.py -q`。同時保留唯一非空匹配成功與零／多匹配失敗案例。
- **常見錯誤**： 只依賴 `count != 1`；只測非空檔，因此測試雖通過卻漏掉空檔；檢查放在寫回之後；把空白字串是否允許與空字串混為一談而未定義契約。

### 練習 3：多檔交易

- **解題方向**： 分成 prepare 與 commit：prepare 階段先解析並驗證所有 Workspace 路徑、讀取快照、驗證每個非空 `old` 恰好唯一匹配、計算新內容，任何一項失敗都不寫檔；commit 階段為每個目標建立同目錄暫存檔，再替換。若替換到一半失敗，要以原始 bytes／備份回滾已提交項目，並報告回滾是否完整。多檔原子性無法只靠多次 `os.replace()` 保證，正式需求宜使用版本控制、資料庫交易或更強協調機制。
- **起始狀態**： `EditTool` 只處理單檔，沒有鎖、交易、備份或回滾，且寫回不是原子操作。
- **預期產物**： 一份明確交易狀態設計與測試：前置條件失敗時零寫入；全部成功時全數更新；第 N 次提交失敗時已提交檔案回復、未提交檔案不變、暫存與備份被清理或明確保留供復原。
- **驗證方法**： 以 monkeypatch 讓第二次 `os.replace()` 失敗，逐檔比對交易前內容；再執行完整成功案例。聚焦測試通過後跑 `uv run --extra test pytest tests/test_tools.py tests/test_safety.py -q`。
- **常見錯誤**： 驗證一檔就立刻寫一檔；把多次原子 rename 誤稱為整批原子交易；回滾資料只存在於被覆寫的目標；路徑別名／重複目標未去重；回滾失敗被靜默吞掉。

## 第 12 章

> **安全前提：** 目前 `BashTool` 不是 sandbox。固定 `cwd` 不限制絕對路徑、網路或 Workspace 外讀寫；現行 `shell=True` 路徑已有 bypass：`echo $(pwd)` 的 `$()`、命令中的換行、`cat /etc/hostname`，以及 `python3 -c ...` 都可穿過目前限制或取得過廣能力。逾時目前只 kill/wait shell 行程，不保證清除整棵衍生行程樹。以下改進不能被描述成「安全執行任意 Bash」。

### 練習 1：未知命令

- **解題方向**： 以 `tmp_path` 建立工具，呼叫 `{"command": "pytest -q"}`，期待 `PermissionError` 且訊息指出 `pytest` 不在 allowlist。若要證明啟動前拒絕，可 monkeypatch subprocess 建立函式並斷言沒有被呼叫。
- **起始狀態**： allowlist 只有 `cat`、`echo`、`ls`、`pwd`、`python3`、`sleep`；現有 `tests/test_bash_tool.py` 尚未直接測 `pytest -q`。
- **預期產物**： 一個非同步測試，證明未知 executable 在建立子行程前 fail closed。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_bash_tool.py -q`；比對 `Command is not allowed: pytest`，並確認沒有任何 Workspace 副作用。
- **常見錯誤**： 只看 command 是否含 allowlist 子字串；把 `pytest` 加入 allowlist 讓測試通過；實際啟動後才拒絕；把 allowlist 誤稱為 sandbox。

### 練習 2：結構化 argv

- **解題方向**： 最清楚的契約是把輸入改成 `{"argv": ["echo", "hello world"]}`，驗證為非空 `list[str]`、每項無 NUL，並以 `create_subprocess_exec(*argv, cwd=..., stdout=PIPE, stderr=PIPE)` 執行；不要把陣列重新 join 成 shell 字串。若為相容舊 `command` 使用 `shlex.split()`，需明確說明平台與 quoting 語意，且仍應盡快移除模糊雙介面。
- **起始狀態**： 現行工具接受單一 command 字串，使用 `create_subprocess_shell()` 加正規表示式阻擋部分字元；這同時漏擋與誤擋。
- **預期產物**： 結構化 argv 介面、更新的 executable allowlist 檢查、保留 stdout/stderr/returncode 與逾時處理的實作；測試 `['echo', 'hello world']` 證明含空格內容仍是一個參數，另測空 argv、非字串項目與 NUL。
- **驗證方法**： 執行 `uv run --extra test pytest tests/test_bash_tool.py -q`；額外測試 argv 中的 `";"` 只是傳給 executable 的資料而不會啟動第二個命令。逾時測試仍須通過，但應再次揭露行程樹清理限制。
- **常見錯誤**： `" ".join(argv)` 後仍用 shell；自行拼接引號；把 shell metacharacter regex 原封不動套在每個資料參數造成不必要誤拒；以為移除 shell 就限制了 `python3`、絕對路徑或網路能力；忽略 Windows/POSIX 差異。

### 練習 3：命令政策

- **解題方向**： 先從能力最小化出發；若沒有必要，移除 `python3` 最安全。若必須保留，為 argv 定義可稽核規則，例如只允許執行 Workspace 內特定腳本、拒絕 `-c`、`-m`、stdin 程式 `-`、啟動旗標與 Workspace 外 script path，並限制後續參數、環境、輸出與逾時。政策檢查應以解析後 argv 運作，不以字串包含判斷。
- **起始狀態**： 現行政策只檢查第一個 token 是否為 `python3`；因此 `python3 -c ...` 可任意執行 Python，固定 `cwd` 也不能阻止它讀寫 Workspace 外或連網。
- **預期產物**： 一個明確 allow-by-construction 的 Python argv 規格與測試表：允許的 Workspace 腳本成功；`-c`、`-m`、`-`、外部絕對路徑、越界 `../`、符號連結逃逸與不允許旗標全部在啟動前拒絕。說明必須聲明參數政策仍不是 OS sandbox。
- **驗證方法**： 對每個拒絕案例 monkeypatch subprocess 並確認未啟動；允許案例只執行無副作用的暫存 Workspace 腳本。執行 `uv run --extra test pytest tests/test_bash_tool.py -q`，再在可用隔離環境跑完整驗證入口。
- **常見錯誤**： 只封鎖字面 `"-c"`，可由其他 Python 啟動模式繞過；只驗證 script 字串含 Workspace 名稱、不做解析後包含檢查；允許任意環境變數、site customization 或可寫 import path；聲稱 executable allowlist、固定 `cwd` 或 argv 已構成 sandbox；忽略現行 `$()`、換行、絕對路徑與衍生行程樹等已知 bypass／限制。

## 第 13 章

### 練習 1：基礎：最大回合

- **解題方向**：沿用 `tests/test_agent_controls.py` 的最小工具，讓 `FakeModel` 每次都回傳含 ToolCall 的 `AssistantMessage`，並把 `AgentConfig(max_turns=1)` 傳入 `run_agent_loop()`。用 `pytest.raises(RuntimeError, match="maximum turns")` 驗證保護性停止；另外斷言 `len(model.calls) == 1`，說明 `max_turns` 計算模型回合，不是工具數。
- **起始狀態**：`tests/test_agent_controls.py::test_agent_stops_at_max_turns`、`src/mini_agent/agent_loop.py`，以及一個只回傳固定值、沒有副作用的替身工具。
- **預期產物**：一個非同步測試，證明最後允許回合的 AssistantMessage 與工具結果可以先進入 history，但 Loop 不會開始第二次模型呼叫，最後拋出 `RuntimeError`。
- **驗證方法**：執行 `uv run --extra test pytest tests/test_agent_controls.py::test_agent_stops_at_max_turns -q`；測試須通過，且錯誤訊息含 `maximum turns`。
- **常見錯誤**：只準備一個無 ToolCall 的最終回答，導致 Loop 正常結束；把 `max_turns` 誤當工具呼叫上限；期待函式在達上限時回傳 history 而不是拋出例外。

### 練習 2：進階：錯誤恢復

- **解題方向**：建立第一次 `execute()` 會拋出 `ValueError("broken")` 的工具，再讓 `FakeModel` 依序回傳 ToolCall 與修正後最終回答。檢查中間的 `ToolResultMessage` 保留原 call ID、工具名稱、錯誤文字與 `is_error=True`，並確認該錯誤結果出現在第二次 `model.complete()` 收到的 Context 中。
- **起始狀態**：`tests/test_cancellation.py::test_tool_events_always_have_matching_end_event_on_failure`、`tests/test_agent_loop.py` 與 `FakeModel.calls`。
- **預期產物**：一個兩回合測試；history 順序為使用者訊息、工具請求、錯誤結果、修正後 AssistantMessage，且 `len(model.calls) == 2`。
- **驗證方法**：執行新增測試所在檔案；斷言錯誤結果的 `tool_call_id`、`is_error` 與內容，並斷言 `model.calls[1]` 含相同 call ID 的 tool 訊息。
- **常見錯誤**：讓工具自行吞掉例外而無法測到 Loop 的錯誤轉換；把可恢復錯誤當成取消；未設合理 `max_turns`，把「可修正」寫成無限重試。

### 練習 3：挑戰：回合事件

- **解題方向**：先定義契約，再擴充 `AgentEvent` 收集：每次通過回合起始取消檢查後加入 `turn_start`（含 turn number），並以 `try/finally` 或明確分支加入帶狀態的 `turn_end`。正常完成可用 `status="completed"`，截斷用 `status="truncated"`，最大回合用 `status="max_turns"`；取消若發生在已開始回合內，收尾用 `status="cancelled"` 後重新拋出 `AgentCancelled`。取消若在 `turn_start` 前已被偵測，則不應憑空產生一對回合事件。
- **起始狀態**：`src/mini_agent/agent_loop.py`、`src/mini_agent/events.py`、`tests/test_agent_controls.py` 與 `tests/test_cancellation.py`。目前 `events` 是呼叫端傳入的 list collector。
- **預期產物**：回合事件契約及正常、截斷、取消、最大回合四組測試；事件 payload 至少包含 `turn` 與收尾 `status`。本題仍是事件列表收集，不是即時串流 API。
- **驗證方法**：逐案比對事件 type、turn number 與 status；取消案例還須斷言 `AgentCancelled` 向外傳遞、工具及下一模型回合未開始；截斷案例須斷言工具未執行。
- **常見錯誤**：把 list 誤稱為 streaming；用一般 `except Exception` 吞掉 `AgentCancelled`；每個 return/raise 分支各自 append，造成重複 `turn_end`；改變既有前置拒絕可能只產生未配對 `tool_end` 的限制卻未同步更新契約與測試。

## 第 14 章

### 練習 1：基礎：CLI renderer

- **解題方向**：在 UI／範例層新增純函式 `render_event(event) -> str | None`，依 `event.type` 將 `tool_start`、`tool_end` 轉成單行文字，並顯示工具名稱與 call ID；未知事件回傳 `None`。核心 Loop 只收集資料，不直接 `print()`。
- **起始狀態**：`examples/v06_event_consumer.py` 的 `render()`、`src/mini_agent/events.py` 與 `tests/test_v06_event_consumer.py`。
- **預期產物**：renderer 與單元測試，例如 `開始：read (call-1)`、`結束：read (call-1)`；輸出端自行忽略 `None`。
- **驗證方法**：對 start、end、未知 type 各做斷言，再執行 `uv run python examples/v06_event_consumer.py`，確認工具結果成功且輸出含成對事件。
- **常見錯誤**：在 `run_agent_loop()` 內 print；只顯示工具名稱而省略 call ID；把有 start 才接受 end 寫死。現況中 Validation、Hook 或取消等前置拒絕可能只有 `tool_end`，renderer 必須能獨立呈現。

### 練習 2：進階：回合事件

- **解題方向**：以第 13 章定義的 `turn_start`／`turn_end` 契約加入從 1 開始的 turn number。正常回答應是一組 start/end；持續要求工具且 `max_turns=1` 時，也要有第一回合的 start/end，收尾狀態標示達上限，而不是製造不存在的第二回合。
- **起始狀態**：完成第 13 章第 3 題後的 Loop、`tests/test_agent_controls.py::test_agent_stops_at_max_turns` 與 `FakeModel.calls`。
- **預期產物**：正常完成與最大回合兩個事件序列測試，能用 turn number 配對，不依賴 list 中的相鄰位置。
- **驗證方法**：正常案例斷言只有 turn 1；上限案例斷言 `RuntimeError`、只有 turn 1、`len(model.calls) == 1`，且 start/end payload 的 turn 相同。
- **常見錯誤**：用零起算內部索引直接當公開 turn number；在 `RuntimeError` 拋出後才嘗試補事件；把模型回合數與該回合工具數混為一談。

### 練習 3：挑戰：事件串流

- **解題方向**：把這題當成「設計與原型」，不要宣稱目前核心已具串流能力。可設計有界 `asyncio.Queue[AgentEvent | Sentinel]`：生產端採非阻塞投遞、獨立 relay task 或明確丟棄／合併政策，消費端用 async iterator 讀取；定義 queue 滿載時的背壓策略、結束 sentinel、消費端取消後的 task 清理，以及哪些稽核事件絕不可丟棄。
- **起始狀態**：目前的 `events: list[AgentEvent]` collector 與 V6 消費端；另建隔離的實驗模組與測試，不必立刻替換穩定 API。
- **預期產物**：一份事件通道介面、最小 queue 原型，以及快生產／慢消費、消費端取消、正常關閉三組非同步測試。說明需明確指出 list collector 仍非 streaming。
- **驗證方法**：用容量很小的 queue 和 `asyncio.Event` 控制時序，避免以任意 sleep 判定；測試結束後檢查 producer、relay、consumer task 都已完成或取消，且沒有 pending task。
- **常見錯誤**：直接 `await queue.put()` 讓慢 UI 阻塞工具；使用無界 queue 逃避背壓；取消 consumer 後留下 producer；把模型 token delta 與工具狀態事件混成沒有版本的 payload。

## 第 15 章

### 練習 1：基礎：延遲工具

- **解題方向**：交換原範例的延遲，或建立 A 很快、B 很慢的工具，但保持 ToolCall 傳入順序不變。平行執行後檢查 ToolResult list 仍按 A、B 排列；真正要驗證的是 `asyncio.gather()` 的結果契約，不是作業系統實際完成時序。
- **起始狀態**：`tests/test_agent_controls.py::test_parallel_tool_results_keep_model_call_order` 與 `examples/v07_parallel_order.py`。
- **預期產物**：一個不依賴排程偶然性的測試，斷言結果內容及 call ID 都維持模型原始順序。
- **驗證方法**：執行 `uv run --extra test pytest tests/test_agent_controls.py::test_parallel_tool_results_keep_model_call_order -q` 與 `uv run python examples/v07_parallel_order.py`；交換延遲後斷言仍按 ToolCall 順序。
- **常見錯誤**：把「先完成」當成「先回傳」；只檢查內容、不檢查 call ID；用極短 sleep 推論完成順序，造成測試偶發失敗。

### 練習 2：進階：資源分類

- **解題方向**：不要只按工具名稱分類，應把每次呼叫抽象成讀集合 R、寫集合 W 與外部副作用。Read：R={正規化目標路徑}；Write：W={目標路徑及必要父目錄}；Edit：R/W={同一目標路徑}；Bash：必須由 argv 與工作目錄保守推導，無法判定時視為可讀寫 Workspace／外部狀態。兩個呼叫只有在 `W1` 不與 `R2∪W2` 相交、`W2` 不與 `R1∪W1` 相交，且 Hook／配額等共享狀態可並行時，才考慮 parallel。
- **起始狀態**：第 9～12 章工具契約、`ensure_workspace_path()` 與第 15 章決策表。
- **預期產物**：Read、Write、Edit、Bash 的讀寫集合表，以及至少 Read(A)+Read(B)、Write(A)+Read(A)、Write(A)+Edit(A)、兩個未知 Bash 的模式判定與理由。
- **驗證方法**：用表格逐案套用衝突公式；含資料相依或同資源寫入者必須選 sequential（或先新增鎖／交易控制），互不相依的純讀取才可標示 parallel 候選。
- **常見錯誤**：認為不同工具名稱必然無相依；忽略路徑正規化、父子路徑及符號連結；把 sequential 誤解為模型能在同一 AssistantMessage 的兩個 call 中間重新決策。

### 練習 3：挑戰：檔案鎖

- **解題方向**：建立由正規化絕對路徑到 `asyncio.Lock` 的 lock manager；先用 `ensure_workspace_path()` 解析目標，再取得該路徑的鎖，並以 `async with` 包住完整讀改寫區段。若一次操作需要多把鎖，先將路徑排序後依固定順序取得，避免死鎖；鎖表本身的建立也要避免競態。
- **起始狀態**：暫存 Workspace、`src/mini_agent/safety.py`、Write/Edit 工具及平行工具測試模式。
- **預期產物**：path lock manager、同一路徑序列化測試與不同路徑可重疊測試；測試不得修改真實專案檔案。
- **驗證方法**：用 `asyncio.Event`／計數器證明同一路徑臨界區的最大同時進入數為 1，不同路徑則可大於 1；再確認最終檔案內容完整且沒有 lost update。
- **常見錯誤**：以未正規化字串當 key，使 `a/../b` 與 `b` 使用不同鎖；只鎖 write、不鎖 Edit 的 read-modify-write；多鎖取得順序不固定；無限保留 lock key 造成記憶體成長。

## 第 16 章

### 練習 1：基礎：取消理由

- **解題方向**：建立 `CancellationToken`，呼叫 `token.cancel("operator stop")`，再用 `pytest.raises(AgentCancelled)` 捕捉 `raise_if_cancelled()`；同時斷言 `exc.value.reason == "operator stop"` 與 `str(exc.value) == "operator stop"`。
- **起始狀態**：`src/mini_agent/cancellation.py` 與 `tests/test_cancellation.py`。
- **預期產物**：一個同步單元測試，證明自訂理由從 token 傳入例外且沒有被預設文字覆蓋。
- **驗證方法**：執行新增測試；再執行 `uv run --extra test pytest tests/test_cancellation.py -q`，既有 Loop 取消測試也須保持通過。
- **常見錯誤**：只用 regex 比對例外而未檢查 `.reason`；取消後又建立新 token；把 `AgentCancelled` 包裝成 `ToolResultMessage(is_error=True)`。

### 練習 2：進階：可取消工具

- **解題方向**：實作分段工具，每段開始前呼叫 `token.raise_if_cancelled()`，工作本身使用可取消的 await；測試以 `asyncio.Event` 確認第一段完成後再取消，避免靠 sleep 猜時序。這是合作式取消：只有抵達檢查點才停止，不能宣稱能強制中斷任意同步程式。
- **起始狀態**：`CancellationToken`、一個無外部副作用的分段替身工具，以及非同步測試環境。
- **預期產物**：可注入 token 的工具與測試；取消後後續段落不執行，`AgentCancelled.reason` 保留，所有 task 都被 await／清理。
- **驗證方法**：記錄完成的段號，取消後預期只有已完成段落；以 `pytest.raises(AgentCancelled)` 驗證向外傳遞，並確認沒有下一段副作用或背景 task。
- **常見錯誤**：只在工具入口檢查一次；在長時間同步迴圈內沒有檢查點；捕捉 `BaseException` 後吞掉取消；把合作式取消誤寫成強制終止保證。

### 練習 3：挑戰：冪等恢復

- **解題方向**：為每個外部寫入建立穩定 `operation_id`，在執行前查詢持久化紀錄；已成功者直接回傳先前結果，未完成者才執行。紀錄至少包含 operation ID、請求摘要／雜湊、狀態與結果；同一 ID 配不同 payload 必須拒絕。針對「副作用已成功但成功紀錄尚未寫入」的裂縫，優先使用外部服務原生 idempotency key 或同一交易，並明確記錄仍無法完全解決的情況。
- **起始狀態**：隔離的 fake external writer、暫存 SQLite／檔案紀錄與可模擬 crash 的測試；目前專案只有記憶體 history，沒有 durable recovery。
- **預期產物**：冪等寫入介面、operation record schema、重送相同操作不重複副作用的測試，以及失敗視窗說明。
- **驗證方法**：連續兩次提交相同 ID 與相同 payload，外部 writer 計數須為 1 且結果一致；相同 ID／不同 payload 須失敗；模擬重啟後重新載入紀錄再測一次。
- **常見錯誤**：每次重試都產生新 ID；只把 ID 放在記憶體 dict；在副作用之後才建立任何紀錄卻宣稱 exactly-once；把保留 history 誤稱為持久化恢復。

## 第 17 章

### 練習 1：基礎：唯讀 Hook

- **解題方向**：實作同步或非同步 allowlist Hook，將工具名稱正規契約限定為 `{"calculator", "read"}`，其他名稱一律 False。用帶 `called` 旗標的 Write/Edit/Bash 替身逐一證明拒絕發生在工具執行前；允許案例則證明 Calculator/Read 可到達工具。
- **起始狀態**：`tests/test_agent_controls.py` 的 Safety Hook 測試、`run_agent_loop(before_tool_call=...)` 與暫存 Workspace。
- **預期產物**：fail-closed 的唯讀 Hook 與參數化測試；被拒呼叫產生 `ToolResultMessage(is_error=True)`，且工具 `called is False`。
- **驗證方法**：執行 Hook 測試並斷言允許／拒絕矩陣、呼叫順序 `hook` 在 `tool` 前，以及拒絕後模型可看到錯誤結果。注意 Hook 是選配；必須由組裝根實際注入才有此政策。
- **常見錯誤**：以「不在 denylist」視為允許；使用 `Calculator`／`Read` 類別名稱而非 Registry 的小寫工具名稱；以提示詞代替 Hook；假設未傳 Hook 時核心預設拒絕。

### 練習 2：進階：敏感路徑

- **解題方向**：先寫負向測試，再建立集中式路徑政策。先以 `ensure_workspace_path()` 正規化並確認未逃離 Workspace，再檢查相對路徑的每個 component：拒絕 `.git` 目錄、檔名 `.env` 及其明確變體政策、私鑰副檔名（例如 `.pem`、`.key`）；對符號連結使用解析後目標做相同邊界檢查。Read、Write、Edit 都應共用政策，而不是只擋 Read。
- **起始狀態**：`src/mini_agent/safety.py`、`tests/test_safety.py` 與 `tmp_path`。先決定大小寫、`.env.local`、隱藏目錄與 symlink 的書面契約。
- **預期產物**：敏感路徑判定函式與參數化負向測試，另有一般檔案正向測試；拒絕必須發生在開檔或寫入前。
- **驗證方法**：至少測 `.env`、`.git/config`、`keys/server.pem`、`id.key`、`../outside`、指向 Workspace 外的 symlink，以及 `src/main.py`；負向案例全部拋出政策例外且未產生／讀取檔案。
- **常見錯誤**：用簡單 substring 導致 `environment.py` 誤判；只檢查原始字串、不解析 `..` 或 symlink；把「位於 Workspace 內」等同「可安全送給模型」；錯誤訊息洩漏秘密內容。

### 練習 3：挑戰：Context 壓縮

- **解題方向**：先把訊息切成不可拆的邏輯單位：含 ToolCall 的 AssistantMessage 必須與其所有 `tool_call_id` 對應 ToolResult 一起保留；未配對 call 一律釘選。另釘選最新使用者要求、最近副作用證據與政策拒絕。只對較舊、已完整配對、沒有必要副作用證據的區段產生摘要，並在壓縮後重新做 call ID 完整性檢查。
- **起始狀態**：`src/mini_agent/context.py`、`src/mini_agent/messages.py` 與獨立測試模組。正文的 `within_context_budget()` 只是教學決策函式，尚未存在於來源碼，也尚未整合核心 Loop。
- **預期產物**：摘要演算法設計、純函式原型與測試；輸出可符合訊息數／字元預算，但若必要釘選資料本身超出預算，應明確回報無法壓縮，不可默默刪除證據。
- **驗證方法**：建構多組交錯 ToolCall、ToolResult、錯誤結果與最近 Write/Edit 證據；壓縮後集合比較每個保留 call ID 的 request/result 都存在，最近副作用仍可辨識，最新需求未變，並測試「必要資料超預算」分支。
- **常見錯誤**：按單一訊息切尾，拆散 ToolCall／ToolResult；只算 `str(message)` 後宣稱精準 token 預算；摘要掉政策拒絕或最近寫入；把本題方案寫成目前產品已實作的 Context budget／壓縮功能。

## 第 18 章

### 練習 1：基礎：版本回顧

- **解題方向**：依 manifest／驗證腳本實際執行 V0～V10，再為每版各記錄一項已觀察能力與一項仍存在的安全邊界。能力要由輸出或測試支持，例如 V7 是結果順序穩定；邊界要具體，例如 V10 只註冊 Write/Edit/Read 且仍由 FakeModel 驅動。
- **起始狀態**：`examples/v00_*.py` 至 `examples/v10_complete_agent.py`、`scripts/verify_examples.py` 與第 18 章版本表。
- **預期產物**：11 列版本回顧表，欄位至少含版本、能力、證據、安全邊界；不得把後續版本能力倒填到較早版本。
- **驗證方法**：執行 `uv run python scripts/verify_examples.py .`，所有版本 return code 與輸出均符合 manifest；再抽查表中每項能力能對應實際程式或輸出。V10 預期仍是 FakeModel-only 的確定性整合範例，不是真實模型展示。
- **常見錯誤**：只閱讀檔名而未執行；把 V10 寫成已支援供應商網路模型、完整串流、Context 壓縮或 Bash；把一次成功輸出誤當所有錯誤與取消路徑都已展示。

### 練習 2：進階：ListFilesTool

- **解題方向**：建立只接受 Workspace 相對起點的工具，先用 `ensure_workspace_path()` 驗證起點，再遍歷檔案。回傳值只包含相對於 Workspace 的 POSIX 路徑並做穩定排序；為 symlink 訂 fail-closed 契約，例如完全拒絕或不追蹤，尤其不可列出指向根目錄外的內容。先寫 `..`、絕對路徑、外部 symlink、排序與空目錄測試。
- **起始狀態**：`src/mini_agent/tools/file_tools.py`、`src/mini_agent/safety.py`、`ToolRegistry` 與 `tmp_path` 暫存 Workspace。
- **預期產物**：符合 `AgentTool` 協定的 `ListFilesTool`、匯出／註冊調整（若正式加入套件）與完整工具測試；結果不得含 Workspace 絕對路徑。
- **驗證方法**：建立巢狀檔案並以非排序順序寫入，斷言回傳如 `['a.txt', 'src/b.py']`；`..`、絕對路徑與外部 symlink 必須拒絕或依書面政策安全略過，重複執行結果一致。
- **常見錯誤**：直接回傳 `Path.rglob()` 的絕對路徑；排序依賴檔案系統列舉順序；遍歷 symlink 逃出 Workspace；把檔名內容當成模型指令而非不可信資料。

### 練習 3：挑戰：Model Adapter

- **解題方向**：在 Adapter 邊界實作 `ModelClient.complete(context) -> AssistantMessage`：明確組裝供應商 system prompt／messages／tool schema，解析文字、ToolCall、finish reason 與 usage，將供應商的截斷原因映射為核心 `stop_reason="length"`。重試只涵蓋明確可重試且尚未造成不可判定副作用的網路錯誤，使用上限與 backoff；畸形或重複 call ID 應在 Adapter／Validation 邊界拒絕。API Key 只從呼叫端設定注入，不放進 Context、工具或日誌。
- **起始狀態**：`ModelClient` Protocol、`AssistantMessage`／`ToolCall`、Fake transport fixture 與供應商 payload 樣本。核心 Loop 與既有測試保持不變。
- **預期產物**：Adapter、transport 抽象或 mock、正常文字、工具呼叫、截斷、畸形 payload、rate limit／重試上限等單元測試，以及格式轉換與秘密處理說明。
- **驗證方法**：所有 Adapter 測試使用 fake HTTP transport，不連網、不需要 API Key；再執行 `uv run --extra test python scripts/verify_all.py .`，既有核心 FakeModel 測試與 V0～V10 全部維持通過。可另做需明確 opt-in 的真實服務 smoke test，但不得成為核心驗收必要條件。
- **常見錯誤**：在核心 Loop 直接寫供應商欄位；測試依賴真實網路或秘密；忽略 finish reason，讓截斷 ToolCall 被執行；無上限重試；宣稱 V10 已改用真實 Adapter。V10 的出版範例應維持 FakeModel-only。
