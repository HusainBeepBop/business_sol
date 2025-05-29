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
        field_vars = {}
        fields_frame = tk.Frame(popup)
        fields_frame.pack(fill="both", expand=True, padx=10)
        for col in self.df.columns:
            var = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(fields_frame, text=col, variable=var)
            cb.pack(anchor="w")
            field_vars[col] = var
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
        tk.Button(popup, text="Apply", command=apply_clean, bg="#4CAF50", fg="white").pack(pady=10)

    def show_table(self):
        # Remove old table if exists
        if hasattr(self, 'table_frame'):
            self.table_frame.destroy()
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        if self.df is None:
            return
        cols = list(self.df.columns)
        tree = ttk.Treeview(self.table_frame, columns=cols, show='headings', selectmode='extended')
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
        tree.pack(fill="both", expand=True)
        # Add lines between rows
        style.configure("Treeview", bordercolor="#cccccc", borderwidth=1)
        # Save reference for later editing
        self.tree = tree


def main():
    root = tk.Tk()
    app = ContactCleanerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
