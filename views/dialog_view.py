# views/dialog_view.py

import tkinter as tk
from tkinter import ttk, messagebox
from constants import COLORS

class TaskDialogFactory:
    """
    Factory class for creating consistent task dialogs
    """
    
    def __init__(self, parent, task_controller,report_controller):
        """
        Initialize the dialog factory
        
        Args:
            parent: Parent window
            task_controller: Controller for task operations
        """
        self.parent = parent
        self.task_controller = task_controller
        self.report_controller = report_controller
    
    def create_dialog(self, title, width=350, height=200):
        """
        Create a standard dialog window with consistent styling
        
        Args:
            title: Dialog title
            width: Dialog width
            height: Dialog height
            
        Returns:
            Tuple of (dialog window, content frame)
        """
        dialog = tk.Toplevel(self.parent)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        
        # Safer popup positioning
        self.parent.update_idletasks()
        main_x = self.parent.winfo_x()
        main_y = self.parent.winfo_y()
        main_w = self.parent.winfo_width()
        
        if main_x < 0 or main_y < 0:
            main_x = 100
            main_y = 100
        
        dialog.geometry(f"+{main_x + main_w + 10}+{main_y}")
        dialog.attributes("-topmost", True)
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
    
    def create_regen_preview_report_dialog(self, callback=None):
        """
        Create a dialog for regenerating a preview report
        
        Args:
            callback: Function to call after successful report generation
        """

        dialog, content = self.create_dialog("Regen Preview", 500, 400)
        # Build form
        tk.Label(
            content, 
            text="Select MD file to regen:",
            font=("Arial", 10, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).pack(anchor="w", pady=(0, 5))

        # Fetch tasks based on task_type
        mds = self.report_controller.list_markdown_files()

        if not mds:
            tk.Label(content, text="No active tasks available.", font=("Courier", 10), bg=COLORS["background"], fg=COLORS["text"]).pack(pady=20)
            return

        # Create a listbox for tasks
        mds_listbox = tk.Listbox(content, bg=COLORS["background"], fg=COLORS["text"], font=("Courier", 10))
        mds_listbox.pack(fill="both", expand=True, padx=10, pady=5)

        # Populate the listbox with markdown files
        for md_file in mds:
            mds_listbox.insert(tk.END, md_file)
        
        # Button frame
        button_frame = tk.Frame(content, bg=COLORS["background"])
        button_frame.pack(fill="x", pady=(15, 0))
        
        def on_submit():
            selected = mds_listbox.curselection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a MD file.")
                return

            selected_md = [mds_listbox.get(i) for i in selected]
          
            selected_md = selected_md[0].strip("[]'")
            print(f"Selected MD: {selected_md}")
            success, message = self.report_controller.preview_existing_markdown(selected_md)
            
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
                if callback:
                    callback()
            else:
                messagebox.showwarning("Warning", message)
        
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
    
    def create_start_task_dialog(self, callback=None):
        """
        Create a dialog for starting a new task
        
        Args:
            callback: Function to call after successful task creation
        """
        # Get inactive tasks for the dropdown
       ## inactive_tasks = self.task_controller.get_inactive_tasks() ## removed stop task functionality so no need to restart.
        
        # Create dialog
        dialog, content = self.create_dialog("Start Task")
        dialog.update_idletasks()  # Update geometry calculations
        dialog.geometry("")  # Let tkinter auto-size the dialog based on its content
        
        # Build form
        tk.Label(
            content, 
            text="Enter new task:",
            font=("Arial", 10, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).pack(anchor="w", pady=(0, 5))
        
        task_var = tk.StringVar()
              
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
            text="Notes:",
            font=("Arial", 10),
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).pack(anchor="w", pady=(10, 5))
        
        note_entry = tk.Text(
            content, 
            width=45,
            height=5,  # Set height for multiline input
            font=("Arial", 10),
            bd=2,
            relief=tk.GROOVE
        )
        note_entry.pack(fill="x", pady=5)

        def on_submit():
            """Handle task submission"""
            selected_task = task_var.get().strip()
            note = note_entry.get("1.0", tk.END).strip()  # Get multiline text
            
            success, message = self.task_controller.start_task(selected_task, note)
            
            if success:
                messagebox.showinfo("Success", message)
                # dialog.destroy()
                if callback:
                    callback()
            else:
                messagebox.showwarning("Warning", message)
        
        # Button frame
        button_frame = tk.Frame(content, bg=COLORS["background"])
        button_frame.pack(fill="x", pady=(15, 0))
        
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
            
