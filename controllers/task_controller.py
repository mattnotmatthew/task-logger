# controllers/task_controller.py

import os
import uuid
from datetime import datetime
from tkinter import ttk, messagebox, simpledialog

class TaskController:
    def __init__(self, task_model):
        """
        Initialize a task controller with a reference to the data model
        
        Args:
            task_model: The data model for tasks
        """
        self.model = task_model
    
    def get_active_tasks(self):
        """
        Get list of currently active tasks with their start times
        
        Returns:
            List of tuples (start_time, task_description) ordered by Start Time descending
        """
        active = self.model.get_tasks(active=True)
        active = active.sort_values(by="Start Time", ascending=True)
        return [(row["Start Time"], row["Task Description"]) for _, row in active.iterrows()]
    
    def get_finished_tasks(self):
        """
        Get list of currently inactive tasks
        
        Returns:
            List of tuples (start_time, task_description) ordered by Start Time ascending
        """
        inactive = self.model.get_tasks(active=False, completed=True)
        inactive = inactive.sort_values(by="Start Time", ascending=True)
        return [(row["Start Time"], row["Task Description"]) for _, row in inactive.iterrows()]
    
    def start_task(self, task_description, notes=""):
        """
        Start a new task or add notes to an existing active task
        
        Args:
            task_description: Description of the task
            notes: Optional notes to add
            
        Returns:
            Tuple of (success, message)
        """
        task_description = task_description.strip()
        
        if not task_description:
            return False, "Please enter a task description"
        
        # Check if task is already active
        active_tasks = self.model.get_tasks(
            active=True, 
            task_description=task_description
        )
        
        if not active_tasks.empty:
            # Task is already active, add notes
            idx = active_tasks.index[-1]
            if notes:
                self.model.add_notes(idx, notes)
            return True, f"Task '{task_description}' is already active. Note added."
        
        # Create a new task
        task_id = str(uuid.uuid4())
        start_time = datetime.now()
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M")
        new_task = {
            "Task ID": task_id,
            "Task Description": task_description,
            "Start Time": start_time_str,
            "Stop Time": "",
            "Duration (min)": "",
            "Completed": "No",
            "Notes": notes or "",
            "Active": 1
           
        }
        
        self.model.add_task(new_task)
        
        # Log the task start
        self._append_to_log(f"▶️ {start_time_str}: - In Progress - {task_description}\n\n")
        
        return True, f"Started task: {task_description}"
    
    def stop_task(self, task_description, notes=""):
        """
        Stop an active task
        
        Args:
            task_description: Description of the task
            notes: Optional notes to add
            
        Returns:
            Tuple of (success, message, duration)
        """
        task_description = task_description.strip()
        
        if not task_description:
            return False, "Please select a task", None
        
        # Find active task rows
        active_tasks = self.model.get_tasks(
            active=True, 
            task_description=task_description
        )
        
        if active_tasks.empty:
            return False, "No active task found with that name", None
        
        # Get most recent active task
        idx = active_tasks.index[-1]
        stop_time = datetime.now()
        stop_time_str = stop_time.strftime("%Y-%m-%d %H:%M")
        
        # Calculate duration
        try:
            start_time = datetime.strptime(self.model.get_value(idx, "Start Time"), "%Y-%m-%d %H:%M")
            duration = round((stop_time - start_time).total_seconds() / 60, 2)
        except (ValueError, TypeError):
            duration = 0
        
        # Update task
        self.model.update_task(idx, {
            "Stop Time": stop_time_str,
            "Duration (min)": duration,
            "Active": 0,
            "Updated": stop_time_str
        })
        
        if notes:
            self.model.add_notes(idx, notes, stop_time)
        
        # Log the task stop
        self._append_to_log(f"✅ {stop_time_str}: - Completed - {task_description} ({duration} min)\n\n")
            
        return True, f"Stopped task: {task_description} ({duration} min)", duration
    
    def finish_task(self, task_description, notes=""):
        """
        Mark an active task as completed
        
        Args:
            task_description: Description of the task
            notes: Optional notes to add
            
        Returns:
            Tuple of (success, message)
        """
        task_description = task_description.strip()
        
        if not task_description:
            return False, "Please select a task"
            
        # Find active tasks with this description
        mask = (self.model.df["Task Description"] == task_description) & (self.model.df["Active"] == 1)
        
        if not any(mask):
            return False, f"No active task found with name: {task_description}"
        
        stop_time = datetime.now()
        stop_time_str = stop_time.strftime("%Y-%m-%d %H:%M")
        
        # Update all matching tasks
        indices = self.model.df[mask].index
        for idx in indices:
            # Calculate duration
            try:
                start_time = datetime.strptime(self.model.get_value(idx, "Start Time"), "%Y-%m-%d %H:%M")
                duration = round((stop_time - start_time).total_seconds() / 60, 2)
            except (ValueError, TypeError):
                duration = 0

            self.model.update_task(idx, {
                "Stop Time": stop_time_str,
                "Duration (min)": duration,
                "Completed": "Yes",
                "Active": 0,
                "Updated": stop_time_str
            })
            
            if notes:
                self.model.add_notes(idx, notes, stop_time)
                
            # Log the task completion
            self._append_to_log(f"✅ {stop_time_str}: - Completed - {task_description} ({duration} min)\n\n")
                
        return True, f"Marked '{task_description}' as completed."
        
    def update_task_notes(self, task_description, note, timestamp=None):
        """
        Update notes for a task
        
        Args:
            task_description: Description of the task to update
            note: Notes to add
            timestamp: Timestamp for the update
            
        Returns:
            Boolean indicating success
        """
        try:
            print(f"Updating notes for: '{task_description}'")
            
            # Find the task by description
            task_df = self.model.get_tasks(task_description=task_description)
            
            if task_df.empty:
                print(f"No tasks found matching description: '{task_description}'")
                return False
            
            print(f"Found {len(task_df)} matching tasks")
            
            # Update the first matching task (should be unique)
            task_idx = task_df.index[0]
            
            current_time = timestamp or datetime.now()
            current_time_str = current_time.strftime("%Y-%m-%d %H:%M")
            
            print(f"Adding note: '{note}' with timestamp: {current_time_str}")
            
            # Add note with timestamp
            success = self.model.add_notes(task_idx, note, current_time)
            
            # Log the note update
            if success:
                print("Note added successfully")
                self._append_to_log(f"ℹ️ {current_time_str}: - Notes Added - {task_description}\n\n")
            else:
                print("Failed to add note")
            
            return success
        except Exception as e:
            print(f"Error updating task notes: {e}")
            import traceback
            traceback.print_exc()
            return False  
            
    # def update_task_notes(self, task_description, note, timestamp=None):
    #     """
    #     Update notes for a task
        
    #     Args:
    #         task_description: Description of the task to update
    #         note: Notes to add
    #         timestamp: Timestamp for the update
            
    #     Returns:
    #         Boolean indicating success
    #     """
    #     try:
    #         # Find the task by description
    #         task_df = self.model.get_tasks(task_description=task_description)
            
    #         if task_df.empty:
    #             return False
            
    #         # Update the first matching task (should be unique)
    #         task_idx = task_df.index[0]
            
    #         current_time = timestamp or datetime.now()
    #         current_time_str = current_time.strftime("%Y-%m-%d %H:%M")
            
    #         # Add note with timestamp
    #         success = self.model.add_notes(task_idx, note, current_time)
            
    #         # Log the note update
    #         if success:
    #             self._append_to_log(f"ℹ️ {current_time_str}: - Notes Added - {task_description}\n\n")
            
    #         return success
    #     except Exception as e:
    #         print(f"Error updating task notes: {e}")
    #         return False
    
    def get_task_notes(self, task_description):
        """Fetch all notes for a given task description."""
        tasks = self.model.get_tasks(task_description=task_description)
        if tasks.empty:
            return "No notes available."

        notes = tasks["Notes"].dropna().tolist()
        return "\n".join(f"> {note.replace(' | ', '\n> ').strip()}" for note in notes)
    
    def _append_to_log(self, entry):
        """
        Append an entry to the task history log file
        
        Args:
            entry: Text entry to append
        """
        try:
            log_file_path = os.path.join("exports", "task_history.log")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            
            # Append to the log file
            with open(log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {entry}")
        except Exception as e:
            print(f"Error appending to log: {e}")