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
                self.add_filter_frame()
                self.show_table()
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
            self.add_filter_frame()
            self.show_table()
        apply_btn = tk.Button(popup, text="Apply", command=apply_clean, bg="#4CAF50", fg="white")
        check_apply_visibility()

    def add_filter_frame(self):
        # Remove old filter frame if exists
        if hasattr(self, 'filter_frame'):
            self.filter_frame.destroy()
        self.filter_frame = tk.Frame(self.root)
        self.filter_frame.pack(fill="x", padx=10, pady=(0, 0))
        if self.df is None or self.df.empty:
            return
        tk.Label(self.filter_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_column = tk.StringVar(value=self.df.columns[0])
        filter_options = list(self.df.columns)
        filter_menu = ttk.Combobox(self.filter_frame, textvariable=self.filter_column, values=filter_options, state="readonly", width=12)
        filter_menu.pack(side=tk.LEFT, padx=2)
        self.filter_type = tk.StringVar(value="Contains")
        filter_type_options = ["Contains", "Starts With", "Filled Only", "Most Filled"]
        filter_type_menu = ttk.Combobox(self.filter_frame, textvariable=self.filter_type, values=filter_type_options, state="readonly", width=12)
        filter_type_menu.pack(side=tk.LEFT, padx=2)
        self.filter_value = tk.StringVar()
        self.filter_entry = tk.Entry(self.filter_frame, textvariable=self.filter_value, width=15)
        self.filter_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(self.filter_frame, text="Apply Filter", command=self.apply_filter, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(self.filter_frame, text="Clear Filter", command=self.clear_filter, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=5)
        # Always show Export button on the right
        tk.Button(self.filter_frame, text="Export Selected", command=self.export_selected, bg="#4CAF50", fg="white").pack(side=tk.RIGHT, padx=5)
        tk.Button(self.filter_frame, text="Delete Selected", command=self.delete_selected, bg="#ff9800", fg="white").pack(side=tk.RIGHT, padx=5)

    def delete_selected(self):
        if not hasattr(self, 'tree') or self.df is None:
            messagebox.showwarning("No Data", "No data to delete.")
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select rows to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected)} contact(s)? This cannot be undone."):
            return
        # Get indices to drop
        df_to_show = self.df if not hasattr(self, 'table_frame') or not hasattr(self, 'tree') else self.get_current_df()
        indices = []
        for i in selected:
            item_idx = self.tree.index(i)
            if hasattr(self, 'current_df_override') and self.current_df_override is not None:
                orig_idx = self.current_df_override.index[item_idx]
            else:
                orig_idx = item_idx
            indices.append(orig_idx)
        self.df.drop(self.df.index[indices], inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        if self.csv_path:
            self.df.to_csv(self.csv_path, index=False)
        self.show_table()

    def get_current_df(self):
        # Helper to get the DataFrame currently shown in the table
        if hasattr(self, 'current_df_override') and self.current_df_override is not None:
            return self.current_df_override
        return self.df

    def apply_filter(self):
        if self.df is None:
            return
        col = self.filter_column.get()
        ftype = self.filter_type.get()
        val = self.filter_value.get().strip()
        df_filtered = self.df.copy()
        if ftype == "Contains" and val:
            df_filtered = df_filtered[df_filtered[col].astype(str).str.contains(val, case=False, na=False)]
        elif ftype == "Starts With" and val:
            df_filtered = df_filtered[df_filtered[col].astype(str).str.startswith(val, na=False)]
        elif ftype == "Filled Only":
            df_filtered = df_filtered[df_filtered[col].notna() & (df_filtered[col].astype(str).str.strip() != "")]
        elif ftype == "Most Filled":
            # Show only the column with the most filled values
            most_filled_col = self.df.count().idxmax()
            df_filtered = self.df[[most_filled_col]]
        self.show_table(df_override=df_filtered)

    def clear_filter(self):
        self.filter_value.set("")
        self.show_table()

    def export_selected(self):
        if not hasattr(self, 'tree') or self.df is None:
            messagebox.showwarning("No Data", "No data to export.")
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select rows to export.")
            return
        cols = list(self.df.columns)
        rows = [self.tree.item(i)['values'] for i in selected]
        df_export = pd.DataFrame(rows, columns=cols)
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df_export.to_excel(file_path, index=False)
            messagebox.showinfo("Exported", f"Exported {len(df_export)} contacts to {file_path}")

    def show_table(self, df_override=None):
        # Remove old table if exists
        if hasattr(self, 'table_frame'):
            self.table_frame.destroy()
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        df_to_show = df_override if df_override is not None else self.df
        if df_to_show is None or df_to_show.empty:
            return
        cols = list(df_to_show.columns)
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
        for i, row in df_to_show.iterrows():
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

        # Direct cell editing on double-click
        def on_double_click(event):
            region = tree.identify('region', event.x, event.y)
            if region != 'cell':
                return
            row_id = tree.identify_row(event.y)
            col_id = tree.identify_column(event.x)
            if not row_id or not col_id:
                return
            col_index = int(col_id.replace('#', '')) - 1
            col_name = cols[col_index]
            x, y, width, height = tree.bbox(row_id, col_id)
            value = tree.set(row_id, col_name)
            # Create entry widget overlay
            entry = tk.Entry(tree, width=width//8)
            entry.place(x=x, y=y, width=width, height=height)
            entry.insert(0, value)
            entry.focus()
            def save_edit(event=None):
                new_val = entry.get()
                tree.set(row_id, col_name, new_val)
                # Update DataFrame
                item_idx = tree.index(row_id)
                df_to_show.iloc[item_idx, col_index] = new_val
                # If not filtered, update main df and save to CSV
                if df_override is None:
                    self.df.iloc[item_idx, col_index] = new_val
                    if self.csv_path:
                        self.df.to_csv(self.csv_path, index=False)
                else:
                    # If filtered, update main df as well
                    orig_idx = df_to_show.index[item_idx]
                    self.df.at[orig_idx, col_name] = new_val
                    if self.csv_path:
                        self.df.to_csv(self.csv_path, index=False)
                entry.destroy()
            entry.bind('<Return>', save_edit)
            entry.bind('<FocusOut>', lambda e: entry.destroy())
        tree.bind('<Double-1>', on_double_click)

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactCleanerApp(root)
    root.mainloop()
