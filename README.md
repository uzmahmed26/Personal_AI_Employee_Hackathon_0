# Personal AI Employee System

Welcome to your Personal AI Employee system! This system consists of two main components that work together to automate task creation from different sources.

## Project Structure

For a complete overview of the folder structure and how the system components work together, see [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md).

## Components

### 1. File Watcher (`file_watcher.py`)
- Monitors the `Inbox` folder for new files
- Creates markdown task files in `01_Incoming_Tasks`
- Archives original files to `03_Completed_Tasks`

### 2. Gmail Watcher (`gmail_watcher.py`)
- Monitors Gmail for new important emails
- Creates markdown task files in `01_Incoming_Tasks`
- Marks emails as read in Gmail

### 3. Main Orchestrator (`main_orchestrator.py`)
- Centrally manages both file and Gmail watchers
- Runs both components simultaneously
- Provides graceful shutdown capability

### 4. Task Processor (`task_processor.py`)
- Automatically moves tasks between status folders
- Processes task status updates from YAML metadata
- Maintains workflow progression

### 5. Notification System (`notification_system.py`)
- Sends desktop notifications for new tasks
- Priority-based alert system
- Prevents duplicate notifications

### 6. Dashboard Generator (`dashboard_generator.py`)
- Creates comprehensive system status reports
- Shows task distribution and system health
- Generates both console and markdown dashboards

## Setup Instructions

### For Gmail Watcher:
1. Follow the setup guide in `GMAIL_SETUP_GUIDE.md` to configure Gmail API access
2. Install required packages: `pip install -r requirements.txt`
3. Run the script for the first time to complete OAuth authentication

### For File Watcher:
1. No additional setup required
2. Simply run the script: `python file_watcher.py`

## Running the System

### Option 1: Run Separately
```bash
# Terminal 1: Run file watcher
python file_watcher.py

# Terminal 2: Run gmail watcher
python gmail_watcher.py
```

### Option 2: Run with Orchestrator (Recommended)
```bash
# Run both watchers simultaneously with centralized control
python main_orchestrator.py
```

### Option 3: Additional Utilities
```bash
# Process tasks based on their status
python task_processor.py

# Generate system dashboard
python dashboard_generator.py

# Run system test
python test_workflow.py
```

You can run both scripts simultaneously to monitor both files and emails.

## Task Management

All tasks from both sources are created in the `01_Incoming_Tasks` folder in markdown format with YAML frontmatter. You can view and manage these tasks in Obsidian.

## Configuration

Both scripts have configurable options at the top of each file:
- `VAULT_PATH`: Your Obsidian vault path
- `CHECK_INTERVAL`: How often to check for new items (in seconds)
- `TASKS_FOLDER`: Where to store task files

## Troubleshooting

Refer to `TROUBLESHOOTING.md` for common issues and solutions.

## Security

- Store `credentials.json` and `token.json` securely
- Add these files to `.gitignore` if using version control
- Revoke OAuth access in your Google Account if credentials are compromised

## Integration with Obsidian

All created task files are in markdown format with YAML frontmatter, making them perfect for use in Obsidian. You can create queries to filter and manage your tasks based on type, status, priority, etc.