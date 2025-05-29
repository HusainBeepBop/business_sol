import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

class ContactCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact CSV Cleaner & Editor")
        self.root.geometry("900x600")
        self.csv_path = None
        self.df = None
        self.setup_gui()

    def setup_gui(self):
        # File picker frame
        file_frame = tk.Frame(self.root)
        file_frame.pack(fill="x", pady=10, padx=10)
        self.file_entry = tk.Entry(file_frame, width=60)
        self.file_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=self.browse_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Clean", command=self.clean_fields_popup).pack(side=tk.LEFT, padx=5)

    def browse_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.csv_path = file_path
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            try:
                self.df = pd.read_csv(file_path)
                messagebox.showinfo("Loaded", f"Loaded {file_path} with {len(self.df)} rows.")
                self.show_table()  # Show table immediately after loading
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {e}")

    def clean_fields_popup(self):
        if self.df is None:
            messagebox.showwarning("No CSV", "Please load a CSV file first.")
            return
        popup = tk.Toplevel(self.root)
        popup.title("Select Fields to Keep")
        popup.geometry("350x400")
        tk.Label(popup, text="Select fields to keep:", font=("Arial", 12, "bold")).pack(pady=10)
        # Improved scrollable frame for checkboxes
        container = tk.Frame(popup)
        container.pack(fill="both", expand=True, padx=10, pady=(0,10))
        canvas = tk.Canvas(container, borderwidth=0, height=300)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)
        scroll_frame_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        scroll_frame.bind("<Enter>", lambda e: scroll_frame.bind_all('<MouseWheel>', _on_mousewheel))
        scroll_frame.bind("<Leave>", lambda e: scroll_frame.unbind_all('<MouseWheel>'))
        def _resize_canvas(event):
            canvas.itemconfig(scroll_frame_id, width=event.width)
        canvas.bind('<Configure>', _resize_canvas)
        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        field_vars = {}
        for col in self.df.columns:
            var = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(scroll_frame, text=col, variable=var)
            cb.pack(anchor="w", pady=2)
            field_vars[col] = var
        def check_apply_visibility(*_):
            if any(var.get() for var in field_vars.values()):
                apply_btn.pack(pady=10)
            else:
                apply_btn.pack_forget()
        for var in field_vars.values():
            var.trace_add('write', check_apply_visibility)
        def apply_clean():
            keep_fields = [col for col, var in field_vars.items() if var.get()]
            if not keep_fields:
                messagebox.showwarning("No Fields", "You must keep at least one field.")
                return
            self.df = self.df[keep_fields]
            self.df.to_csv(self.csv_path, index=False)
            messagebox.showinfo("Cleaned", f"CSV updated to keep {len(keep_fields)} fields.")
            popup.destroy()
            self.show_table()
        apply_btn = tk.Button(popup, text="Apply", command=apply_clean, bg="#4CAF50", fg="white")
        check_apply_visibility()

    def show_table(self):
        # Remove old table if exists
        if hasattr(self, 'table_frame'):
            self.table_frame.destroy()
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        if self.df is None or self.df.empty:
            return
        cols = list(self.df.columns)
        # Add a vertical scrollbar for the Treeview
        tree_scroll = tk.Scrollbar(self.table_frame, orient="vertical")
        tree_scroll.pack(side="right", fill="y")
        tree = ttk.Treeview(self.table_frame, columns=cols, show='headings', selectmode='extended', yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=tree.yview)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')
        # Add alternating row colors
        style = ttk.Style()
        style.configure("Treeview", rowheight=24)
        style.map('Treeview', background=[('selected', '#b3d9ff')])
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        for i, row in self.df.iterrows():
            values = [row[col] for col in cols]
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert('', 'end', values=values, tags=(tag,))
        tree.tag_configure('evenrow', background='#f9f9f9')
        tree.tag_configure('oddrow', background='#e6e6e6')
        tree.pack(fill="both", expand=True, side="left")
        # Add lines between rows
        style.configure("Treeview", bordercolor="#cccccc", borderwidth=1)
        # Smooth mousewheel scrolling
        def _on_mousewheel(event):
            tree.yview_scroll(int(-1*(event.delta/120)), "units")
        tree.bind('<Enter>', lambda e: tree.bind_all('<MouseWheel>', _on_mousewheel))
        tree.bind('<Leave>', lambda e: tree.unbind_all('<MouseWheel>'))
        # Save reference for later editing
        self.tree = tree


def main():
    root = tk.Tk()
    app = ContactCleanerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
