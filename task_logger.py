
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import pandas as pd
from datetime import datetime, timedelta
import os
import uuid
import webbrowser
import sys
import markdown

VERSION = "1.3.0" 

# Constants
CSV_FILE = "task_log.csv"
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".task_logger")
DEFAULT_WINDOW_SIZE = "500x800"

# Colors
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

class TaskLogger:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Logger")
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        
        # Set application icon if available
        try:
            if os.path.exists("app_icon.ico"):
                self.root.iconbitmap("app_icon.ico")
        except:
            pass  # Ignore icon errors
        
        # Initialize always on top state variable
        self.always_on_top_var = tk.BooleanVar(value=True)
        
        # Initialize data
        self.load_data()
        
        # Configure styles
        self.configure_styles()
        
        # UI Components
        self.setup_ui()
        
        # Apply always on top setting
        self.toggle_always_on_top()

        # Initialize filter state variable
        self.current_filter = "all"  # Default to showing all tasks
        
        # Refresh history on load
        self.refresh_history()
    
    def configure_styles(self):
        """Configure ttk styles for consistent look and feel"""
        style = ttk.Style()
        
        # Configure the theme
        try:
            style.theme_use('clam')  # Try to use a more modern theme if available
        except:
            pass  # Default theme is acceptable
        
        # Button styles
        style.configure('Primary.TButton', 
                        background=COLORS["primary"], 
                        foreground=COLORS["background"],
                        font=('Arial', 10, 'bold'))
        
        style.configure('Success.TButton', 
                        background=COLORS["success"], 
                        foreground=COLORS["background"],
                        font=('Arial', 10, 'bold'))
        
        style.configure('Warning.TButton', 
                        background=COLORS["warning"], 
                        foreground=COLORS["text"],
                        font=('Arial', 10, 'bold'))
        
        # Label styles
        style.configure('Header.TLabel',
                        font=('Arial', 14, 'bold'),
                        foreground=COLORS["primary"])
        
        style.configure('Subheader.TLabel',
                        font=('Arial', 12, 'bold'),
                        foreground=COLORS["text"])
    
    def load_data(self):
        """Load data from CSV or create a new DataFrame if file doesn't exist"""
        if os.path.exists(CSV_FILE):
            self.df = pd.read_csv(CSV_FILE)
        else:
            self.df = pd.DataFrame(columns=[
                "Task ID", "Task Description", "Start Time", "Stop Time", 
                "Duration (min)", "Completed", "Notes", "Active"
            ])
            self.save_data()
        
        # Ensure necessary columns exist
        required_columns = ["Task ID", "Task Description", "Start Time", "Stop Time", 
                         "Duration (min)", "Completed", "Notes", "Active"]
        for col in required_columns:
            if col not in self.df.columns:
                self.df[col] = ""
    
    def save_data(self):
        """Save the DataFrame to the CSV file"""
        # Create backup before saving
        if os.path.exists(CSV_FILE):
            backup_file = f"{CSV_FILE}.bak"
            try:
                self.df.to_csv(backup_file, index=False)
            except Exception as e:
                print(f"Error creating backup: {e}")
        
        # Save current data
        try:
            self.df.to_csv(CSV_FILE, index=False)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save data: {e}")
    
    def setup_ui(self):
        """Set up the user interface"""
        # Configure the root window to use grid
        self.root.configure(bg=COLORS["background"])
        
        # Configure grid weights to make content area expandable
        self.root.grid_columnconfigure(0, weight=1)  # Makes column expandable
        self.root.grid_rowconfigure(1, weight=1)     # Makes content row expandable
        
        # Create a header frame
        header_frame = tk.Frame(self.root, bg=COLORS["primary"], padx=10, pady=10)
        header_frame.grid(row=0, column=0, sticky="ew")  # Stick to east-west
        
        # App title
        title_label = tk.Label(
            header_frame, 
            text="Task Logger", 
            font=("Arial", 18, "bold"), 
            fg=COLORS["background"],
            bg=COLORS["primary"]
        )
        title_label.pack(side="left")
        
        # Always on top toggle
        always_on_top_frame = tk.Frame(header_frame, bg=COLORS["primary"])
        always_on_top_frame.pack(side="right")
        
        always_on_top_checkbox = tk.Checkbutton(
            always_on_top_frame,
            text="Always on Top",
            variable=self.always_on_top_var,
            command=self.toggle_always_on_top,
            bg=COLORS["primary"],
            fg=COLORS["background"],
            selectcolor=COLORS["primary"],
            activebackground=COLORS["primary"],
            activeforeground=COLORS["background"],
        )
        always_on_top_checkbox.pack(side="right")
        
        # Main content area - will expand/contract with window
        content_frame = tk.Frame(self.root, bg=COLORS["background"], padx=15, pady=15)
        content_frame.grid(row=1, column=0, sticky="nsew")  # nsew = fill in all directions
        
        # Rest of your content setup remains the same, using pack within content_frame
        # Action buttons section
        actions_frame = tk.LabelFrame(
            content_frame, 
            text="Actions", 
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Arial", 11, "bold"),
            padx=10, 
            pady=10
        )
        actions_frame.pack(fill="x", pady=(0, 15))
        
        # Create a button frame with grid layout for task actions
        button_frame = tk.Frame(actions_frame, bg=COLORS["background"])
        button_frame.pack(fill="x")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Task action buttons
        start_button = tk.Button(
            button_frame, 
            text="Start Task", 
            command=self.start_task, 
            bg=COLORS["success"],
            fg=COLORS["background"],
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
        )
        start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    
        
        finish_button = tk.Button(
            button_frame, 
            text="Finish Task", 
            command=self.finish_task,
            bg=COLORS["primary"],
            fg=COLORS["background"], 
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
        )
        finish_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Export actions section
        export_frame = tk.LabelFrame(
            content_frame, 
            text="Reporting", 
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Arial", 11, "bold"),
            padx=10, 
            pady=10
        )
        export_frame.pack(fill="x", pady=(0, 15))
        
        # Preview button
        preview_button = tk.Button(
            export_frame,
            text="Preview Weekly Report",
            command=self.preview_markdown,
            bg=COLORS["primary"],
            fg=COLORS["background"],
            font=("Arial", 10),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
        )
        preview_button.pack(fill="x", pady=5)
        
        # Export button
        export_button = tk.Button(
            export_frame,
            text="Export to Markdown",
            command=self.export_to_markdown,
            bg=COLORS["primary"],
            fg=COLORS["background"],
            font=("Arial", 10),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
        )
        export_button.pack(fill="x", pady=5)
        
        # Summary button
        summary_button = tk.Button(
            export_frame,
            text="Generate Weekly CSV Summary",
            command=self.summarize_tasks,
            bg=COLORS["primary"],
            fg=COLORS["background"],
            font=("Arial", 10),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
        )
        summary_button.pack(fill="x", pady=5)
        
        # Task History section
        history_frame = tk.LabelFrame(
            content_frame,
            text="Task History",
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        history_frame.pack(fill="both", expand=True)
        
        # Add scrollbar to history text
        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Custom font for history
        history_font = ("Consolas", 10)
        
        # History text widget with custom styling
        self.history_text = tk.Text(
            history_frame, 
            wrap="word", 
            state="disabled",
            yscrollcommand=scrollbar.set,
            bg=COLORS["secondary"],
            fg=COLORS["text"],
            font=history_font,
            relief=tk.SUNKEN,
            borderwidth=2,
            padx=5,
            pady=5
        )
        self.history_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.history_text.yview)
        
        # Add status bar at the bottom using grid
        status_frame = tk.Frame(self.root, bg=COLORS["sidebar"], padx=5, pady=3)
        status_frame.grid(row=2, column=0, sticky="ew")  # Stick to east-west
        
        status_text = f"Task Logger {VERSION} • Last updated: {datetime.now().strftime('%Y-%m-%d')}"
        status_label = tk.Label(
            status_frame, 
            text=status_text, 
            fg=COLORS["sidebar_text"], 
            bg=COLORS["sidebar"],
            font=("Arial", 8)
        )
        status_label.pack(side="left")
        
        # Add a refresh button to the status bar
        refresh_button = tk.Button(
            status_frame,
            text="↻ Refresh",
            command=self.refresh_history,
            bg=COLORS["sidebar"],
            fg=COLORS["sidebar_text"],
            font=("Arial", 8),
            relief=tk.FLAT,
            borderwidth=0,
            padx=5,
            highlightthickness=0
        )
        refresh_button.pack(side="right")
        
        # Task Filter section
        filter_frame = tk.LabelFrame(
            content_frame,
            text="Filter Tasks",
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        filter_frame.pack(fill="x", pady=(0, 15))

        # Filter buttons
        filter_button_frame = tk.Frame(filter_frame, bg=COLORS["background"])
        filter_button_frame.pack(fill="x")
        filter_button_frame.grid_columnconfigure(0, weight=1)
        filter_button_frame.grid_columnconfigure(1, weight=1)
        filter_button_frame.grid_columnconfigure(2, weight=1)

        # All tasks button
        self.all_button = tk.Button(
            filter_button_frame,
            text="All Tasks",
            command=lambda: self.filter_tasks("all"),
            bg=COLORS["primary"],  # Start with this one active
            fg=COLORS["background"],
            font=("Arial", 10),
            relief=tk.RAISED,
            borderwidth=2,
            padx=5,
            pady=5
        )
        self.all_button.grid(row=0, column=0, padx=2, pady=5, sticky="ew")

        # Active tasks button
        self.active_button = tk.Button(
            filter_button_frame,
            text="Active Tasks",
            command=lambda: self.filter_tasks("active"),
            bg=COLORS["secondary"],
            fg=COLORS["text"],
            font=("Arial", 10),
            relief=tk.RAISED,
            borderwidth=2,
            padx=5,
            pady=5
        )
        self.active_button.grid(row=0, column=1, padx=2, pady=5, sticky="ew")

        # Finished tasks button
        self.finished_button = tk.Button(
            filter_button_frame,
            text="Finished Tasks",
            command=lambda: self.filter_tasks("finished"),
            bg=COLORS["secondary"],
            fg=COLORS["text"],
            font=("Arial", 10),
            relief=tk.RAISED,
            borderwidth=2,
            padx=5,
            pady=5
        )
        self.finished_button.grid(row=0, column=2, padx=2, pady=5, sticky="ew")

        # Configure text tags for colored text in history
        self.history_text.tag_configure("completed", foreground=COLORS["success"])
        self.history_text.tag_configure("stopped", foreground=COLORS["warning"])
        self.history_text.tag_configure("active", foreground=COLORS["primary"])
        self.history_text.tag_configure("timestamp", foreground=COLORS["light_text"], font=(history_font[0], history_font[1], "italic"))
        self.history_text.tag_configure("note", foreground=COLORS["light_text"])
        
        # Set minimum window size to ensure all elements are visible
        self.root.update_idletasks()
        min_width = 500
        min_height = 1000  # Reduced minimum height
        self.root.minsize(min_width, min_height)

    def toggle_always_on_top(self):
        """Toggle always-on-top state"""
        self.root.attributes("-topmost", self.always_on_top_var.get())

    def filter_tasks(self, filter_type):
        """Filter tasks by status: all, active, or finished"""
        # Set current filter
        self.current_filter = filter_type
        
        # Update button appearances based on active filter
        self.all_button.config(
            bg=COLORS["primary"] if filter_type == "all" else COLORS["secondary"],
            fg=COLORS["background"] if filter_type == "all" else COLORS["text"]
        )
        
        self.active_button.config(
            bg=COLORS["primary"] if filter_type == "active" else COLORS["secondary"],
            fg=COLORS["background"] if filter_type == "active" else COLORS["text"]
        )
        
        self.finished_button.config(
            bg=COLORS["primary"] if filter_type == "finished" else COLORS["secondary"],
            fg=COLORS["background"] if filter_type == "finished" else COLORS["text"]
        )
        
        # Refresh the task history with filtered results
        self.refresh_history()


    def refresh_history(self):
        """Refresh the task history display"""
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        
        try:
            # Convert datetime columns and sort
            sorted_df = self.df.copy()

            # Parse dates
            sorted_df["Start Time"] = pd.to_datetime(sorted_df["Start Time"], errors='coerce')
            sorted_df["Stop Time"] = pd.to_datetime(sorted_df["Stop Time"], errors='coerce')

            # Determine the last activity time (either Stop Time or Start Time)
            sorted_df["Last Activity"] = sorted_df[["Start Time", "Stop Time"]].max(axis=1)

            # Sort by Last Activity in descending order
            sorted_df = sorted_df.sort_values(by="Last Activity", ascending=False)

            # Apply current filter
            if self.current_filter == "active":
                sorted_df = sorted_df[sorted_df["Active"] == 1]
                self.history_text.insert(tk.END, "Showing active tasks only\n\n", "active")
            elif self.current_filter == "finished":
                sorted_df = sorted_df[sorted_df["Active"] == 0]
                self.history_text.insert(tk.END, "Showing finished tasks only\n\n", "completed")
            else:
                # If showing all tasks, add a summary of active tasks
                active_count = len(sorted_df[sorted_df["Active"] == 1])
                if active_count > 0:
                    self.history_text.insert(tk.END, f"You have {active_count} active task(s)\n\n", "active")

            # Display recent tasks
            for _, row in sorted_df.head(25).iterrows():
                desc = row["Task Description"]
                start_time = row["Start Time"]
                stop_time = row["Stop Time"]
                hasStopTime = pd.notna(stop_time)
                active = row["Active"] == 0
                duration = f"{row['Duration (min)']} min" if pd.notna(row["Duration (min)"]) else "-"
                note = str(row["Notes"]) if pd.notna(row["Notes"]) else ""
                note_snippet = (note[:100] + "...") if len(note) > 100 else note

                # Format the timestamp safely
                def format_timestamp(ts):
                    if pd.notna(ts):
                        try:
                            return ts.strftime("%Y-%m-%d %H:%M")
                        except (AttributeError, ValueError):
                            return "Invalid timestamp"
                    return "No timestamp"

                if active:
                    icon = "✅"
                    timestamp = format_timestamp(stop_time)
                    status = "Completed"
                    tag = "completed"
                else:
                    icon = "▶️"
                    timestamp = format_timestamp(start_time)
                    status = "In Progress"
                    tag = "active"

                self.history_text.insert(tk.END, f"{icon} ", tag)
                self.history_text.insert(tk.END, f"{timestamp}: ", "timestamp")
                self.history_text.insert(tk.END, f"- {status} - ", tag)
                self.history_text.insert(tk.END, f"{desc}", tag)

                self.history_text.insert(tk.END, "\n\n")
                
        except Exception as e:
            import traceback
            self.history_text.insert(tk.END, f"Error refreshing history: {str(e)}\n")
            self.history_text.insert(tk.END, traceback.format_exc())
        
        self.history_text.config(state="disabled")
        
    def get_active_tasks(self):
        """Get list of currently active tasks"""
        # Filter for tasks where Active = 1 AND Completed = "No"
        active = self.df[(self.df["Active"] == 1)]
        return sorted(active["Task Description"].unique())
        
    def get_inactive_tasks(self):
        """Get list of currently inactive tasks"""
        active = self.df[(self.df["Active"] == 0) & (self.df["Completed"] == "No")]
        return sorted(active["Task Description"].unique())
    
    def create_dialog(self, title, width=350, height=200):
        """Create a standard dialog window with consistent styling"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        
        # Safer popup positioning
        self.root.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_w = self.root.winfo_width()
        
        if main_x < 0 or main_y < 0:
            main_x = 100
            main_y = 100
        
        dialog.geometry(f"+{main_x + main_w + 10}+{main_y}")
        dialog.attributes("-topmost", self.always_on_top_var.get())
        dialog.grab_set()
        
        # Style the dialog
        dialog.configure(bg=COLORS["background"])
        
        # Create a header
        header = tk.Frame(dialog, bg=COLORS["primary"], padx=10, pady=5)
        header.pack(fill="x")
        
        header_label = tk.Label(
            header,
            text=title,
            font=("Arial", 12, "bold"),
            fg=COLORS["background"],
            bg=COLORS["primary"]
        )
        header_label.pack(anchor="w")
        
        # Create a content frame
        content = tk.Frame(dialog, bg=COLORS["background"], padx=15, pady=15)
        content.pack(fill="both", expand=True)
        
        return dialog, content
    ####
    def start_task(self):
        """Start a new task or resume an existing one"""
        # Get only active tasks (where Active = 0) for the dropdown
        active_tasks = self.get_inactive_tasks();
       ## existing_tasks = sorted(active_tasks["Task Description"].dropna().unique())
        
        # Create dialog
        dialog, content = self.create_dialog("Start Task", 380, 250)
        
        # Build form
        tk.Label(
            content, 
            text="Choose or enter task:",
            font=("Arial", 10, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).pack(anchor="w", pady=(0, 5))
        
        task_var = tk.StringVar()
        
        # Task dropdown frame
        dropdown_frame = tk.Frame(content, bg=COLORS["background"])
        dropdown_frame.pack(fill="x", pady=5)
        
        # Handle empty task list by setting default empty string
        if active_tasks:
            task_var.set(active_tasks[0])
            task_menu = ttk.Combobox(
                dropdown_frame, 
                textvariable=task_var, 
                values=active_tasks,
                width=45
            )
            task_menu.pack(fill="x", padx=5)
        else:
            task_var.set("")
            task_menu = ttk.Combobox(
                dropdown_frame, 
                textvariable=task_var,
                width=45
            )
            task_menu.pack(fill="x", padx=5)
        
        tk.Label(
            content, 
            text="Or type a new task name:",
            font=("Arial", 10),
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).pack(anchor="w", pady=(10, 5))
        
        task_entry = tk.Entry(
            content, 
            textvariable=task_var, 
            width=45,
            font=("Arial", 10),
            bd=2,
            relief=tk.GROOVE
        )
        task_entry.pack(fill="x", pady=5)
        
        tk.Label(
            content, 
            text="Optional Notes:",
            font=("Arial", 10),
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).pack(anchor="w", pady=(10, 5))
        
        note_entry = tk.Entry(
            content, 
            width=45,
            font=("Arial", 10),
            bd=2,
            relief=tk.GROOVE
        )
        note_entry.pack(fill="x", pady=5)
        
        # Button frame
        button_frame = tk.Frame(content, bg=COLORS["background"])
        button_frame.pack(fill="x", pady=(15, 0))
        
        def on_submit():
            selected_task = task_var.get().strip()
            note = note_entry.get().strip()
            
            if not selected_task:
                messagebox.showwarning("Warning", "Please enter a task description")
                return
            
            active = (
                self.df[(self.df["Task Description"] == selected_task) & 
                        (self.df["Completed"] == "No") & 
                        (self.df["Active"] == 1)]
            )
            
            if not active.empty:
                idx = active.index[-1]
                if note:
                    self.df.at[idx, "Notes"] += f" | {note}"
                messagebox.showinfo("Already Active", f"Task '{selected_task}' is already active. Note added.")
            else:
                task_id = str(uuid.uuid4())
                start_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                new_row = {
                    "Task ID": task_id,
                    "Task Description": selected_task,
                    "Start Time": start_time,
                    "Stop Time": "",
                    "Duration (min)": "",
                    "Completed": "No",
                    "Notes": note or "",
                    "Active": 1
                }
                self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
                messagebox.showinfo("Started", f"Started task: {selected_task}")
            
            self.save_data()
            self.refresh_history()
            dialog.destroy()
        
        # Create the buttons
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            bg=COLORS["secondary"],
            fg=COLORS["text"],
            font=("Arial", 10),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
        )
        cancel_button.pack(side="left", padx=5)
        
        start_button = tk.Button(
            button_frame,
            text="Start",
            command=on_submit,
            bg=COLORS["success"],
            fg=COLORS["background"],
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=20,
            pady=5
        )
        start_button.pack(side="right", padx=5)
        
        # Focus the entry
        task_entry.focus_set()
        ####
    def stop_task(self):
        """Stop an active task"""
        active_tasks_list = self.get_active_tasks()
        
        if not active_tasks_list:
            messagebox.showinfo("No Active Tasks", "There are no active tasks to stop.")
            return
        
        # Create dialog
        dialog, content = self.create_dialog("Stop Task", 380, 230)
        
        # Build form
        tk.Label(
            content, 
            text="Choose task to stop:",
            font=("Arial", 10, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).pack(anchor="w", pady=(0, 5))
        
        task_var = tk.StringVar()
        
        if active_tasks_list:
            task_var.set(active_tasks_list[0])
            task_menu = ttk.Combobox(
                content, 
                textvariable=task_var, 
                values=active_tasks_list,
                width=45
            )
        else:
            task_var.set("")
            task_menu = ttk.Combobox(
                content, 
                textvariable=task_var,
                width=45
            )
        
        task_menu.pack(fill="x", pady=5)
        
        tk.Label(
            content, 
            text="Optional Notes:",
            font=("Arial", 10),
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).pack(anchor="w", pady=(10, 5))
        
        note_entry = tk.Entry(
            content, 
            width=45,
            font=("Arial", 10),
            bd=2,
            relief=tk.GROOVE
        )
        note_entry.pack(fill="x", pady=5)
        
        # Button frame
        button_frame = tk.Frame(content, bg=COLORS["background"])
        button_frame.pack(fill="x", pady=(15, 0))
        
        def on_submit():
            selected = task_var.get().strip()
            note = note_entry.get().strip()
            
            if not selected:
                messagebox.showwarning("Warning", "Please select a task")
                return
            
            active = self.df[self.df["Active"] == 1]
            task_rows = active[active["Task Description"] == selected]
            if task_rows.empty:
                messagebox.showwarning("Warning", "No active task found with that name")
                return
            
            # Find most recent row
            idx = task_rows.index[-1]
            stop_time = datetime.now()
            
            try:
                start_time = datetime.strptime(self.df.at[idx, "Start Time"], "%Y-%m-%d %H:%M")
                duration = round((stop_time - start_time).total_seconds() / 60, 2)
            except (ValueError, TypeError):
                duration = 0
            
            self.df.at[idx, "Stop Time"] = stop_time.strftime("%Y-%m-%d %H:%M")
            self.df.at[idx, "Duration (min)"] = duration
            self.df.at[idx, "Active"] = 0
            if note:
                self.df.at[idx, "Notes"] += f" | {note}"
            
            self.save_data()
            messagebox.showinfo("Stopped", f"Stopped task: {selected} ({duration} min)")
            dialog.destroy()
            self.refresh_history()
        
        # Create the buttons
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            bg=COLORS["secondary"],
            fg=COLORS["text"],
            font=("Arial", 10),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
        )
        cancel_button.pack(side="left", padx=5)
        
        stop_button = tk.Button(
            button_frame,
            text="Stop",
            command=on_submit,
            bg=COLORS["warning"],
            fg=COLORS["text"],
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=20,
            pady=5
        )
        stop_button.pack(side="right", padx=5)
    
    def finish_task(self):
        """Mark a task as completed"""
        active_tasks_list = self.get_active_tasks()
        
        if not active_tasks_list:
            messagebox.showinfo("No Active Tasks", "There are no active tasks to finish.")
            return
        
        # Create dialog
        dialog, content = self.create_dialog("Finish Task", 380, 230)
        
        # Build form
        tk.Label(
            content, 
            text="Choose task to complete:",
            font=("Arial", 10, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).pack(anchor="w", pady=(0, 5))
        
        task_var = tk.StringVar()
        
        if active_tasks_list:
            task_var.set(active_tasks_list[0])
            task_menu = ttk.Combobox(
                content, 
                textvariable=task_var, 
                values=active_tasks_list,
                width=45
            )
        else:
            task_var.set("")
            task_menu = ttk.Combobox(
                content, 
                textvariable=task_var,
                width=45
            )
        
        task_menu.pack(fill="x", pady=5)
        
        tk.Label(
            content, 
            text="Optional Notes:",
            font=("Arial", 10),
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).pack(anchor="w", pady=(10, 5))
        
        note_entry = tk.Entry(
            content, 
            width=45,
            font=("Arial", 10),
            bd=2,
            relief=tk.GROOVE
        )
        note_entry.pack(fill="x", pady=5)
        
        # Button frame
        button_frame = tk.Frame(content, bg=COLORS["background"])
        button_frame.pack(fill="x", pady=(15, 0))
        
        def on_submit():
            selected = task_var.get().strip()
            note = note_entry.get().strip()
            
            if not selected:
                messagebox.showwarning("Warning", "Please select a task")
                return
            
            # Find active tasks with this description
            mask = (self.df["Task Description"] == selected) & (self.df["Active"] == 1)
            
            if not any(mask):
                messagebox.showinfo("Task Not Found", f"No active task found with name: {selected}")
                dialog.destroy()
                return
            
            stop_time = datetime.now()
                
            # Update tasks
            self.df.loc[mask, "Completed"] = "Yes"
            self.df.loc[mask, "Active"] = 0
            self.df.loc[mask, "Stop Time"] = stop_time.strftime("%Y-%m-%d %H:%M")
            
            # Calculate duration for each matching task row
            for idx in self.df[mask].index:
                try:
                    start_time = datetime.strptime(self.df.at[idx, "Start Time"], "%Y-%m-%d %H:%M")
                    duration = round((stop_time - start_time).total_seconds() / 60, 2)
                    self.df.at[idx, "Duration (min)"] = duration
                except (ValueError, TypeError):
                    pass
            
            if note:
                self.df.loc[mask, "Notes"] += f" | {note}"
            
            self.save_data()
            messagebox.showinfo("Finished", f"Marked '{selected}' as completed.")
            dialog.destroy()
            self.refresh_history()
        
        # Create the buttons
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            bg=COLORS["secondary"],
            fg=COLORS["text"],
            font=("Arial", 10),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
        )
        cancel_button.pack(side="left", padx=5)
        
        complete_button = tk.Button(
            button_frame,
            text="Complete",
            command=on_submit,
            bg=COLORS["primary"],
            fg=COLORS["background"],
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=20,
            pady=5
        )
        complete_button.pack(side="right", padx=5)
    
    def generate_markdown_content(self, days=7):
        """Generate markdown content for reports"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        temp_df = self.df.copy()
        temp_df["Start Time"] = pd.to_datetime(temp_df["Start Time"], errors='coerce')
        temp_df["Stop Time"] = pd.to_datetime(temp_df["Stop Time"], errors='coerce')
        
        recent = temp_df[temp_df["Start Time"].between(start_date, end_date)]
        recent = recent.sort_values(by="Start Time")
        
        # Create completed and in-progress task dataframes
        completed_tasks = recent[recent["Active"] == 0]
        pending_tasks = recent[recent["Active"] != 1]
        
        export_date = datetime.now().strftime("%Y-%m-%d")
        lines = ["# 📋 5-15\n"]
        lines.append("### Name: [InsertName]")
        lines.append(f"### Week Ending: {export_date}\n")
        
        # Accomplishments section
        lines.append("## Accomplishments this week")
        
        if not completed_tasks.empty:
            # Group completed tasks by description
            completed_grouped = completed_tasks.groupby("Task Description")
            
            for task, group in completed_grouped:
                lines.append(f"### ✅ {task}")
                
                for _, row in group.iterrows():
                    stop_time = row["Stop Time"]
                    start_time = row["Start Time"]
                    
                    timestamp = (
                        stop_time.strftime("%Y-%m-%d %H:%M")
                        if pd.notna(stop_time)
                        else start_time.strftime("%Y-%m-%d %H:%M")
                    )
                    duration = f"{row['Duration (min)']} min" if pd.notna(row["Duration (min)"]) else "-"
                    note = str(row["Notes"]) if pd.notna(row["Notes"]) else ""
                    # note_snippet = (note[:100] + "...") if len(note) > 100 else note
                    # note_text = f"📝 {note_snippet}" if note_snippet else ""
                    
                    lines.append(
                        f"- [NEW: {timestamp}] Completed: duration of {duration}; {note}"
                    )
                
                lines.append("")  # Add a blank line between task groups
        else:
            lines.append("*No completed tasks this week*\n")
        
        # Priorities section
        lines.append("## Priorities next week")
        
        if not pending_tasks.empty:
            # Group pending tasks by description
            pending_grouped = pending_tasks.groupby("Task Description")
            
            for task, group in pending_grouped:
                icon = "🟡"  # In progress icon
                lines.append(f"### {icon} {task}")
                
                for _, row in group.iterrows():
                    stop_time = row["Stop Time"]
                    start_time = row["Start Time"]
                    
                    timestamp = (
                        stop_time.strftime("%Y-%m-%d %H:%M")
                        if pd.notna(stop_time)
                        else start_time.strftime("%Y-%m-%d %H:%M")
                    )
                    status = "Stopped" if pd.notna(stop_time) else "In Progress"
                    ##duration = f"{row['Duration (min)']} min" if pd.notna(row["Duration (min)"]) else "-"
                    note = str(row["Notes"]) if pd.notna(row["Notes"]) else ""
                    # note_snippet = (note[:100] + "...") if len(note) > 100 else note
                    # note_text = f"📝 {note_snippet}" if note_snippet else ""
                    
                    lines.append(
                        f"- [NEW: {timestamp}] {status}: duration of {duration}; {note}"
                    )
                
                lines.append("")  # Add a blank line between task groups
        else:
            lines.append("*No pending tasks for next week*\n")
        
        return "\n".join(lines)
    
    def preview_markdown(self):
        """Preview markdown content in browser"""
        try:
            md_content = self.generate_markdown_content()
            
            # Convert to HTML
            html = markdown.markdown(md_content)
            
            # Save as temp HTML file
            temp_html = f"temp_preview_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; color: #333; }}
                        h1 {{ color: #2c3e50; border-bottom: 2px solid #4287f5; padding-bottom: 10px; }}
                        h2 {{ color: #34495e; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 30px; }}
                        h3 {{ color: #3498db; margin-top: 20px; }}
                        ul {{ padding-left: 20px; }}
                        li {{ margin-bottom: 10px; }}
                        .timestamp {{ color: #777; font-style: italic; }}
                        .note {{ background-color: #f8f9fa; padding: 5px 10px; border-left: 3px solid #4287f5; margin-top: 5px; }}
                    </style>
                </head>
                <body>
                    {html}
                </body>
                </html>
                """)
            
            # Open in default browser
            webbrowser.open(temp_html)
        except Exception as e:
            messagebox.showerror("Preview Error", f"Error generating preview: {str(e)}")
    
    def export_to_markdown(self):
        """Export tasks to markdown file"""
        try:
            md_content = self.generate_markdown_content()
            
            date_str = datetime.now().strftime("%Y-%m-%d")
            output_path = f"exports/{date_str}_weekly_summary.md"

            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            
            messagebox.showinfo("Markdown Exported", f"Markdown summary saved to {output_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting to markdown: {str(e)}")
    
    def summarize_tasks(self):
        """Generate a CSV summary of tasks"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            temp_df = self.df.copy()
            temp_df["Start Time"] = pd.to_datetime(temp_df["Start Time"], errors='coerce')
            weekly = temp_df[temp_df["Start Time"].between(start_date, end_date)]
            
            date_str = datetime.now().strftime("%Y-%m-%d")
            summary_file = f"{date_str}_weekly_summary.csv"
            weekly.to_csv(summary_file, index=False)
            
            messagebox.showinfo("Summary Created", f"Weekly summary saved to {summary_file}")
        except Exception as e:
            messagebox.showerror("Summary Error", f"Error creating summary: {str(e)}")

def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        app = TaskLogger(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()