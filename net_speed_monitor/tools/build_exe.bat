@echo off
python -m pip install --upgrade pyinstaller
pyinstaller --onefile --windowed ..\net_speed_monitor.py
