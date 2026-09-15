import tkinter as tk
from tkinter import filedialog, messagebox
import tokenize
import keyword
import re
import os
import shutil
import json
import io

BG_MAIN = "#1e1e1e"
BG_PANEL = "#252526"
FG_TEXT = "#d4d4d4"
BG_ENTRY = "#3c3c3c"
BG_BTN = "#333333"
FG_BTN = "#ffffff"
BG_BTN_HOVER = "#4d4d4d"
BG_DELETE_BTN = "#8a2b2b"
FG_DELETE_BTN = "#ffffff"
LIST_SEL_BG = "#094771"
HIGHLIGHT_LINE = "#3b3b3b"

class CommentRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python & Jupyter Comment Remover")
        self.root.geometry("1100x650")
        self.root.config(bg=BG_MAIN)
        
        self.filepath = ""
        self.all_comments = []
        self.displayed_comments = []
        self.notebook_data = None

        self.setup_ui()

    def setup_ui(self):
        left_frame = tk.Frame(self.root, width=380, padx=10, pady=10, bg=BG_PANEL)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)

        btn_select = tk.Button(left_frame, text="Select .py or .ipynb File", command=self.load_file, 
                               bg=BG_BTN, fg=FG_BTN, activebackground=BG_BTN_HOVER, activeforeground=FG_BTN, relief=tk.FLAT, pady=5)
        btn_select.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_file = tk.Label(left_frame, text="No file selected", fg="#888888", bg=BG_PANEL, wraplength=350)
        self.lbl_file.pack(pady=(0, 10))

        search_frame = tk.Frame(left_frame, bg=BG_PANEL)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(search_frame, text="Find:", bg=BG_PANEL, fg=FG_TEXT).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_comments)
        
        entry_search = tk.Entry(search_frame, textvariable=self.search_var, bg=BG_ENTRY, fg=FG_TEXT, insertbackground="white", relief=tk.FLAT)
        entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=3)

        btn_frame = tk.Frame(left_frame, bg=BG_PANEL)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Button(btn_frame, text="Select All", command=self.select_all, bg=BG_BTN, fg=FG_BTN, relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        tk.Button(btn_frame, text="Deselect All", command=self.deselect_all, bg=BG_BTN, fg=FG_BTN, relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        tk.Label(left_frame, text="Comments (Left-click select, Right-click view):", bg=BG_PANEL, fg=FG_TEXT).pack(anchor="w", pady=(0,5))
        
        list_scroll = tk.Scrollbar(left_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(left_frame, selectmode=tk.MULTIPLE, yscrollcommand=list_scroll.set, 
                                  bg=BG_MAIN, fg=FG_TEXT, selectbackground=LIST_SEL_BG, highlightthickness=0, relief=tk.FLAT)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.listbox.yview)
        
        self.listbox.bind("<Button-3>", self.on_right_click)

        btn_delete = tk.Button(left_frame, text="Delete Selected Comments", command=self.delete_comments, 
                               bg=BG_DELETE_BTN, fg=FG_DELETE_BTN, activebackground="#a33333", activeforeground="white", relief=tk.FLAT, pady=8)
        btn_delete.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        right_frame = tk.Frame(self.root, padx=10, pady=10, bg=BG_MAIN)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right_frame, text="Code Preview:", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", pady=(0,5))

        text_scroll = tk.Scrollbar(right_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_view = tk.Text(right_frame, wrap=tk.NONE, yscrollcommand=text_scroll.set, 
                                 bg=BG_MAIN, fg="#a9b7c6", insertbackground="white", highlightthickness=0, relief=tk.FLAT, padx=5, pady=5)
        self.text_view.pack(fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.text_view.yview)
        
        x_scroll = tk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=self.text_view.xview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_view.config(xscrollcommand=x_scroll.set)

        self.setup_tags()

    def setup_tags(self):
        self.text_view.tag_configure("keyword", foreground="#cc7832", font=("Courier", 10, "bold"))
        self.text_view.tag_configure("string", foreground="#6a8759")
        self.text_view.tag_configure("comment", foreground="#808080", font=("Courier", 10, "italic"))
        self.text_view.tag_configure("highlight_line", background=HIGHLIGHT_LINE)
        self.text_view.tag_configure("cell_header", foreground="#4b92d6", font=("Courier", 10, "bold"), background="#2a2a2a")

    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Select File", 
            filetypes=[("Python & Jupyter", "*.py *.ipynb"), ("Python Files", "*.py"), ("Jupyter Notebooks", "*.ipynb")]
        )
        if not filepath:
            return

        self.filepath = filepath
        self.lbl_file.config(text=os.path.basename(filepath), fg=FG_TEXT)
        self.search_var.set("") 
        self.notebook_data = None
        self.parse_and_display()

    def parse_and_display(self):
        ext = os.path.splitext(self.filepath)[1].lower()
        self.all_comments = []
        preview_content = ""

        try:
            if ext == '.py':
                with open(self.filepath, "r", encoding="utf-8") as f:
                    preview_content = f.read()

                with open(self.filepath, 'rb') as f:
                    for tok in tokenize.tokenize(f.readline):
                        if tok.type == tokenize.COMMENT:
                            self.all_comments.append({
                                'type': 'py',
                                'line': tok.start[0],
                                'col': tok.start[1],
                                'text': tok.string,
                                'display_line': tok.start[0]
                            })

            elif ext == '.ipynb':
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.notebook_data = json.load(f)

                preview_lines = []
                for cell_idx, cell in enumerate(self.notebook_data.get('cells', [])):
                    if cell.get('cell_type') == 'code':
                        source_lines = cell.get('source', [])
                        if isinstance(source_lines, str):
                            source_lines = [source_lines]
                            
                        cell_text = "".join(source_lines)
                        
                        cell_start_preview_line = len(preview_lines) + 2 
                        
                        header = f"# --- Code Cell {cell_idx} ---\n"
                        preview_lines.append(header)
                        
                        try:
                            bytes_io = io.BytesIO(cell_text.encode('utf-8'))
                            for tok in tokenize.tokenize(bytes_io.readline):
                                if tok.type == tokenize.COMMENT:
                                    self.all_comments.append({
                                        'type': 'ipynb',
                                        'cell_idx': cell_idx,
                                        'source_line_idx': tok.start[0] - 1,
                                        'col': tok.start[1],
                                        'text': tok.string,
                                        'display_line': cell_start_preview_line + tok.start[0] - 1 
                                    })
                        except tokenize.TokenError:
                            pass
                            
                        for line in source_lines:
                            preview_lines.append(line if line.endswith('\n') else line + '\n')
                        preview_lines.append('\n')
                
                preview_content = "".join(preview_lines)

            self.text_view.config(state=tk.NORMAL)
            self.text_view.delete(1.0, tk.END)
            self.text_view.insert(tk.END, preview_content)
            self.apply_syntax_highlighting()
            self.text_view.config(state=tk.DISABLED)

            self.filter_comments()

        except Exception as e:
            messagebox.showerror("Error", f"Could not parse file properly:\n{e}")

    def apply_syntax_highlighting(self):
        content = self.text_view.get("1.0", tk.END)
        
        for match in re.finditer(r'^# --- Code Cell \d+ ---$', content, re.MULTILINE):
            start = f"1.0 + {match.start()}c"
            end = f"1.0 + {match.end()}c"
            self.text_view.tag_add("cell_header", start, end)

        for kw in keyword.kwlist:
            for match in re.finditer(r'\b' + kw + r'\b', content):
                start = f"1.0 + {match.start()}c"
                end = f"1.0 + {match.end()}c"
                self.text_view.tag_add("keyword", start, end)

        for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', content):
            start = f"1.0 + {match.start()}c"
            end = f"1.0 + {match.end()}c"
            self.text_view.tag_add("string", start, end)

        for match in re.finditer(r'#.*', content):
            text_match = match.group()
            if not text_match.startswith("# --- Code Cell"):
                start = f"1.0 + {match.start()}c"
                end = f"1.0 + {match.end()}c"
                self.text_view.tag_add("comment", start, end)

    def filter_comments(self, *args):
        query = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        self.displayed_comments = []

        for c in self.all_comments:
            if query in c['text'].lower():
                self.displayed_comments.append(c)
                if c['type'] == 'py':
                    display_text = f"Ln {c['display_line']}: {c['text'].strip()}"
                else:
                    display_text = f"Cell {c['cell_idx']} Ln {c['source_line_idx']+1}: {c['text'].strip()}"
                self.listbox.insert(tk.END, display_text)

    def select_all(self):
        self.listbox.select_set(0, tk.END)

    def deselect_all(self):
        self.listbox.selection_clear(0, tk.END)

    def on_right_click(self, event):
        if not self.displayed_comments:
            return
            
        index = self.listbox.nearest(event.y)
        if index >= 0 and index < len(self.displayed_comments):
            comment = self.displayed_comments[index]
            line_num = comment['display_line']

            self.text_view.see(f"{line_num}.0")
            self.text_view.tag_remove("highlight_line", "1.0", tk.END)
            self.text_view.tag_add("highlight_line", f"{line_num}.0", f"{line_num}.end")

    def delete_comments(self):
        if not self.filepath:
            messagebox.showwarning("Warning", "No file selected.")
            return

        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "No comments selected for deletion.")
            return

        do_backup = messagebox.askyesnocancel("Backup", "Do you want to create a backup of the original file before modifying it?")
        if do_backup is None:
            return
        
        if do_backup:
            try:
                shutil.copy(self.filepath, self.filepath + ".bak")
            except Exception as e:
                messagebox.showerror("Backup Error", f"Failed to create backup:\n{e}")
                return

        to_delete = [self.displayed_comments[i] for i in selected_indices]
        ext = os.path.splitext(self.filepath)[1].lower()

        try:
            if ext == '.py':
                with open(self.filepath, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                to_delete.sort(key=lambda x: x['line'], reverse=True)

                for c in to_delete:
                    line_idx = c['line'] - 1
                    start_col = c['col']
                    
                    original_line = lines[line_idx]
                    new_line = original_line[:start_col]
                    
                    if new_line.strip() == "":
                        lines.pop(line_idx)
                    else:
                        lines[line_idx] = new_line.rstrip() + "\n"

                with open(self.filepath, "w", encoding="utf-8") as f:
                    f.writelines(lines)

            elif ext == '.ipynb':
                to_delete.sort(key=lambda x: (x['cell_idx'], x['source_line_idx']), reverse=True)

                for c in to_delete:
                    c_idx = c['cell_idx']
                    s_idx = c['source_line_idx']
                    start_col = c['col']
                    
                    cell_source = self.notebook_data['cells'][c_idx]['source']
                    
                    if isinstance(cell_source, str):
                        cell_source = cell_source.splitlines(keepends=True)
                        
                    original_line = cell_source[s_idx]
                    new_line = original_line[:start_col]
                    
                    if new_line.strip() == "":
                        cell_source.pop(s_idx)
                    else:
                        suffix = "\n" if original_line.endswith('\n') else ""
                        cell_source[s_idx] = new_line.rstrip() + suffix
                        
                    self.notebook_data['cells'][c_idx]['source'] = cell_source

                with open(self.filepath, "w", encoding="utf-8") as f:
                    json.dump(self.notebook_data, f, indent=1, ensure_ascii=False)

            messagebox.showinfo("Success", "Selected comments have been deleted successfully!")
            self.parse_and_display() 
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CommentRemoverApp(root)
    root.mainloop()
