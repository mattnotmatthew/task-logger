# main.py

import tkinter as tk
from tkinter import messagebox
import os
import sys

# Import application components
from constants import VERSION, CSV_FILE, DEFAULT_WINDOW_SIZE
from models.task_model import TaskModel
from controllers.task_controller import TaskController
from controllers.report_controller import ReportController
from views.main_view import MainView

def main():
    """
    Main application entry point
    """
    try:
        # Initialize the main window
        root = tk.Tk()
        root.title(f"Task Logger {VERSION}")
        root.geometry(DEFAULT_WINDOW_SIZE)
        
        # Set application icon if available
        try:
            if os.path.exists("app_icon.ico"):
                root.iconbitmap("app_icon.ico")
        except:
            pass  # Ignore icon errors
            
        # Initialize model and controllers
        task_model = TaskModel(CSV_FILE)
        task_controller = TaskController(task_model)
        report_controller = ReportController(task_model)
        
        # Initialize the main view
        app = MainView(root, task_controller, report_controller)
        
        # Start the application
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()