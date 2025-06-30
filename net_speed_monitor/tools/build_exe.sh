#!/usr/bin/env bash
python -m pip install --upgrade pyinstaller
pyinstaller --onefile --windowed ../net_speed_monitor.py
