# Task Logger

A Python application for logging and tracking tasks.

## Features

- Start, stop, and complete tasks
- Log time spent on tasks
- Add notes to tasks
- Generate weekly reports in Markdown format
- Export task summaries to CSV

## Installation

No installation required! Just download the executable from the Releases section.

## Usage

1. Run the TaskLogger.exe file
2. Use the buttons to start, stop, or complete tasks
3. View your task history in the main window
4. Generate reports using the reporting buttons

## Development

To work on this project:

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment
4. Install dependencies (if any)
5. Run the script: `python task_logger.py`

## Building the Executable

The executable was built using PyInstaller:

```
pyinstaller --onefile --noconsole --icon=app_icon.ico task_logger.py
```

## License

MIT
