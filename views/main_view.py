# views/main_view.py

import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import pandas as pd
import uuid


# Import from other modules
from constants import VERSION, COLORS
from views.dialog_view import TaskDialogFactory


class MainView:
    """
    Main application view that handles the UI and user interactions
    """
    
    def __init__(self, root, task_controller, report_controller):
        """
        Initialize the main view
        
        Args:
            root: The root tkinter window
            task_controller: Controller for task operations
            report_controller: Controller for report operations
        """
        self.root = root
        self.task_controller = task_controller
        self.report_controller = report_controller
        self.dialog_factory = TaskDialogFactory(self.root, self.task_controller, self.report_controller)
        
        # Initialize always on top state variable
        self.always_on_top_var = tk.BooleanVar(value=True)
        
        # Initialize filter state variable
        self.current_filter = "all"  # Default to showing all tasks
        
        # Configure styles
        self.configure_styles()
        
        # Set up UI components
        self.setup_ui()
    
        # Apply always on top setting
        self.toggle_always_on_top()

        # setup logging
        self.setup_logging()
        
        # Refresh history on load
        self.refresh_history(True)
        

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
    
    def setup_ui(self):
        """Set up the user interface components"""
        # Configure the root window to use grid
        self.root.configure(bg=COLORS["background"])
        
        # Configure grid weights to make content area expandable
        self.root.grid_columnconfigure(0, weight=1)  # Makes column expandable
        self.root.grid_rowconfigure(1, weight=1)     # Makes content row expandable
        
        # Create a header frame
        self._create_header_frame()
        
        # Main content area - will expand/contract with window
        content_frame = tk.Frame(self.root, bg=COLORS["background"], padx=15, pady=15)
        content_frame.grid(row=1, column=0, sticky="nsew")  # nsew = fill in all directions
        
        # Add components to content frame
        self._create_actions_section(content_frame)
        self._create_history_section(content_frame)
        
        # Add status bar at the bottom
        self._create_status_bar()
        
        # Set minimum window size to ensure all elements are visible
        self.root.update_idletasks()
        min_width = 775
        min_height = 550  # Reduced minimum height
        self.root.minsize(min_width, min_height)

    def setup_logging(self):
        """Set up the initial log file."""
        log_file_path = "exports/task_history.log"  # Path to the log file

        # Use the task_controller to fetch the DataFrame
        df = self.task_controller.model.get_tasks()  # Fetch all tasks from the model

        # Define a formatting function for timestamps
        format_func = lambda ts: pd.to_datetime(ts).strftime("%Y-%m-%d %H:%M") if pd.notna(ts) else "No timestamp"

        # # Create the log file if it doesn't exist
        # if not os.path.exists(log_file_path):
        #     with open(log_file_path, "w", encoding="utf-8") as log_file:
        #         log_file.write(f"# Task Logger History - Created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        #         log_file.write("## Task History\n")

        # Create or update the log file with proper formatting
        self._create_initial_log(log_file_path, df, format_func)

    def log_exports_clear(self):
        """Create a log entry for clearing exports folder"""
        task_id = str(uuid.uuid4())
        start_time = datetime.now()
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M")
        
        # Add to task database
        new_task = {
            "Task ID": task_id,
            "Task Description": "Clear exports folder",
            "Start Time": start_time_str,
            "Stop Time": start_time_str,
            "Duration (min)": "",
            "Completed": "Yes",
            "Notes": "HTML files cleared from exports folder",
            "Active": 0,
            "Updated": start_time_str
        }
        self.task_controller.model.add_task(new_task)
        
        # Log to history with consistent format
        log_entry = f"❌ {start_time_str}: - Clear Export Dir - Clear exports folder\n"
        self.task_controller._append_to_log(log_entry)
        

    def _create_header_frame(self):
        """Create the header frame with title and controls"""
        header_frame = tk.Frame(self.root, bg=COLORS["primary"], padx=10, pady=10)
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
    
    def _create_actions_section(self, parent):
        """Create the task actions section"""
        actions_frame = tk.LabelFrame(
            parent, 
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
        
        # Configure all columns to have equal weight
        for i in range(4):  # Assuming you have 4 columns
            button_frame.grid_columnconfigure(i, weight=1)
        
        # Task action buttons with minimum width
        min_width = 15  # Set a minimum width for buttons
        
        start_button = tk.Button(
            button_frame, 
            text="Start Task", 
            command=self._show_start_task_dialog, 
            bg=COLORS["primary"],
            fg=COLORS["background"],
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5,
            width=min_width  # Set minimum width
        )
        start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        show_active_tasks = tk.Button(
            button_frame, 
            text="View Active Tasks", 
            command=self._show_tasks_window, 
            bg=COLORS["primary"],
            fg=COLORS["background"], 
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5,
            width=min_width  # Set minimum width
        )
        show_active_tasks.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        show_inactive_tasks = tk.Button(
            button_frame, 
            text="View Completed Tasks", 
            command=lambda: self._show_tasks_window("finished"), 
            bg=COLORS["primary"],
            fg=COLORS["background"], 
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5,
            width=min_width  # Set minimum width
        )
        show_inactive_tasks.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    
        # Preview button spanning all columns
        preview_button = tk.Button(
            button_frame,
            text="Generate Weekly Report",
            command=self._preview_report,
            bg=COLORS["success"],
            fg=COLORS["background"],
            font=("Arial", 10,"bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
        )
        preview_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")  # Note the columnspan=4

        # Preview button spanning all columns
        regenerate_preview = tk.Button(
            button_frame,
            text="Regenerate Preview",
            command=self._show_regen_preview_report,
            bg=COLORS["success"],
            fg=COLORS["background"],
            font=("Arial", 10,"bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
        )
        regenerate_preview.grid(row=1, column=1, padx=5, pady=5, sticky="ew")  # Note the columnspan=4

        
        clear_exports_folder = tk.Button(
            button_frame, 
            text="Clear Exports Folder", 
            command=self._clear_exports_folder,
            bg=COLORS["critical_action"],
            fg=COLORS["background"], 
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5,

            width=min_width  # Set minimum width
        )
        clear_exports_folder.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
    
    def _create_history_section(self, parent):
        """Create the task history section"""
        history_frame = tk.LabelFrame(
            parent,
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

        # Add filter buttons directly to the history frame
        button_frame = tk.Frame(history_frame, bg=COLORS["background"])
        button_frame.pack(fill="x", pady=(0, 0))

        self.all_button = tk.Button(
            button_frame,
            text="All History",
            command=lambda: self.filter_tasks("all"),
            bg=COLORS["primary"],
            fg=COLORS["background"],
            font=("Arial", 10),
            relief=tk.FLAT,
            borderwidth=2,
            padx=5,
            pady=5
        )
        self.all_button.grid(row=0, column=0, padx=2, pady=5, sticky="ew")

        self.active_button = tk.Button(
            button_frame,
            text="In Progress",
            command=lambda: self.filter_tasks("active"),
            bg=COLORS["secondary"],
            fg=COLORS["text"],
            font=("Arial", 10),
            relief=tk.FLAT,
            borderwidth=2,
            padx=5,
            pady=5
        )
        self.active_button.grid(row=0, column=1, padx=2, pady=5, sticky="ew")

        self.finished_button = tk.Button(
            button_frame,
            text="Completed",
            command=lambda: self.filter_tasks("finished"),
            bg=COLORS["secondary"],
            fg=COLORS["text"],
            font=("Arial", 10),
            relief=tk.FLAT,
            borderwidth=2,
            padx=5,
            pady=5
        )
        self.finished_button.grid(row=0, column=2, padx=2, pady=5, sticky="ew")

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

        # Configure text tags for colored text in history
        self.history_text.tag_configure("completed", foreground=COLORS["success"])
        self.history_text.tag_configure("stopped", foreground=COLORS["warning"])
        self.history_text.tag_configure("active", foreground=COLORS["primary"])
        self.history_text.tag_configure("timestamp", foreground=COLORS["light_text"], font=(history_font[0], history_font[1], "italic"))
        self.history_text.tag_configure("note", foreground=COLORS["light_text"])
        self.history_text.tag_configure("notes_only", foreground=COLORS["sidebar"])
        self.history_text.tag_configure("export", foreground=COLORS["critical_action"])  # Use critical action color for export entries

       
    def _create_status_bar(self):
        """Create the status bar at the bottom of the window"""
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
            text="🔃Refresh",
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
    
    def toggle_always_on_top(self):
        """Toggle always-on-top state"""
        self.root.attributes("-topmost", self.always_on_top_var.get())
    
    def filter_tasks(self, filter_type):
        """
        Filter tasks by status: all, active, or finished
        
        Args:
            filter_type: The type of filter to apply
        """
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
    
    def refresh_history(self, clear_exports=False):
        """Refresh the task history display directly from the log file."""
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)

        try:
            log_file_path = "exports/task_history.log"
            if not os.path.exists(log_file_path):
                self.history_text.insert(tk.END, "No task history available.\n")
                self.history_text.config(state="disabled")
                return

            entries = []
            with open(log_file_path, "r", encoding="utf-8") as log_file:
                for line in log_file:
                    if not line.strip() or line.startswith("#"):  # Skip empty lines and headers
                        continue
                    
                    # Parse the log entry
                    try:
                        # Format is: emoji timestamp: - status - description
                        if ":" not in line or " - " not in line:
                            continue

                        # Split on the colon first to separate emoji+timestamp from the rest
                        timestamp_part, rest = line.split(" - ", 1)
                        # Explicitly strip leading/trailing whitespace from timestamp_part
                        timestamp_part = timestamp_part.strip()
                        timestamp_str = timestamp_part[1:].strip()  # Extract timestamp after the emoji
                    
                        
                        if " - " not in rest:
                            continue
                            
                       # Split the rest into status and description
                        parts = rest.strip().split(" - ",1)

                            
                        status = parts[0].strip()
                        desc = parts[1].strip()
                       

                        # Extract emoji and timestamp
                        emoji = timestamp_part[0]  # First character should be emoji
                        
                        
                        # Determine the entry type and tag based on status
                        tag = "completed"
                        if "In Progress" in status:
                            tag = "active" 
                        elif "Notes" in status:
                            tag = "note"                            
                        elif "Clear Export Dir" in status:
                            tag = "export"
                            
                        print(f"Tag: {tag}")
                        # Parse the timestamp
                        try:
                            # print(f"Timestamp string: {timestamp_str}")
                            timestamp = pd.to_datetime(timestamp_str.strip())
                            # print(f"Parsed timestamp: {timestamp}")
                            # print(f"text: {line.strip()}")
                            # print (f"tag: {tag}")
                            # print (f"status: {status}") 
                            # print (f"desc: {desc}")

                            entries.append({
                                'timestamp': timestamp,
                                'text': line.strip(),
                                'tag': tag,
                                'status': status,
                                'desc': desc
                            })
                            
                        except Exception as e:
                            print(f"Inner parsing timestamp: {e}")
                            continue
                    
                    except Exception as e:
                        print(f"Error parsing log line: {e}")
                        continue

            # Sort entries by timestamp (newest first)
            entries.sort(key=lambda x: x['timestamp'], reverse=True)
           

            # Filter entries based on current filter
            filtered_entries = []
            
            if self.current_filter == "active":
                # For active filter, only show tasks that are In Progress and haven't been completed
                for entry in entries:
                    if entry['status'] == "In Progress":
                        filtered_entries.append(entry)
            elif self.current_filter == "all":
                # For "all" 
                for entry in entries:
                    filtered_entries.append(entry)
            else:
                for entry in entries:
                    if self.current_filter == "finished" and entry['tag'] not in ["active", "export","note"]:
                        filtered_entries.append(entry)
                    

            # Display count header
            if self.current_filter == "active":
                active_count = len(filtered_entries)
                self.history_text.insert(tk.END, f"You have {active_count} active task(s)\n\n", "active")
            elif self.current_filter == "finished":
                completed_count = len(filtered_entries)
                self.history_text.insert(tk.END, f"You have {completed_count} finished task(s)\n\n", "completed")
            else:
                all_count = len(filtered_entries)
                if all_count > 0:
                    self.history_text.insert(tk.END, f"You have {all_count} total task(s)\n\n", "active")

            # Display filtered entries
            for entry in filtered_entries:
                self.history_text.insert(tk.END, entry['text'] + "\n", entry['tag'])

        except Exception as e:
            import traceback
            error_message = f"Error refreshing history: {str(e)}\n"
            self.history_text.insert(tk.END, error_message)
            self.history_text.insert(tk.END, traceback.format_exc())

        self.history_text.config(state="disabled")

    def _create_initial_log(self, log_file_path, df, format_func):
        """Create the initial log file from existing data if it does not already exist."""
        try:
            # Check if the log file already exists
            if os.path.exists(log_file_path):
                print(f"Log file already exists at {log_file_path}. Skipping initial log creation.")
                return  # Exit the function if the file exists

            # Ensure relevant columns are converted to datetime
            for col in ["Start Time", "Stop Time", "Updated"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")

            # Create the log file
            with open(log_file_path, "w", encoding="utf-8") as log_file:
                log_file.write(f"# Task Logger History - Created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                log_file.write("## Task History\n\n")
                
                # Create a new DataFrame for all events to sort chronologically
                events = []
                
                # Process active tasks (start times)
                active_tasks = df[df["Active"] == 1].copy()
                for _, row in active_tasks.iterrows():
                    if row["Task Description"] != "Clear exports folder":  # Skip clear exports entries here
                        events.append({
                            "timestamp": row["Start Time"],
                            "desc": row["Task Description"],
                            "event_type": "start",
                            "formatted_time": format_func(row["Start Time"]),
                            "emoji": "➕",
                            "status": "In Progress"
                        })
                
                # Process completed tasks
                completed_tasks = df[df["Active"] == 0].copy()
                for _, row in completed_tasks.iterrows():
                    if row["Task Description"] == "Clear exports folder":
                        # Handle clear exports entries
                        events.append({
                            "timestamp": row["Start Time"],
                            "desc": "Clear exports folder",
                            "event_type": "export",
                            "formatted_time": format_func(row["Start Time"]),
                            "emoji": "❌",
                            "status": "Clear Export Dir"
                        })
                    else:
                        # # Add regular completed task events
                        # if pd.notna(row["Start Time"]):
                        #     events.append({
                        #         "timestamp": row["Start Time"],
                        #         "desc": row["Task Description"],
                        #         "event_type": "start",
                        #         "formatted_time": format_func(row["Start Time"]),
                        #         "emoji": "▶️",
                        #         "status": "Started"
                        #     })
                        
                        if pd.notna(row["Stop Time"]):
                            events.append({
                                "timestamp": row["Stop Time"],
                                "desc": row["Task Description"],
                                "event_type": "stop",
                                "formatted_time": format_func(row["Stop Time"]),
                                "emoji": "✅",
                                "status": "Completed"
                            })
                
                # Process note updates
                note_updates = df[pd.notna(df["Updated"])].copy()
                for _, row in note_updates.iterrows():
                    if row["Task Description"] != "Clear exports folder":  # Skip clear exports entries here
                        events.append({
                            "timestamp": row["Updated"],
                            "desc": row["Task Description"],
                            "event_type": "update",
                            "formatted_time": format_func(row["Updated"]),
                            "emoji": "⏫",
                            "status": "Notes Updated"
                        })
                
                # Convert to DataFrame and sort chronologically (newest first)
                events_df = pd.DataFrame(events)
                if not events_df.empty:
                    events_df = events_df.sort_values(by="timestamp", ascending=False)
                    
                    # Write all events in chronological order with single newlines
                    for _, event in events_df.iterrows():
                        log_file.write(f"{event['emoji']} {event['formatted_time']} - {event['status']} - {event['desc']}\n")
                else:
                    log_file.write("No tasks have been recorded yet.\n")
                    
        except Exception as e:
            print(f"Error creating initial log file: {e}")

    def _append_to_log(self, log_file_path, entry):
        """
        Append an entry to the task history log file
        
        Args:
            log_file_path: Path to the log file
            entry: Text entry to append
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            
            # Append to the log file
            with open(log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {entry}")
        except Exception as e:
            print(f"Error appending to log: {e}")

    
    # Dialog methods

    def _show_regen_preview_report (self):
        self.dialog_factory.create_regen_preview_report_dialog()


    def _show_start_task_dialog(self):
        """Show dialog to start a new task"""
        self.dialog_factory.create_start_task_dialog(self.refresh_history)
    
    # def function that clears out the exports folder of HTML files
    def _clear_exports_folder(self):
        """Clear the exports folder of HTML files and log the action."""
        exports_folder = "exports"
        if os.path.exists(exports_folder):
            cleared_files = False
            for filename in os.listdir(exports_folder):
                if filename.endswith(".html"):
                    file_path = os.path.join(exports_folder, filename)
                    try:
                        os.remove(file_path)
                        cleared_files = True
                        print(f"Deleted {file_path}")
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
            
            if cleared_files:
                # Log the action of clearing the exports folder
                self.log_exports_clear()
                messagebox.showinfo("Success", "Exports folder cleared.")
            else:
                messagebox.showinfo("Info", "No HTML files found to clear in the exports folder.")
        else:
            messagebox.showwarning("Warning", "Exports folder does not exist.")
        
        # Refresh the history to include the log entry
        self.refresh_history(True)

    def _show_tasks_window(self, task_type="active"):
        """Open a new window to manage active tasks."""

        # Fetch tasks based on task_type
        dialog_title = "Active Tasks" if task_type == "active" else "Finished Tasks"
        dialog, content = self.dialog_factory.create_dialog(dialog_title, 500, 400)
        if task_type == "active":
            tasks = self.task_controller.get_active_tasks()
        else:
            tasks = self.task_controller.get_finished_tasks()

        if not tasks:
            tk.Label(content, text="No active tasks available.", font=("Courier", 10), bg=COLORS["background"], fg=COLORS["text"]).pack(pady=20)
            return

        # Create a listbox for tasks
        task_listbox = tk.Listbox(content, selectmode=tk.MULTIPLE, bg=COLORS["background"], fg=COLORS["text"], font=("Courier", 10))
        task_listbox.pack(fill="both", expand=True, padx=10, pady=5)

        # Bind double-click event to the listbox
        task_listbox.bind("<Double-1>", lambda event: self._handle_task_listbox_double_click(event, task_listbox))

        # Populate the listbox with tasks
        for start_date, task_description in tasks:
            ## format start_date to be MM/DD/YYYY HH:MM AM/PM
            start_date = pd.to_datetime(start_date).strftime("%m/%d/%Y %I:%M %p")
            task_listbox.insert(tk.END, f"[{start_date}] - {task_description}")

        def close_selected_tasks():
            selected_indices = task_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select at least one task.")
                return

            selected_tasks = [task_listbox.get(i) for i in selected_indices]
            for task in selected_tasks:
                note = simpledialog.askstring("Closing Note", f"Add a note for task: {task}")
                self.task_controller.finish_task(task, note or "")
                messagebox.showinfo("Success", "Selected tasks have been closed.")
            # dialog.destroy()
            self.refresh_history()

        def add_notes_to_selected_tasks():
            selected_indices = task_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select at least one task.")
                return

            selected_tasks = [task_listbox.get(i) for i in selected_indices]
            for task_full in selected_tasks:
                # Extract just the task description (after the timestamp)
                task_description = task_full.split(" - ", 1)[1] if " - " in task_full else task_full

                note = simpledialog.askstring("Add Note", f"Enter a note for task: {task_description}")
                if note:
                    # Get tasks matching just the description part
                    matching_tasks = self.task_controller.model.get_tasks(task_description=task_description)
                    
                    if not matching_tasks.empty:
                        for idx in matching_tasks.index:
                            # Pass the current timestamp to update the "Updated" field
                            current_time = datetime.now()
                            self.task_controller.update_task_notes(task_description, note, current_time)
                            
                            # Add debug output to verify the task is being processed
                            print(f"Adding note to task: {task_description} at index {idx}")
                            messagebox.showinfo("Success", "Notes have been added to the selected tasks.")
            # dialog.destroy()
            # Remove notes_only=True to show the full history
            self.refresh_history()

        # Button frame
        button_frame = tk.Frame(content, bg=COLORS["background"])
        button_frame.pack(fill="x", pady=(15, 0))

        # Cancel button
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

        # Add Notes button
        add_notes_button = tk.Button(
            button_frame,
            text="Add Notes",
            command=add_notes_to_selected_tasks,
            bg=COLORS["primary"],
            fg=COLORS["background"],
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
        )
        add_notes_button.pack(side="left", padx=5)

        if task_type == "active":
            # Close All Selected Tasks button
            close_button = tk.Button(
            button_frame,
            text="Close All Selected Tasks",
            command=close_selected_tasks,
            bg=COLORS["danger"],
            fg=COLORS["background"],
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
            )
            close_button.pack(side="right", padx=5)
    
    # Report methods
    def _preview_report(self):
        """Preview markdown report in browser"""
        success, message = self.report_controller.preview_markdown()
        if not success:
            messagebox.showerror("Preview Error", message)

    def _regen_preview_report (self):
        """Preview markdown report in browser"""
        success, message = self.report_controller.preview_existing_markdown()
        if not success:
            messagebox.showerror("Preview Error", message)

    def _export_to_markdown(self):
        """Export tasks to markdown file"""
        success, result = self.report_controller.export_to_markdown()
        if success:
            messagebox.showinfo("Markdown Exported", f"Markdown summary saved to {result}")
        else:
            messagebox.showerror("Export Error", result)
    
    def _handle_task_listbox_double_click(self, event, listbox):
        """Handle double-click on a task in the task listbox"""
        try:
            # Get the selected index
            selected_index = listbox.nearest(event.y)
            if selected_index >= 0:
                # Get the task text
                task_text = listbox.get(selected_index)
                # Extract just the task description part (after the timestamp)
                task_description = task_text.split(" - ", 1)[1] if " - " in task_text else task_text
                # Call the existing method to show notes
                self._show_task_notes_from_description(task_description)
        except Exception as e:
            messagebox.showerror("Error", f"Could not show task notes: {str(e)}")

    def _show_task_notes_from_description(self, task_description):
        """Display notes for a task based on its description."""
        try:
            notes = self.task_controller.get_task_notes(task_description)
            dialog, content = self.dialog_factory.create_dialog(f"Notes for {task_description}", 500, 300)

            # Create the text widget with monospaced font
            notes_text = tk.Text(
                content,
                wrap="word",
                state="normal",
                bg=COLORS["background"],
                fg=COLORS["text"],
                font=("Arial", 10),
                relief=tk.SUNKEN,
                borderwidth=2,
                padx=5,
                pady=5
            )
            notes_text.insert("1.0", notes)
            notes_text.config(state="disabled")  # Make the text read-only
            notes_text.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch notes: {str(e)}")