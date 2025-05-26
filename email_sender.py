import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import threading

class EmailSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Sender from Excel")
        self.root.geometry("700x700")
        self.file_path = None
        self.df = None
        self.column_vars = {}
        self.custom_fields = []
        self.setup_gui()

    def setup_gui(self):
        # File selection
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10)
        tk.Label(file_frame, text="Excel File:").pack(side=tk.LEFT)
        self.file_entry = tk.Entry(file_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=self.browse_excel_file).pack(side=tk.LEFT)

        # Column mapping
        self.mapping_frame = tk.LabelFrame(self.root, text="Column Mapping")
        self.mapping_frame.pack(fill="x", padx=10, pady=10)
        self.mapping_widgets = {}
        for label in ["Name", "Email"]:
            row = tk.Frame(self.mapping_frame)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label+" column:", width=15, anchor="w").pack(side=tk.LEFT)
            var = tk.StringVar()
            self.column_vars[label] = var
            cb = ttk.Combobox(row, textvariable=var, state="readonly")
            cb.pack(side=tk.LEFT, fill="x", expand=True)
            self.mapping_widgets[label] = cb
        # Custom fields
        self.custom_fields_frame = tk.Frame(self.mapping_frame)
        self.custom_fields_frame.pack(fill="x", pady=2)
        tk.Button(self.mapping_frame, text="Add Custom Field", command=self.add_custom_field).pack(pady=2)

        # Email subject
        subject_frame = tk.Frame(self.root)
        subject_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(subject_frame, text="Subject:").pack(side=tk.LEFT)
        self.subject_entry = tk.Entry(subject_frame, width=80)
        self.subject_entry.pack(side=tk.LEFT, padx=5)

        # Email body
        body_frame = tk.Frame(self.root)
        body_frame.pack(fill="both", expand=True, padx=10, pady=5)
        tk.Label(body_frame, text="Body:").pack(anchor="w")
        self.body_text = tk.Text(body_frame, height=10)
        self.body_text.pack(fill="both", expand=True)

        # Placeholder guidance
        self.placeholder_label = tk.Label(self.root, text="Available placeholders: {Name}, {Email}", fg="blue")
        self.placeholder_label.pack(pady=2)

        # Sender credentials
        sender_frame = tk.LabelFrame(self.root, text="Sender Credentials")
        sender_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(sender_frame, text="Sender Email:").grid(row=0, column=0, sticky="e")
        self.sender_email_entry = tk.Entry(sender_frame, width=30)
        self.sender_email_entry.grid(row=0, column=1, padx=5, pady=2)
        tk.Label(sender_frame, text="Password:").grid(row=1, column=0, sticky="e")
        self.sender_password_entry = tk.Entry(sender_frame, show="*", width=30)
        self.sender_password_entry.grid(row=1, column=1, padx=5, pady=2)

        # SMTP config
        smtp_frame = tk.LabelFrame(self.root, text="SMTP Configuration")
        smtp_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(smtp_frame, text="SMTP Host:").grid(row=0, column=0, sticky="e")
        self.smtp_host_entry = tk.Entry(smtp_frame, width=25)
        self.smtp_host_entry.insert(0, "smtp.gmail.com")
        self.smtp_host_entry.grid(row=0, column=1, padx=5, pady=2)
        tk.Label(smtp_frame, text="Port:").grid(row=0, column=2, sticky="e")
        self.smtp_port_entry = tk.Entry(smtp_frame, width=6)
        self.smtp_port_entry.insert(0, "587")
        self.smtp_port_entry.grid(row=0, column=3, padx=5, pady=2)
        self.tls_var = tk.BooleanVar(value=True)
        tk.Checkbutton(smtp_frame, text="Use TLS/SSL", variable=self.tls_var).grid(row=0, column=4, padx=5)

        # Send button
        self.send_button = tk.Button(self.root, text="Send Emails", command=self.start_sending_emails, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.send_button.pack(pady=10)

        # Status display
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)
        tk.Label(status_frame, text="Status:").pack(anchor="w")
        self.status_text = tk.Text(status_frame, height=10, state="disabled", bg="#f0f0f0")
        self.status_text.pack(fill="both", expand=True)

    def browse_excel_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.file_path = file_path
            try:
                self.df = pd.read_excel(file_path)
                columns = list(self.df.columns)
                for label, cb in self.mapping_widgets.items():
                    cb['values'] = columns
                    if columns:
                        cb.current(0)
                self.update_placeholder_label()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load Excel file: {e}")

    def add_custom_field(self):
        idx = len(self.custom_fields) + 1
        field_name = f"Custom Field {idx}"
        row = tk.Frame(self.custom_fields_frame)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=field_name+" column:", width=15, anchor="w").pack(side=tk.LEFT)
        var = tk.StringVar()
        cb = ttk.Combobox(row, textvariable=var, state="readonly")
        cb.pack(side=tk.LEFT, fill="x", expand=True)
        if self.df is not None:
            cb['values'] = list(self.df.columns)
            if self.df.columns.size > 0:
                cb.current(0)
        self.custom_fields.append((field_name, var))
        self.update_placeholder_label()

    def update_placeholder_label(self):
        placeholders = ["{Name}", "{Email}"]
        for field, _ in self.custom_fields:
            placeholders.append(f"{{{field}}}")
        self.placeholder_label.config(text="Available placeholders: " + ", ".join(placeholders))

    def start_sending_emails(self):
        t = threading.Thread(target=self.send_emails)
        t.start()

    def send_emails(self):
        self.set_status("")
        if not self.df_is_ready():
            return
        sender = self.sender_email_entry.get().strip()
        password = self.sender_password_entry.get().strip()
        smtp_host = self.smtp_host_entry.get().strip()
        smtp_port = self.smtp_port_entry.get().strip()
        use_tls = self.tls_var.get()
        subject_template = self.subject_entry.get()
        body_template = self.body_text.get("1.0", tk.END)
        name_col = self.column_vars["Name"].get()
        email_col = self.column_vars["Email"].get()
        custom_map = {field: var.get() for field, var in self.custom_fields}
        # Validation
        if not sender or not password or not smtp_host or not smtp_port:
            self.set_status("Missing sender credentials or SMTP details.")
            return
        if not name_col or not email_col:
            self.set_status("Please map both Name and Email columns.")
            return
        try:
            smtp_port = int(smtp_port)
        except ValueError:
            self.set_status("SMTP port must be a number.")
            return
        # Connect to SMTP
        try:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
            if use_tls:
                server.starttls()
            server.login(sender, password)
        except Exception as e:
            self.set_status(f"SMTP connection failed: {e}")
            return
        total = len(self.df)
        sent = 0
        errors = 0
        for idx, row in self.df.iterrows():
            name = str(row.get(name_col, ""))
            email = str(row.get(email_col, ""))
            if not email:
                self.append_status(f"Row {idx+1}: Missing email, skipped.")
                errors += 1
                continue
            # Prepare placeholders
            placeholders = {"Name": name, "Email": email}
            for field, col in custom_map.items():
                placeholders[field] = str(row.get(col, ""))
            subject = subject_template.format(**placeholders)
            body = body_template.format(**placeholders)
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            try:
                server.sendmail(sender, email, msg.as_string())
                sent += 1
                self.append_status(f"Email sent to {name} <{email}>. Remaining: {total-sent}")
            except Exception as e:
                errors += 1
                self.append_status(f"Error sending to {name} <{email}>: {e}")
            time.sleep(1.5)
        server.quit()
        if errors == 0:
            self.append_status("All emails sent successfully!")
        else:
            self.append_status(f"Completed with {errors} errors.")

    def set_status(self, msg):
        self.status_text.config(state="normal")
        self.status_text.delete("1.0", tk.END)
        self.status_text.insert(tk.END, msg+"\n")
        self.status_text.config(state="disabled")

    def append_status(self, msg):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, msg+"\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")

    def df_is_ready(self):
        if self.df is None:
            self.set_status("No Excel file loaded.")
            return False
        return True

def main():
    root = tk.Tk()
    app = EmailSenderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
