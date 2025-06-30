# Net Speed Monitor

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)  
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A minimal desktop application to continuously measure and log internet speed (download, upload, ping) with real-time graphs, start/stop/pause controls, and persistent CSV logging. Built with PyQt6 and pyqtgraph for smooth live plotting.

---

## Screenshot

*Add a screenshot at `docs/screenshot.png`*

---

## Quick Start

```bash
python -m pip install -r requirements.txt
python net_speed_monitor.py
```

---

## Packaging

To build a standalone executable:

```bash
pyinstaller --onefile --windowed net_speed_monitor.py
```

The `--windowed` flag prevents a console window from popping up on Windows.

---

## Output Log Format (CSV)

Example:

```csv
timestamp,download,upload,ping
2025-06-30 12:00:00,94.2,18.1,12.3
2025-06-30 12:01:00,92.7,17.9,12.1
```

---

## Required Libraries

```bash
python -m pip install PyQt6 pyqtgraph speedtest-cli pandas
```

---

## License

MIT License. See [LICENSE](LICENSE).
