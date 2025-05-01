# views/main_view.py

import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import pandas as pd

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
        self.dialog_factory = TaskDialogFactory(self.root, self.task_controller)
        
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
        min_width = 700
        min_height = 550  # Reduced minimum height
        self.root.minsize(min_width, min_height)

    def setup_logging(self):
        """Set up the initial log file."""
        log_file_path = "exports/task_history.log"  # Path to the log file

        # Use the task_controller to fetch the DataFrame
        df = self.task_controller.model.get_tasks()  # Fetch all tasks from the model

        # Define a formatting function for timestamps
        format_func = lambda ts: ts.strftime("%Y-%m-%d %H:%M") if pd.notna(ts) else "No timestamp"

        # Call _create_initial_log with the fetched DataFrame
        self._create_initial_log(log_file_path, df, format_func)   

    def _create_header_frame(self):
        """Create the header frame with title and controls"""
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
        min_width = 12  # Set a minimum width for buttons
        
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

        finish_button = tk.Button(
            button_frame, 
            text="Finish Task", 
            command=self._show_finish_task_dialog,
            bg=COLORS["primary"],
            fg=COLORS["background"], 
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5,
            width=min_width  # Set minimum width
        )
        finish_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

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
        show_active_tasks.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
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
        show_inactive_tasks.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
    
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
        preview_button.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")  # Note the columnspan=4
    
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

        self.history_text.bind("<Double-1>", self._show_task_notes)


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
    
    def refresh_history(self):
        """
        Refresh the task history display with proper filtering for notes
        """
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)

        try:
            # Get recent tasks
            task_model = self.task_controller.model
            sorted_df = task_model.get_recent_tasks(days=7, limit=25)
            
            # Apply current filter
            if self.current_filter == "active":
                filtered_df = sorted_df[sorted_df["Active"] == 1]
                self.history_text.insert(tk.END, "Showing active tasks only\n\n", "active")
            elif self.current_filter == "finished":
                filtered_df = sorted_df[sorted_df["Active"] == 0]
                self.history_text.insert(tk.END, "Showing finished tasks only\n\n", "completed")
            else:
                filtered_df = sorted_df
                # If showing all tasks, add a summary of active tasks
                active_count = len(sorted_df[sorted_df["Active"] == 1])
                if active_count > 0:
                    self.history_text.insert(tk.END, f"You have {active_count} active task(s)\n\n", "active")

            # Format the timestamp safely
            def format_timestamp(ts):
                if pd.notna(ts) and ts:
                    try:
                        # If it's already a string, return it
                        if isinstance(ts, str):
                            return ts
                        # If it's a datetime, format it
                        return ts.strftime("%Y-%m-%d %H:%M")
                    except (AttributeError, ValueError):
                        return "Invalid timestamp"
                return "No timestamp"

            # Create a list of all entries for chronological sorting
            entries = []

            # Process each task and create entries
            for _, row in filtered_df.iterrows():
                desc = row["Task Description"]
                start_time = row["Start Time"]
                stop_time = row["Stop Time"]
                updated = row["Updated"] if pd.notna(row["Updated"]) else None
                active = row["Active"] == 1

                # Parse timestamps to datetime objects for sorting
                start_time_obj = pd.to_datetime(start_time, errors='coerce')
                stop_time_obj = pd.to_datetime(stop_time, errors='coerce')
                updated_obj = pd.to_datetime(updated, errors='coerce') if updated else None

                # Add start entry only if we're showing all tasks or active tasks
                if self.current_filter == "all" or self.current_filter == "active":
                    entries.append({
                        'timestamp': start_time_obj,
                        'timestamp_str': format_timestamp(start_time),
                        'icon': "⏩",
                        'status': "In Progress",
                        'desc': desc,
                        'tag': "active"
                    })

                # Add completion entry if task is completed
                if not active and pd.notna(stop_time):
                    entries.append({
                        'timestamp': stop_time_obj,
                        'timestamp_str': format_timestamp(stop_time),
                        'icon': "⏹️",
                        'status': "Completed",
                        'desc': desc,
                        'tag': "completed"
                    })

                # Add note entry if it exists and we're showing all tasks
                if self.current_filter == "all" and updated and (pd.isna(stop_time) or updated != stop_time):
                    entries.append({
                        'timestamp': updated_obj,
                        'timestamp_str': format_timestamp(updated),
                        'icon': "ℹ️",
                        'status': "Notes Updated",
                        'desc': desc,
                        'tag': "note"
                    })

            # Sort entries by timestamp (newest first)
            # Handle NaT values safely
            entries.sort(key=lambda x: (x['timestamp'] if x['timestamp'] is not pd.NaT and pd.notna(x['timestamp']) 
                                    else pd.Timestamp.min), reverse=True)

            # Display all entries
            for entry in entries:
                display_text = f"{entry['icon']} {entry['timestamp_str']} - {entry['status']} - {entry['desc']}\n"
                self.history_text.insert(tk.END, display_text, entry['tag'])

        except Exception as e:
            import traceback
            error_message = f"Error refreshing history: {str(e)}\n"
            self.history_text.insert(tk.END, error_message)
            self.history_text.insert(tk.END, traceback.format_exc())

        self.history_text.config(state="disabled")

    def _create_initial_log(self, log_file_path, df, format_func):
        """
        Create the initial log file from existing data if it does not already exist.
        """
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
                
                # Create a new DataFrame for all events to sort chronologically
                events = []
                
                # Process active tasks (start times)
                active_tasks = df[df["Active"] == 1].copy()
                for _, row in active_tasks.iterrows():
                    events.append({
                        "timestamp": row["Start Time"],
                        "desc": row["Task Description"],
                        "event_type": "start",
                        "formatted_time": format_func(row["Start Time"]),
                        "emoji": "▶️",
                        "status": "In Progress"
                    })
                
                # Process completed tasks
                completed_tasks = df[df["Active"] == 0].copy()
                for _, row in completed_tasks.iterrows():
                    # Add start event for completed tasks
                    if pd.notna(row["Start Time"]):
                        events.append({
                            "timestamp": row["Start Time"],
                            "desc": row["Task Description"],
                            "event_type": "start",
                            "formatted_time": format_func(row["Start Time"]),
                            "emoji": "▶️",
                            "status": "Started"
                        })
                    
                    # Add completion event
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
                    events.append({
                        "timestamp": row["Updated"],
                        "desc": row["Task Description"],
                        "event_type": "update",
                        "formatted_time": format_func(row["Updated"]),
                        "emoji": "ℹ️",
                        "status": "Notes Updated"
                    })
                
                # Convert to DataFrame and sort chronologically (newest first)
                events_df = pd.DataFrame(events)
                if not events_df.empty:
                    events_df = events_df.sort_values(by="timestamp", ascending=False)
                    
                    # Write all events in chronological order
                    log_file.write("## Task History\n\n")
                    for _, event in events_df.iterrows():
                        log_file.write(f"{event['emoji']} {event['formatted_time']}: - {event['status']} - {event['desc']}\n\n")
                else:
                    log_file.write("## No Task History\n\nNo tasks have been recorded yet.\n\n")
                    
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
    def _show_start_task_dialog(self):
        """Show dialog to start a new task"""
        self.dialog_factory.create_start_task_dialog(self.refresh_history)
    
    def _show_finish_task_dialog(self):
        """Show dialog to finish a task"""
        self.dialog_factory.create_finish_task_dialog(self.refresh_history)

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
            dialog.destroy()
            self.refresh_history()

        def add_notes_to_selected_tasks():
            selected_indices = task_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select at least one task.")
                return

            selected_tasks = [task_listbox.get(i) for i in selected_indices]
            for task in selected_tasks:
                note = simpledialog.askstring("Add Note", f"Enter a note for task: {task}")
                if note:
                    task_indices = self.task_controller.model.get_tasks(task_description=task).index
                    for idx in task_indices:
                        # Pass the current timestamp to update the "Updated" field
                        current_time = datetime.now()
                        self.task_controller.update_task_notes(task, note, current_time)

            messagebox.showinfo("Success", "Notes have been added to the selected tasks.")
            dialog.destroy()
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
    
    def _export_to_markdown(self):
        """Export tasks to markdown file"""
        success, result = self.report_controller.export_to_markdown()
        if success:
            messagebox.showinfo("Markdown Exported", f"Markdown summary saved to {result}")
        else:
            messagebox.showerror("Export Error", result)
    
    def _show_task_notes(self, event):
        """Display all notes for the double-clicked task."""
        try:
            index = self.history_text.index("@%s,%s linestart" % (event.x, event.y))
            line_content = self.history_text.get(index, "%s lineend" % index)
            task_description = line_content.rsplit("-", 1)[-1].strip()

            notes = self.task_controller.get_task_notes(task_description)

            dialog, content = self.dialog_factory.create_dialog(f"Notes for {task_description}", 400, 300)

            # Create the text widget with monospaced font
            notes_text = tk.Text(
                content,
                wrap="word",
                state="normal",
                bg=COLORS["background"],
                fg=COLORS["text"],
                font=("Arial", 10),  # Monospaced font
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