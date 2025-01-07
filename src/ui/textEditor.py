import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, simpledialog, messagebox
import keyword
import re


class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Text Editor")

        # Initialize variables
        self.text_font = ("Consolas", 12)
        self.file_path = None
        self.word_wrap = tk.FALSE

        # Setup UI
        self.setup_ui()
        self.bind_events()

    def setup_ui(self):
        # Frame for text editor and line numbers
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Line numbers
        self.line_numbers = tk.Text(
            self.frame, width=3, bg="#1e1e1e", fg="#858585", font=self.text_font, state=tk.DISABLED, bd=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Main text widget
        self.text = tk.Text(
            self.frame,
            wrap=tk.NONE,
            font=self.text_font,
            undo=True,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#d4d4d4",
            selectbackground="#264f78",
            selectforeground="#ffffff",
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars
        y_scroll = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.sync_scroll_y)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=y_scroll.set)
        self.line_numbers.configure(yscrollcommand=y_scroll.set)

        x_scroll = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.text.xview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.text.configure(xscrollcommand=x_scroll.set)

        # Syntax highlighting tags
        self.text.tag_configure("keyword", foreground="#569cd6")
        self.text.tag_configure("string", foreground="#ce9178")
        self.text.tag_configure("comment", foreground="#6a9955", font=self.text_font)
        self.text.tag_configure("number", foreground="#b5cea8")
        self.text.tag_configure("builtin", foreground="#4ec9b0")

        # Menu
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find and Replace", command=self.find_and_replace)
        edit_menu.add_command(label="Goto Line", command=self.goto_line)

        view_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Word Wrap", command=self.toggle_word_wrap)

    def bind_events(self):
        self.text.bind("<KeyRelease>", self.on_key_release)
        self.text.bind("<MouseWheel>", lambda e: self.sync_scroll_y())
        self.text.bind("<Control-z>", lambda e: self.text.edit_undo())
        self.text.bind("<Control-y>", lambda e: self.text.edit_redo())
        self.text.bind("<Tab>", self.insert_tab)

    def sync_scroll_y(self, *args):
        self.line_numbers.yview_moveto(self.text.yview()[0])
        self.text.yview(*args)

    def update_line_numbers(self):
        lines = self.text.get("1.0", tk.END).split("\n")
        line_number_string = "\n".join(str(i) for i in range(1, len(lines)))
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_number_string)
        self.line_numbers.config(state=tk.DISABLED)

    def syntax_highlight(self):
        self.text.tag_remove("keyword", "1.0", tk.END)
        self.text.tag_remove("string", "1.0", tk.END)
        self.text.tag_remove("comment", "1.0", tk.END)
        self.text.tag_remove("number", "1.0", tk.END)
        self.text.tag_remove("builtin", "1.0", tk.END)

        text_content = self.text.get("1.0", tk.END)

        # Highlight keywords
        for kw in keyword.kwlist:
            start_idx = "1.0"
            while True:
                start_idx = self.text.search(rf'\b{kw}\b', start_idx, tk.END, regexp=True)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(kw)}c"
                self.text.tag_add("keyword", start_idx, end_idx)
                start_idx = end_idx

        # Highlight numbers
        start_idx = "1.0"
        while True:
            start_idx = self.text.search(r'\b\d+\b', start_idx, tk.END, regexp=True)
            if not start_idx:
                break
            end_idx = f"{start_idx}+{len(self.text.get(start_idx, f'{start_idx} lineend'))}c"
            self.text.tag_add("number", start_idx, end_idx)
            start_idx = end_idx

        # Highlight comments
        start_idx = "1.0"
        while True:
            start_idx = self.text.search(r'#.*', start_idx, tk.END, regexp=True)
            if not start_idx:
                break
            end_idx = f"{start_idx} lineend"
            self.text.tag_add("comment", start_idx, end_idx)
            start_idx = end_idx

        # Highlight strings
        for pattern in [r'"[^"]*"', r"'[^']*'"]:
            start_idx = "1.0"
            while True:
                start_idx = self.text.search(pattern, start_idx, tk.END, regexp=True)
                if not start_idx:
                    break
                end_idx = f"{start_idx} lineend"
                self.text.tag_add("string", start_idx, end_idx)
                start_idx = end_idx

    def on_key_release(self, event):
        self.update_line_numbers()
        self.syntax_highlight()

    def insert_tab(self, event):
        self.text.insert(tk.INSERT, " " * 4)
        return "break"

    def new_file(self):
        self.text.delete("1.0", tk.END)
        self.file_path = None
        self.root.title("Untitled - Tkinter Text Editor")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", file.read())
            self.file_path = file_path
            self.root.title(f"{file_path} - Tkinter Text Editor")
            self.update_line_numbers()

    def save_file(self):
        if not self.file_path:
            self.save_as_file()
        else:
            with open(self.file_path, "w") as file:
                file.write(self.text.get("1.0", tk.END).strip())
            messagebox.showinfo("Save File", "File saved successfully!")

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self.file_path = file_path
            self.save_file()

    def find_and_replace(self):
        find = simpledialog.askstring("Find and Replace", "Find:")
        replace = simpledialog.askstring("Find and Replace", "Replace with:")
        if find and replace:
            content = self.text.get("1.0", tk.END)
            content = content.replace(find, replace)
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", content)

    def goto_line(self):
        line = simpledialog.askinteger("Goto Line", "Enter line number:")
        if line:
            self.text.mark_set("insert", f"{line}.0")
            self.text.see(f"{line}.0")

    def toggle_word_wrap(self):
        self.word_wrap = not self.word_wrap
        self.text.config(wrap=tk.WORD if self.word_wrap else tk.NONE)


if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()
