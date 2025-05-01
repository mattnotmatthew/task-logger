# models/task_model.py

import os
import pandas as pd
from datetime import datetime
from tkinter import ttk, messagebox, simpledialog

class TaskModel:
    """
    Data model for task management
    
    Handles all data operations including loading, saving, 
    and querying task data.
    """
    
    def __init__(self, csv_file):
        """
        Initialize the task model
        
        Args:
            csv_file: Path to the CSV file for data storage
        """
        self.csv_file = csv_file
        self.df = None
        self.load_data()
        
    def load_data(self):
        """
        Load data from CSV or create a new DataFrame if file doesn't exist
        """
        if os.path.exists(self.csv_file):
            self.df = pd.read_csv(self.csv_file)
        else:
            self.df = pd.DataFrame(columns=[
                "Task ID", "Task Description", "Start Time", "Stop Time", 
                "Duration (min)", "Completed", "Notes", "Active", "Updated"
            ])
            self.save_data()
        
        # Track whether any columns were added
        columns_added = False
        
        # Ensure necessary columns exist
        required_columns = ["Task ID", "Task Description", "Start Time", "Stop Time", 
                        "Duration (min)", "Completed", "Notes", "Active", "Updated"]
        for col in required_columns:
            if col not in self.df.columns:
                print(f"Column '{col}' does not exist. Adding it.")
                self.df[col] = ""  # Using empty string for all columns including Updated
                columns_added = True  # Set flag when a column is added
            else:
                print(f"Column '{col}' already exists.")
        
        # After adding any missing columns, save the updated DataFrame
        if columns_added:
            print("Saving updated DataFrame with missing columns.")
            self.save_data()
        
    def save_data(self):
        """
        Save the DataFrame to the CSV file
        
        Returns:
            Boolean indicating success or failure
        """
        try:
            # Create backup before saving
            if os.path.exists(self.csv_file):
                backup_file = f"{self.csv_file}.bak"
                try:
                    self.df.to_csv(backup_file, index=False)
                except Exception as e:
                    print(f"Error creating backup: {e}")
            
            # Save current data
            self.df.to_csv(self.csv_file, index=False)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def get_tasks(self, active=None, completed=None, task_description=None):
        """
        Get tasks based on filters
        
        Args:
            active: Boolean filter for active status
            completed: Boolean filter for completed status
            task_description: Filter for specific task description
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = self.df.copy()
        
        if active is not None:
            filtered_df = filtered_df[filtered_df["Active"] == (1 if active else 0)]
            
        if completed is not None:
            filtered_df = filtered_df[filtered_df["Completed"] == ("Yes" if completed else "No")]
            
        if task_description is not None:
           ## messagebox.showinfo("Task Description", f"Filtering by task description: {task_description}")##remmove
            filtered_df = filtered_df[filtered_df["Task Description"] == task_description]
            
        return filtered_df
    
    def add_task(self, task_data):
        """
        Add a new task to the dataframe
        
        Args:
            task_data: Dictionary containing task data
            
        Returns:
            Boolean indicating success
        """
        try:
            self.df = pd.concat([self.df, pd.DataFrame([task_data])], ignore_index=True)
            return self.save_data()
        except Exception as e:
            print(f"Error adding task: {e}")
            return False
    
    def update_task(self, idx, update_data):
        """
        Update a task with new values
        
        Args:
            idx: Index of the task to update
            update_data: Dictionary of columns and values to update
            
        Returns:
            Boolean indicating success
        """
        try:
            for column, value in update_data.items():
                self.df.at[idx, column] = value
            return self.save_data()
        except Exception as e:
            print(f"Error updating task: {e}")
            return False
    
    def add_notes(self, idx, notes, update_time=None):
        """
        Add notes to an existing task
        
        Args:
            idx: Index of the task to update
            notes: Notes to add
            
        Returns:
            Boolean indicating success
        """
        clean_update_time = update_time.strftime("%Y-%m-%d %H:%M") if update_time else None
        try:
            # Update the notes
            current_notes = self.df.at[idx, "Notes"]
            if current_notes and current_notes.strip():
                self.df.at[idx, "Notes"] = f"{current_notes} | {notes}"
            else:
                self.df.at[idx, "Notes"] = notes

            # Update the "Update" column with the timestamp if provided
            if update_time is not None:
                self.df.at[idx, "Updated"] = clean_update_time

            return self.save_data()
        except Exception as e:
            print(f"Error adding notes: {e}")
            return False
            
    def get_value(self, idx, column):
        """
        Get a specific value from the dataframe
        
        Args:
            idx: Index of the row
            column: Column name
            
        Returns:
            The value at the specified position
        """
        try:
            return self.df.at[idx, column]
        except:
            return None
            
    def get_recent_tasks(self, days=7, limit=25):
        """
        Get tasks from the last N days
        
        Args:
            days: Number of days to look back
            limit: Maximum number of tasks to return
            
        Returns:
            DataFrame with recent tasks
        """
        try:
            # Create a copy to avoid modifying the original
            temp_df = self.df.copy()
            
            # Convert dates
            temp_df["Start Time"] = pd.to_datetime(temp_df["Start Time"], errors='coerce')
            temp_df["Stop Time"] = pd.to_datetime(temp_df["Stop Time"], errors='coerce')
            
            # Determine the last activity time (either Stop Time or Start Time)
            temp_df["Last Activity"] = temp_df[["Start Time", "Stop Time"]].max(axis=1)
            
            # Sort by Last Activity in descending order
            temp_df = temp_df.sort_values(by="Last Activity", ascending=False)
            
            return temp_df.head(limit)
        except Exception as e:
            print(f"Error getting recent tasks: {e}")
            return pd.DataFrame()
        


        # Add this method to your TaskModel class
    def add_updated_column(self):
        """
        Add the 'Updated' column to the tasks DataFrame and save changes.
        """
        # Add the Updated column with NaN values
        self.tasks_df['Updated'] = ""
        
        # Save the updated DataFrame back to the file
        self.save_tasks()