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
        # Placeholder for next checkpoint
        messagebox.showinfo("Clean", "Field selection popup will be implemented in the next checkpoint.")


def main():
    root = tk.Tk()
    app = ContactCleanerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
