# constants.py

import os

# Application version
VERSION = "1.5.0"

# File and directory paths
CSV_FILE = "task_log.csv"
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".task_logger")

# Default settings
DEFAULT_WINDOW_SIZE = "500x800"

# UI Colors
COLORS = {
    "primary": "#4287f5",      # Blue
    "secondary": "#f0f0f0",    # Light gray
    "success": "#4caf50",      # Green
    "warning": "#ff9800",      # Orange
    "danger": "#f44336",       # Red
    "text": "#333333",         # Dark gray
    "light_text": "#666666",   # Medium gray
    "background": "#ffffff",   # White
    "sidebar": "#2c3e50",      # Dark blue-gray
    "sidebar_text": "#ecf0f1", # Almost white
}