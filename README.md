# ACPI_Tree

使用說明
---------------------------
1. 環境準備<br>
請確保你的電腦已安裝 Python (建議 3.7 以上版本)。此工具僅使用 Python 內建函式庫，無需額外安裝 pip install 任何套件。<br>

2. 取得 DSL 檔案<br>
  1.使用 RW-Everything 打開 ACPI Table。<br>
  2.找到 DSDT 或 SSDT。<br>
  3.點擊 Save as 將其存為 .bin 檔案。<br>
  4.使用 Intel ASL Compiler (iasl.exe) 將其反編譯成 .dsl 檔案：(註：你也可以直接嘗試開啟 RW-Everything 直接 dump 出來的內容。)<br>
```iasl -d dsdt.dat```

3. 執行腳本<br>
在終端機或命令提示字元執行：<br>
```python acpi_tree_view.py```

4. 功能操作提示<br>
  1.開啟檔案：點擊左上角按鈕，讀取 .dsl。<br>
  2.瀏覽：左側樹狀結構呈現 Scope 與 Device。Device (RPxx) 底下的子設備會縮進顯示。<br>
  3.搜尋：在上方框輸入 RP05 或 PXSX 後按 Enter。<br>
  4.程式會自動展開所有層級直到看見該節點。<br>
  5.該節點會以黃色高亮顯示。<br>
  6.你可以直接看到該設備下的 _ADR (Address)、_STA (Status) 等重要暫存器設定。<br>


專家開發心得 (給 BIOS 同行) 
---------------------------
層級感：ASL 最麻煩的是 Scope 可以在任何地方定義，本工具透過 stack 追蹤括號層級，能正確還原出 BIOS Code 裡的邏輯嵌套。<br>
搜尋定位：當一個 DSDT 有幾萬行時，手動找 _PRT 很痛苦。這款工具將屬性 (Property) 直接掛在 Device 節點下，讓你在搜尋到 RPxx 時，一眼就能看到它的資源分配，這對於 debug PCIe 裝置沒出來（No Device Found）的問題非常有幫助。<br>
