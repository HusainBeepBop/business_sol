# 🧰 business_sol

**A collection of Python-based automation tools built to simplify repetitive tasks for business owners.**  
These scripts help automate everyday operations — saving time, minimizing errors, and boosting productivity.

---

## 🚀 Features

- 📧 **Email Automation** – Send bulk or templated emails using a Python script.
- 🗃️ **File Management** – Easily rename, move, or organize files in bulk.
- 📋 **Report Generation** – Generate business reports with minimal input.
- 🕒 **Task Scheduling** – Schedule your scripts to run at specific times.
- 🧱 **Executable Bundling** – Scripts can be converted into standalone `.exe` files using PyInstaller.

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
**Each script is self-contained in its own folder. Navigate to the desired automation and run:**

```bash
cd email_automation
python send_email.py
```
## 🧪 Packaging as Executable
**To generate a standalone .exe for any script using PyInstaller:**

```bash
pyinstaller --onefile your_script.py
```
>[!NOTE]
>The executable will be available in the dist/ folder.

## 💼 Who is this for?
- Small business owners
- Freelancers
- Startup founders
- Anyone looking to automate boring, repetitive digital tasks


## 📁 Folder Structure

```bash
    business_sol/
    │
    ├── email_automation/
    │   ├── send_email.py
    │   ├── config.json
    │   └── ...
    │
    ├── file_renamer/
    │   ├── rename_files.py
    │   └── ...
    │
    ├── report_generator/
    │   └── generate_report.py
    │
    └── README.md
```

## 🤝 Contributing
Pull requests are welcome! If you have useful automations you want to share, feel free to contribute.

## 📃 License
This project is licensed under the MIT License.