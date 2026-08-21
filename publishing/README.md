# EPUB 生產

## 出版資訊

- 書名：用 Python 自己寫一個 Coding Agent
- 副標：從對話迴圈、工具呼叫到可擴充的 AI 程式助手
- 作者：Happy eBook Authors
- 出版者：Happy eBook
- 語言：zh-TW
- 版次：第 1 版
- 封面：1600×2400 RGB

## 產物

- `cover/cover-1600x2400.png`：無損封面
- `cover/cover-1600x2400.jpg`：EPUB／書店用封面
- `cover/build_cover.py`：可編輯封面排版來源
- `ebook.css`：EPUB CJK、程式碼、表格與圖片樣式
- `build_epub.py`：EPUB 3 建置與結構驗證腳本
- `../dist/python-coding-agent-book.epub`：發行草稿

## 重建

```bash
uv run --with pillow python publishing/cover/build_cover.py
uv run --with pillow python publishing/build_epub.py
uv run --with pillow python publishing/check_reproducible_build.py
```

建置腳本會：

1. 依六篇十八章順序組裝 Markdown；
2. 加入練習解答附錄；
3. 將篇名與章名建立為巢狀導覽；
4. 保留正文 `1. …` 章號，但從 EPUB 導覽標籤移除章號；
5. 嵌入 1600×2400 JPEG 封面；
6. 寫入標題、副標、作者、出版者、語言、日期與 UUID；
7. 確認 mimetype、OPF、cover-image、nav 與封面尺寸。

建置會固定 OPF `dcterms:modified` 與所有 ZIP entry timestamp／權限。`check_reproducible_build.py` 連續建置兩次並要求 SHA-256 完全相同。

## EPUBCheck

本專案以 EPUBCheck 5.3.0 驗證：

```bash
java -jar epubcheck-5.3.0/epubcheck.jar dist/python-coding-agent-book.epub
```

目前結果為 0 fatals、0 errors、0 warnings。

Pandoc 會顯示缺少 `zh-TW` UI translation 的警告；這是 Pandoc 翻譯資料警告，不是 EPUB 規格錯誤。EPUBCheck 結果才是封裝有效性的判定依據。

## 尚待人工驗證

- Ace by DAISY：目前在此 WSL／Chromium 執行環境於 `nav.xhtml` 發生處理錯誤，尚未取得完整報告。
- 至少兩種實際 EPUB 閱讀器的手機與桌面預覽。
- Google Play Books 上傳預覽。
- 書店描述、分類、關鍵字、價格與 DRM 決策。
