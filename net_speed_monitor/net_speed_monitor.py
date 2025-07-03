import sys
# Monkey-patch for PyInstaller/Speedtest compatibility
if not hasattr(sys, 'stdout') or sys.stdout is None:
    import io
    sys.stdout = io.StringIO()

# Ensure builtins is imported for speedtest-cli compatibility
import builtins
import threading
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyqtgraph as pg
from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QWidget,
    QMainWindow,
    QFileDialog,
    QMessageBox,
)

# System monitoring
import psutil
import wmi

try:
    from speedtest import Speedtest
except ImportError:
    raise SystemExit(
        "speedtest-cli not installed. Run: python -m pip install speedtest-cli"
    )


class SpeedTestWorker(QObject):
    """Runs speed tests in a separate thread and emits results."""

    result_ready = pyqtSignal(dict)

    def __init__(self, interval: int = 60):
        super().__init__()
        self._interval = interval  # seconds between tests
        self._running = False
        self._paused = False

    def start_tests(self):
        self._running = True
        self._paused = False
        threading.Thread(target=self._loop, daemon=True).start()

    def pause(self, state: bool):
        self._paused = state

    def stop(self):
        self._running = False

    def _loop(self):
        st = Speedtest()
        st.get_servers()
        c = wmi.WMI(namespace="root\\wmi")
        while self._running:
            if self._paused:
                time.sleep(1)
                continue
            try:
                st.get_best_server()
                download = st.download() / 1_000_000  # to Mbps
                upload = st.upload(pre_allocate=False) / 1_000_000
                ping = st.results.ping

                # System metrics
                cpu_percent = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory()
                mem_percent = mem.percent
                mem_used = mem.used / (1024 ** 3)
                mem_total = mem.total / (1024 ** 3)
                # CPU temperature (Windows, may require admin)
                cpu_temp = None
                try:
                    temps = c.MSAcpi_ThermalZoneTemperature()
                    if temps:
                        # Convert from tenths of Kelvin to Celsius
                        cpu_temp = round(temps[0].CurrentTemperature / 10.0 - 273.15, 1)
                except Exception:
                    cpu_temp = None

                result = {
                    "timestamp": datetime.now(),
                    "download": round(download, 2),
                    "upload": round(upload, 2),
                    "ping": round(ping, 2),
                    "cpu_percent": cpu_percent,
                    "mem_percent": mem_percent,
                    "mem_used": round(mem_used, 2),
                    "mem_total": round(mem_total, 2),
                    "cpu_temp": cpu_temp,
                }
                self.result_ready.emit(result)
            except Exception as exc:
                self.result_ready.emit(
                    {
                        "timestamp": datetime.now(),
                        "download": None,
                        "upload": None,
                        "ping": None,
                        "cpu_percent": None,
                        "mem_percent": None,
                        "mem_used": None,
                        "mem_total": None,
                        "cpu_temp": None,
                        "error": str(exc),
                    }
                )
            for _ in range(self._interval):
                if not self._running or self._paused:
                    break
                time.sleep(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Net Speed Monitor")
        self.resize(900, 500)

        # ‑‑‑ Data storage
        self.data = pd.DataFrame(columns=[
            "timestamp", "download", "upload", "ping",
            "cpu_percent", "mem_percent", "mem_used", "mem_total", "cpu_temp"
        ])
        self.csv_path = (
            Path.cwd()
            / f"speed_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        # ‑‑‑ Plot
        pg.setConfigOptions(antialias=True)
        self.plot = pg.PlotWidget(title="Live Internet Speed (Mbps)")
        self.plot.addLegend()
        self.download_line = self.plot.plot(
            pen=pg.mkPen(width=2), name="Download"
        )
        self.upload_line = self.plot.plot(
            pen=pg.mkPen(style=Qt.PenStyle.DotLine, width=2), name="Upload"
        )
        self.drop_scatter = pg.ScatterPlotItem(pen=None, brush="r", size=10)
        self.plot.addItem(self.drop_scatter)
        # Set up auto-range for x-axis (show last N points)
        self.max_points = 30  # Number of points to keep visible
        self.plot.setXRange(0, self.max_points, padding=0)
        self.plot.setAutoVisible(y=True)

        # Loading animation
        self.loading_label = QLabel("<b>Loading...</b>")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.hide()

        # ‑‑‑ Labels
        self.dl_label = QLabel("Download: … Mbps")
        self.ul_label = QLabel("Upload: … Mbps")
        self.ping_label = QLabel("Ping: … ms")
        self.cpu_label = QLabel("CPU: … %")
        self.mem_label = QLabel("Memory: … %")
        self.temp_label = QLabel("CPU Temp: … °C")

        # ‑‑‑ Buttons
        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop & Save")
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        # Layout
        hbox = QHBoxLayout()
        for widget in (self.dl_label, self.ul_label, self.ping_label, self.cpu_label, self.mem_label, self.temp_label):
            hbox.addWidget(widget)
            hbox.addStretch(1)
        btnbox = QHBoxLayout()
        for widget in (self.start_btn, self.pause_btn, self.stop_btn):
            btnbox.addWidget(widget)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.plot)
        vbox.addWidget(self.loading_label)
        vbox.addLayout(btnbox)
        container = QWidget()
        container.setLayout(vbox)
        self.setCentralWidget(container)

        # Thread + worker
        self.worker = SpeedTestWorker(interval=10)  # 10-second interval for more frequent updates
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker.result_ready.connect(self.handle_result)
        self.worker_thread.started.connect(self.worker.start_tests)

        # Signals
        self.start_btn.clicked.connect(self.start_tests)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.stop_btn.clicked.connect(self.stop_tests)

    # ‑‑‑ UI callbacks
    def start_tests(self):
        if not self.worker_thread.isRunning():
            self.worker_thread.start()
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.loading_label.show()
        self.loading_label.setText("<b>Testing... Please wait</b>")

    def toggle_pause(self):
        paused = self.pause_btn.text() == "Pause"
        self.worker.pause(paused)
        self.pause_btn.setText("Resume" if paused else "Pause")

    def stop_tests(self):
        self.worker.stop()
        self.worker_thread.quit()
        self.worker_thread.wait()
        self.save_data()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.loading_label.hide()

    def handle_result(self, result: dict):
        # append to DataFrame
        self.data = pd.concat(
            [self.data, pd.DataFrame([result])], ignore_index=True
        )
        # update labels
        if result.get("download") is not None:
            self.dl_label.setText(f"Download: {result['download']:.2f} Mbps")
            self.ul_label.setText(f"Upload: {result['upload']:.2f} Mbps")
            self.ping_label.setText(f"Ping: {result['ping']:.2f} ms")
            self.cpu_label.setText(f"CPU: {result.get('cpu_percent', 0):.1f} %")
            self.mem_label.setText(f"Memory: {result.get('mem_percent', 0):.1f} % ({result.get('mem_used', 0):.2f}/{result.get('mem_total', 0):.2f} GB)")
            temp = result.get('cpu_temp')
            if temp is not None:
                self.temp_label.setText(f"CPU Temp: {temp:.1f} °C")
            else:
                self.temp_label.setText("CPU Temp: N/A")
            self.loading_label.setText("<b>Testing... Please wait</b>")
        else:
            # error case
            self.dl_label.setText("Download: error")
            self.ul_label.setText("Upload: error")
            self.ping_label.setText("Ping: error")
            self.cpu_label.setText("CPU: error")
            self.mem_label.setText("Memory: error")
            self.temp_label.setText("CPU Temp: error")
            self.loading_label.setText("<b>Error: Test failed</b>")

        # update plot lines
        x = self.data.index.values
        self.download_line.setData(x, self.data["download"].fillna(0).values)
        self.upload_line.setData(x, self.data["upload"].fillna(0).values)

        # Auto-move x-axis to keep last N points visible
        if len(x) > self.max_points:
            self.plot.setXRange(x[-self.max_points], x[-1], padding=0)
        else:
            self.plot.setXRange(0, self.max_points, padding=0)

        # critical drops (download < 30% of mean of previous 5 tests)
        if len(self.data) > 5:
            recent_mean = self.data["download"].tail(5).mean()
            drops = self.data["download"] < 0.3 * recent_mean
            self.drop_scatter.setData(x[drops], self.data.loc[drops, "download"].values)

    # ‑‑‑ Helpers
    def save_data(self):
        try:
            self.data.to_csv(self.csv_path, index=False)
            QMessageBox.information(
                self,
                "Saved",
                f"Log saved to {self.csv_path}",
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Save error",
                f"Could not save log: {exc}",
            )

    def closeEvent(self, event: QCloseEvent):
        if self.worker_thread.isRunning():
            self.worker.stop()
            self.worker_thread.quit()
            self.worker_thread.wait()
        self.save_data()
        self.loading_label.hide()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
