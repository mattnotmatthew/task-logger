# controllers/task_controller.py

import uuid
from datetime import datetime

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
        Get list of currently active tasks
        
        Returns:
            List of unique active task descriptions
        """
        active = self.model.get_tasks(active=True)
        return sorted(active["Task Description"].unique())
    
    def get_inactive_tasks(self):
        """
        Get list of currently inactive tasks
        
        Returns:
            List of unique inactive task descriptions
        """
        inactive = self.model.get_tasks(active=False, completed=False)
        return sorted(inactive["Task Description"].unique())
    
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
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_task = {
            "Task ID": task_id,
            "Task Description": task_description,
            "Start Time": start_time,
            "Stop Time": "",
            "Duration (min)": "",
            "Completed": "No",
            "Notes": notes or "",
            "Active": 1
        }
        
        self.model.add_task(new_task)
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
        
        # Calculate duration
        try:
            start_time = datetime.strptime(self.model.get_value(idx, "Start Time"), "%Y-%m-%d %H:%M")
            duration = round((stop_time - start_time).total_seconds() / 60, 2)
        except (ValueError, TypeError):
            duration = 0
        
        # Update task
        self.model.update_task(idx, {
            "Stop Time": stop_time.strftime("%Y-%m-%d %H:%M"),
            "Duration (min)": duration,
            "Active": 0
        })
        
        if notes:
            self.model.add_notes(idx, notes)
            
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
                "Active": 0
            })
            
            if notes:
                self.model.add_notes(idx, notes)
                
        return True, f"Marked '{task_description}' as completed."