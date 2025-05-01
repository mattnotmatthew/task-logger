# controllers/report_controller.py

import os
import webbrowser
import markdown
import pandas as pd
from datetime import datetime, timedelta

class ReportController:
    """
    Controller for generating reports from task data
    """
    
    def __init__(self, task_model):
        """
        Initialize with a reference to the task model
        
        Args:
            task_model: The task data model
        """
        self.model = task_model
        
    def generate_markdown_content(self, days=7):
        """
        Generate markdown content for reports
        
        Args:
            days: Number of days to include in the report
            
        Returns:
            String containing markdown formatted report
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Create a temporary DataFrame for processing
        temp_df = self.model.df.copy()
        temp_df["Start Time"] = pd.to_datetime(temp_df["Start Time"], errors='coerce')
        temp_df["Stop Time"] = pd.to_datetime(temp_df["Stop Time"], errors='coerce')
        
        recent = temp_df[temp_df["Start Time"].between(start_date, end_date)]
        recent = recent.sort_values(by="Start Time")
        
        # Create completed and in-progress task dataframes
        completed_tasks = recent[recent["Active"] == 0]
        pending_tasks = recent[recent["Active"] != 0]
        
        export_date = datetime.now().strftime("%Y-%m-%d")
        lines = ["📋 5-15\n"]
        lines.append(f"<strong>Name</strong>: [InsertName]<br><strong>Week Ending</strong>: {export_date}")
        
        # Accomplishments section
        lines.append("### Accomplishments this week")
                
        if not completed_tasks.empty:
            # Group completed tasks by description
            completed_grouped = completed_tasks.groupby("Task Description")
            
            for task, group in completed_grouped:
                lines.append(f"- {task}")
                
                
                for _, row in group.iterrows():
                    note_text = str(row["Notes"]) if pd.notna(row["Notes"]) else ""
                    
                    # Split notes by the pipe delimiter
                    individual_notes = note_text.split("|")
                    
                    # Add each note as a separate bullet point, stripping whitespace
                    for note in individual_notes:
                        if note.strip():  # Only add if note isn't empty after stripping
                            lines.append(f"     - {note.strip()}")
                
                lines.append("")  # Add a blank line between task groups
        else:
            lines.append("*No completed tasks this week*\n")
        
        # Priorities section
        lines.append("### Priorities next week")
        
        if not pending_tasks.empty:
            # Group pending tasks by description
            pending_grouped = pending_tasks.groupby("Task Description")
            
            for task, group in pending_grouped:
                lines.append(f"- {task}")
                lines.append("")  # Add a blank line after the task heading
                
                for _, row in group.iterrows():
                    note_text = str(row["Notes"]) if pd.notna(row["Notes"]) else ""
                    
                    # Split notes by the pipe delimiter
                    individual_notes = note_text.split("|")
                    
                    # Add each note as a separate bullet point, stripping whitespace
                    for note in individual_notes:
                        if note.strip():  # Only add if note isn't empty after stripping
                            lines.append(f"     - {note.strip()}")
                
                lines.append("")  # Add a blank line between task groups
        else:
            lines.append("*No pending tasks for next week*\n")
        
        lines.append("### Risks/Challenges")
        lines.append("### Learnings, Opportunities, Feedback, or Observations")
        return "\n".join(lines)
    
    def preview_markdown(self):
        """
        Preview markdown content in browser
        
        Returns:
            Tuple of (success, message or error)
        """
        try:
            md_content = self.generate_markdown_content()
            
            # Convert to HTML
            html = markdown.markdown(md_content)
        
            # Save as temp HTML file
            temp_html = f"exports/temp_preview_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
            abolute_path = os.path.abspath(temp_html)
            file_url = f"file://{abolute_path}"

            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; color: #000; }}
                        h1 {{ color: #2c3e50; border-bottom: 2px solid #4287f5; padding-bottom: 10px; }}
                        h2 {{ color: #34495e; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 30px; }}
                        h3 {{ color: #3498db; margin-top: 20px; margin-bottom: 10px; }}
                        ul {{ padding-left: 20px; }}
                        li {{ margin-bottom: 10px; margin-bottom: 0 !important; }}
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
            webbrowser.open(file_url)
            return True, f"Preview opened in browser: {temp_html}"
        except Exception as e:
            return False, f"Error generating preview: {str(e)}"
    
    def export_to_markdown(self):
        """
        Export tasks to markdown file
        
        Returns:
            Tuple of (success, file path or error message)
        """
        try:
            md_content = self.generate_markdown_content()
            
            date_str = datetime.now().strftime("%Y-%m-%d")
            output_path = f"exports/{date_str}_weekly_summary.md"
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            
            return True, output_path
        except Exception as e:
            return False, f"Error exporting to markdown: {str(e)}"
