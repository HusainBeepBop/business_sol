# Changelog

All notable changes to this project will be documented in this file.

## [3.1] - 2025-07-04
### Added
- Net Speed Monitor now logs and displays system metrics: CPU usage, memory usage, and CPU temperature (if available) alongside internet speed.
- All metrics are saved to CSV and visible in the GUI.
- Updated README to document new features for public users.

## [3.0] - 2025-07-01
### Added
- A minimal desktop application to continuously measure and log internet speed (download, upload, ping) with real-time graphs, start/stop/pause controls, and persistent CSV logging. Built with PyQt6 and pyqtgraph for smooth live plotting. 

## [2.0] - 2025-05-29
- Contact CSV Cleaner & Editor GUI: clean, filter, edit, delete, and export contacts from CSV files.
- Direct cell editing in table view (double-click to edit, auto-save to CSV).
- Row deletion with confirmation popup.
- Export selected contacts to Excel.
- Improved filter bar and field selection UI.
- Packaged as standalone executable (contact_cleaner.exe).

### Improved
- Updated README with detailed instructions for both Email Sender and Contact Cleaner tools.
- Packaging instructions clarified for multiple tools.

## [1.1] - 2024-05-26
### Added
- Email Sender GUI: send personalized emails from Excel/CSV with HTML support, progress, and preview.
- Delay and progress bar features.
- Packaged as standalone executable (email_sender.exe).

## [1.0] - 2024-05-26
### Added
- Initial automation scripts for email, file renaming, and report generation.
