import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re

class ACPITreeExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("ACPI DSL Tree Explorer - BIOS Expert Tool")
        self.root.geometry("1000x700")

        self.nodes_dict = {}  # 儲存 tree_id 與節點名稱的對應
        self.setup_ui()

    def setup_ui(self):
        # 上方控制列
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.pack(side=tk.TOP, fill=tk.X)

        self.btn_open = ttk.Button(top_frame, text="開啟 .dsl 檔案", command=self.load_file)
        self.btn_open.pack(side=tk.LEFT, padx=5)

        ttk.Label(top_frame, text="搜尋 (Device/Method):").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_node())

        self.btn_search = ttk.Button(top_frame, text="搜尋並展開", command=self.search_node)
        self.btn_search.pack(side=tk.LEFT, padx=5)

        # 中間樹狀視圖
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=("Type", "Detail"), show="tree headings")
        self.tree.heading("#0", text="ACPI Structure (Scope/Device/Method)")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Detail", text="Value/Detail")
        self.tree.column("#0", width=400)
        self.tree.column("Type", width=100)
        self.tree.column("Detail", width=300)

        # 滾動條
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # 設定標籤顏色
        self.tree.tag_configure('highlight', background='yellow')
        self.tree.tag_configure('device', foreground='blue', font=('Segoe UI', 9, 'bold'))
        self.tree.tag_configure('method', foreground='green')
        self.tree.tag_configure('prop', foreground='dark orange')

    def parse_dsl(self, file_path):
        """解析 DSL 檔案邏輯"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        stack = [("", "")] # (tree_id, current_indent)
        
        # 正則表達式
        header_re = re.compile(r'(Device|Scope|Method)\s*\(([^,)]+)')
        prop_re = re.compile(r'Name\s*\((_[A-Z0-9]{3}),\s*([^)]+)\)|(_ADR|_STA|_PRT)')

        for line in lines:
            line_strip = line.strip()
            if not line_strip or line_strip.startswith("//") or line_strip.startswith("*"):
                continue

            # 處理進場 (括號層級)
            match = header_re.search(line_strip)
            if match:
                obj_type = match.group(1)
                obj_name = match.group(2).strip().strip('"')
                
                parent_id = stack[-1][0]
                
                tag = 'device' if obj_type == "Device" else 'method'
                if any(x in obj_name for x in ["RP", "PXSX", "GFX0"]):
                    display_name = f"★ {obj_name}"
                else:
                    display_name = obj_name

                node_id = self.tree.insert(parent_id, "end", text=display_name, values=(obj_type, ""), tags=(tag,))
                self.nodes_dict[node_id] = obj_name
                
                if "{" in line_strip:
                    stack.append((node_id, "{"))
                else:
                    stack.append((node_id, "pending"))
                continue

            if "{" in line_strip and stack[-1][1] == "pending":
                stack[-1] = (stack[-1][0], "{")
                continue

            # 處理屬性 (如 _ADR)
            prop_match = prop_re.search(line_strip)
            if prop_match:
                p_name = prop_match.group(1) or prop_match.group(3)
                p_val = prop_match.group(2) if prop_match.group(2) else ""
                parent_id = stack[-1][0]
                self.tree.insert(parent_id, "end", text=p_name, values=("Property", p_val), tags=('prop',))

            # 處理退場
            if "}" in line_strip:
                if len(stack) > 1:
                    stack.pop()

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("DSL files", "*.dsl"), ("All files", "*.*")])
        if file_path:
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.nodes_dict.clear()
            
            try:
                self.parse_dsl(file_path)
                messagebox.showinfo("成功", "DSL 檔案解析完成！")
            except Exception as e:
                messagebox.showerror("錯誤", f"解析失敗: {str(e)}")

    def search_node(self):
        query = self.search_var.get().strip().upper()
        if not query:
            return

        # 清除舊的高亮
        for item in self.tree.get_children():
            self.clear_tags_recursive(item)

        found_items = []
        self.find_items_recursive("", query, found_items)

        if found_items:
            for item in found_items:
                # 展開父節點
                parent = self.tree.parent(item)
                while parent:
                    self.tree.item(parent, open=True)
                    parent = self.tree.parent(parent)
                
                self.tree.selection_set(item)
                self.tree.see(item)
                
                current_tags = list(self.tree.item(item, "tags"))
                if 'highlight' not in current_tags:
                    current_tags.append('highlight')
                self.tree.item(item, tags=tuple(current_tags))
        else:
            messagebox.showinfo("搜尋", f"找不到包含 '{query}' 的節點。")

    def find_items_recursive(self, parent, query, found_list):
        for item in self.tree.get_children(parent):
            if query in self.tree.item(item, "text").upper():
                found_list.append(item)
            self.find_items_recursive(item, query, found_list)

    def clear_tags_recursive(self, item):
        tags = list(self.tree.item(item, "tags"))
        if 'highlight' in tags:
            tags.remove('highlight')
            self.tree.item(item, tags=tuple(tags))
        for child in self.tree.get_children(item):
            self.clear_tags_recursive(child)

if __name__ == "__main__":
    root = tk.Tk()
    app = ACPITreeExplorer(root)
    root.mainloop()