import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QListWidget, QMessageBox
)
from PyQt6.QtCore import Qt

try:
    from pptx2pdf import convert
except ImportError:
    convert = None

class PPTXtoPDFConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PPTX to PDF Converter")
        self.resize(500, 400)
        layout = QVBoxLayout()

        self.label = QLabel("Select PPTX files to convert to PDF.")
        layout.addWidget(self.label)

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        self.select_btn = QPushButton("Select PPTX Files")
        self.select_btn.clicked.connect(self.select_files)
        layout.addWidget(self.select_btn)

        self.convert_btn = QPushButton("Convert to PDF")
        self.convert_btn.clicked.connect(self.convert_files)
        layout.addWidget(self.convert_btn)

        self.setLayout(layout)
        self.pptx_files = []

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PPTX Files", "", "PowerPoint Files (*.pptx)")
        if files:
            self.pptx_files = files
            self.file_list.clear()
            self.file_list.addItems(files)

    def convert_files(self):
        if not self.pptx_files:
            QMessageBox.warning(self, "No Files", "Please select PPTX files first.")
            return
        if convert is None:
            QMessageBox.critical(self, "Missing Dependency", "pptx2pdf is not installed. Run: pip install pptx2pdf")
            return
        downloads = str(Path.home() / "Downloads" / "pptx_to_pdf")
        os.makedirs(downloads, exist_ok=True)
        errors = []
        for pptx in self.pptx_files:
            try:
                convert(pptx, downloads)
            except Exception as e:
                errors.append(f"{os.path.basename(pptx)}: {e}")
        if errors:
            QMessageBox.warning(self, "Some files failed", "\n".join(errors))
        else:
            QMessageBox.information(self, "Done", f"PDFs saved to {downloads}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PPTXtoPDFConverter()
    win.show()
    sys.exit(app.exec())
