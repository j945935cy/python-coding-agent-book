# 11. Edit：精確修改程式碼

## 本章目標

建立比整檔覆寫更安全的精確修改工具，避免模型產生完整檔案時遺失未涉及的內容。

## 唯一匹配是安全邊界

`EditTool` 要求 `old` 文字在檔案中剛好出現一次。零次代表模型提供的上下文已過時，多次代表修改範圍不夠精確；兩者都應停止，而不是猜測要改哪一處。

```python
async def demo(edit):
    await edit.execute(
        "call-1",
        {
            "path": "src/hello.py",
            "old": "print('hello')",
            "new": "print('hello, agent')",
        },
    )
```

結果回傳 `replacements: 1`。這個欄位是可觀察證據，測試也可以直接驗證。

## 與 Write 的取捨

Write 適合建立新檔或完全重建內容；Edit 適合保留檔案其他區域。對 Coding Agent 來說，Edit 的失敗比靜默套用錯位置安全。

## 練習

1. 為 Edit 加入行號範圍提示。
2. 測試 old 出現零次與兩次。
3. 設計多檔案修改時的原子性策略。

## 本章驗收

- 唯一匹配才能修改。
- 修改結果可被 Read 驗證。
- 不會因模糊匹配而靜默破壞程式碼。
