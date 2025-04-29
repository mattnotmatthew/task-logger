# Task Logger

A simple desktop application for tracking and managing tasks with reporting capabilities.

## Features

- Log and track tasks
- Filter tasks by status (active, completed, all)
- Generate weekly reports in Markdown format
- Export task data to CSV
- Always-on-top mode for convenient access

## Requirements

- Python 3.6 or higher
- Required packages:
  - tkinter (usually comes with Python)
  - pandas
  - markdown

## Installation

1. Clone or download this repository
2. Install required packages:
   ```
   pip install pandas markdown
   ```
3. Run the setup script to organize the files:
   ```
   python setup.py
   ```

## Running the Application

```
python main.py
```

## Application Structure

The application follows the Model-View-Controller (MVC) pattern:

- **Model**: Handles data operations

  - `task_model.py`: Manages task data (loading, saving, querying)

- **View**: Handles UI components

  - `main_view.py`: Main application window
  - `dialog_view.py`: Task operation dialogs
  - `utils/helpers.py`: UI helper functions

- **Controller**: Contains business logic

  - `task_controller.py`: Task management logic
  - `report_controller.py`: Report generation logic

- **Other Files**:
  - `main.py`: Application entry point
  - `constants.py`: Application constants and colors

## Usage

### Starting a Task

1. Click "Start Task"
2. Enter or select a task name
3. Add optional notes
4. Click "Start"

### Finishing a Task

1. Click "Finish Task"
2. Select the task to complete
3. Add optional notes
4. Click "Complete"

### Filtering Tasks

Use the filter buttons to show:

- All Tasks
- Active Tasks
- Finished Tasks

### Generating Reports

- Click "Preview Weekly Report" to view a web-based preview
- Click "Export to Markdown" to save a markdown report file
- Click "Generate Weekly CSV Summary" to export data as CSV

## Customization

Edit the `constants.py` file to customize:

- Colors
- Default window size
- File paths

## License

This project is released under the MIT License.
