# views/main_view.py

import tkinter as tk
from tkinter import ttk, messagebox
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
        self._create_export_section(content_frame)
        self._create_filter_section(content_frame)
        self._create_history_section(content_frame)
        
        # Add status bar at the bottom
        self._create_status_bar()
        
        # Set minimum window size to ensure all elements are visible
        self.root.update_idletasks()
        min_width = 500
        min_height = 1000  # Reduced minimum height
        self.root.minsize(min_width, min_height)
    
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
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Task action buttons
        start_button = tk.Button(
            button_frame, 
            text="Start Task", 
            command=self._show_start_task_dialog, 
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
            command=self._show_finish_task_dialog,
            bg=COLORS["primary"],
            fg=COLORS["background"], 
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
        )
        finish_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    def _create_export_section(self, parent):
        """Create the export/reporting section"""
        export_frame = tk.LabelFrame(
            parent, 
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
            command=self._preview_report,
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
            command=self._export_to_markdown,
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
            command=self._generate_csv_summary,
            bg=COLORS["primary"],
            fg=COLORS["background"],
            font=("Arial", 10),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5
        )
        summary_button.pack(fill="x", pady=5)
    
    def _create_filter_section(self, parent):
        """Create the task filter section"""
        filter_frame = tk.LabelFrame(
            parent,
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
        """Refresh the task history display"""
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        
        try:
            # Get recent tasks
            task_model = self.task_controller.model
            sorted_df = task_model.get_recent_tasks(days=7, limit=25)

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
            for _, row in sorted_df.iterrows():
                desc = row["Task Description"]
                start_time = row["Start Time"]
                stop_time = row["Stop Time"]
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
    
    # Dialog methods
    def _show_start_task_dialog(self):
        """Show dialog to start a new task"""
        self.dialog_factory.create_start_task_dialog(self.refresh_history)
    
    def _show_finish_task_dialog(self):
        """Show dialog to finish a task"""
        self.dialog_factory.create_finish_task_dialog(self.refresh_history)
    
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
    
    def _generate_csv_summary(self):
        """Generate a CSV summary of tasks"""
        success, result = self.report_controller.summarize_tasks()
        if success:
            messagebox.showinfo("Summary Created", f"Weekly summary saved to {result}")
        else:
            messagebox.showerror("Summary Error", result)