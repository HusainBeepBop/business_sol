# 🧰 business_sol

**A collection of Python-based automation tools built to simplify repetitive tasks for business owners.**  
These scripts help automate everyday operations — saving time, minimizing errors, and boosting productivity.

---

## 🚀 Features

- 📧 **Email Automation** – Send bulk or templated emails using a Python script or GUI.
- 🗃️ **File Management** – Easily rename, move, or organize files in bulk.
- 📋 **Report Generation** – Generate business reports with minimal input.
- 🕒 **Task Scheduling** – Schedule your scripts to run at specific times.
- 🧱 **Executable Bundling** – Scripts can be converted into standalone `.exe` files using PyInstaller.
- 🧹 **Contact CSV Cleaner & Editor** – Clean, filter, edit, and export contact lists with a user-friendly GUI. Supports direct cell editing, row deletion, and Excel export.

---

## 📦 Setup & Installation

1. **Clone the repository**

```bash
git clone https://github.com/HusainBeepBop/business_sol.git
cd business_sol
```

2. **Install required packages**

```bash
pip install -r requirements.txt
```
> [!NOTE]
> ℹ️ Make sure you have Python 3.8+ installed on your system.

## 🛠️ How to Use
**Each script is self-contained in its own folder or as a standalone file.**

### Email Sender GUI
- Run the email sender tool:

```bash
python email_sender.py
```
- Or use the packaged executable (if available):

```powershell
dist\email_sender.exe
```

### Contact CSV Cleaner & Editor
- Run the contact cleaner tool:

```bash
python contact_cleaner.py
```
- Or use the packaged executable (if available):

```powershell
dist\contact_cleaner.exe
```

**Features:**
- Load a CSV of contacts.
- Select which fields to keep (clean fields).
- View and filter contacts in a table.
- Double-click any cell to edit it directly (auto-saves to CSV).
- Select rows and click "Delete Selected" to remove contacts (with confirmation).
- Export selected rows to Excel.

## 🧪 Packaging as Executable
**To generate a standalone .exe for any script using PyInstaller:**

```bash
python -m PyInstaller --onefile your_script.py --name your_script
```
>[!NOTE]
>The executable will be available in the dist/ folder. Use a unique name for each tool to avoid overwriting previous builds.

## 📁 Folder Structure

```bash
business_sol/
│
├── email_sender.py
├── contact_cleaner.py
├── requirements.txt
├── dist/
│   ├── email_sender.exe
│   └── contact_cleaner.exe
├── ...
└── README.md
```

## 🤝 Contributing
Pull requests are welcome! If you have useful automations you want to share, feel free to contribute.

## 📃 License
This project is licensed under the MIT License.