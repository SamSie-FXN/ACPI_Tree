# ACPI_Tree

如何使用說明
1. 環境準備
請確保你的電腦已安裝 Python (建議 3.7 以上版本)。此工具僅使用 Python 內建函式庫，無需額外安裝 pip install 任何套件。

2. 取得 DSL 檔案
使用 RW-Everything 打開 ACPI Table。
找到 DSDT 或 SSDT。
點擊 Save as 將其存為 .bin 檔案。
使用 Intel ASL Compiler (iasl.exe) 將其反編譯成 .dsl 檔案：
iasl -d dsdt.dat
(註：你也可以直接嘗試開啟 RW-Everything 直接 dump 出來的內容。)

3. 執行腳本
在終端機或命令提示字元執行：
python acpi_tree_view.py

4. 功能操作提示
開啟檔案：點擊左上角按鈕，讀取 .dsl。
瀏覽：左側樹狀結構呈現 Scope 與 Device。Device (RPxx) 底下的子設備會縮進顯示。
搜尋：在上方框輸入 RP05 或 PXSX 後按 Enter。
程式會自動展開所有層級直到看見該節點。
該節點會以黃色高亮顯示。
你可以直接看到該設備下的 _ADR (Address)、_STA (Status) 等重要暫存器設定。

專家開發心得 (給 BIOS 同行)
層級感：ASL 最麻煩的是 Scope 可以在任何地方定義，本工具透過 stack 追蹤括號層級，能正確還原出 BIOS Code 裡的邏輯嵌套。
搜尋定位：當一個 DSDT 有幾萬行時，手動找 _PRT 很痛苦。這款工具將屬性 (Property) 直接掛在 Device 節點下，讓你在搜尋到 RPxx 時，一眼就能看到它的資源分配，這對於 debug PCIe 裝置沒出來（No Device Found）的問題非常有幫助。