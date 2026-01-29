import time
import os
from pathlib import Path
import mimetypes
from datetime import datetime
import signal
import sys

# Configuration constants - easily changeable
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
INBOX_FOLDER = "Inbox"
INCOMING_TASKS_FOLDER = "01_Incoming_Tasks"
COMPLETED_TASKS_FOLDER = "03_Completed_Tasks"

# Convert to Path objects for easier manipulation
inbox_path = Path(VAULT_PATH) / INBOX_FOLDER
incoming_tasks_path = Path(VAULT_PATH) / INCOMING_TASKS_FOLDER
completed_tasks_path = Path(VAULT_PATH) / COMPLETED_TASKS_FOLDER

def format_file_size(size_bytes):
    """
    Convert file size from bytes to human-readable format (KB, MB, GB)

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Human-readable file size
    """
    if size_bytes == 0:
        return "0 B"

    # Define size units
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)

    # Keep dividing by 1024 until we reach the appropriate unit
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    # Format to 2 decimal places if in KB or larger, otherwise whole number
    if i == 0:  # Bytes
        return f"{int(size)} {size_names[i]}"
    else:
        return f"{size:.2f} {size_names[i]}"

def get_file_type(file_path):
    """
    Determine the file type based on extension

    Args:
        file_path (Path): Path to the file

    Returns:
        str: Human-readable file type
    """
    # Get the file extension
    ext = file_path.suffix.lower()

    # Map common extensions to readable types
    type_map = {
        '.txt': 'Text Document',
        '.pdf': 'PDF Document',
        '.doc': 'Word Document',
        '.docx': 'Word Document',
        '.xls': 'Excel Spreadsheet',
        '.xlsx': 'Excel Spreadsheet',
        '.ppt': 'PowerPoint Presentation',
        '.pptx': 'PowerPoint Presentation',
        '.jpg': 'JPEG Image',
        '.jpeg': 'JPEG Image',
        '.png': 'PNG Image',
        '.gif': 'GIF Image',
        '.mp3': 'Audio File',
        '.wav': 'Audio File',
        '.mp4': 'Video File',
        '.avi': 'Video File',
        '.py': 'Python Script',
        '.js': 'JavaScript File',
        '.html': 'HTML Document',
        '.css': 'CSS Stylesheet',
        '.csv': 'CSV Data File',
        '.zip': 'ZIP Archive',
        '.rar': 'RAR Archive',
        '.exe': 'Executable File'
    }

    return type_map.get(ext, f'{ext.upper()[1:]} File')

def create_task_file(file_path):
    """
    Create a markdown task file in the 01_Incoming_Tasks folder

    Args:
        file_path (Path): Path to the original file that triggered the task
    """
    try:
        # Get file stats
        stat_info = file_path.stat()
        file_size = stat_info.st_size
        formatted_size = format_file_size(file_size)

        # Generate unique task ID using timestamp
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Create the task filename
        task_filename = f"{task_id}.md"
        task_file_path = incoming_tasks_path / task_filename

        # Get current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        # Get file details
        file_name = file_path.name
        file_type = get_file_type(file_path)

        # Create the markdown content with YAML frontmatter
        markdown_content = f"""---
type: file_arrival
filename: {file_name}
size: {formatted_size}
created: {timestamp}
status: pending_review
priority: normal
task_id: {task_id}
---

## New File Detected

A new file has arrived in the Inbox:

**File Details:**
- **Name:** {file_name}
- **Type:** {file_type}
- **Size:** {formatted_size}
- **Received:** {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}

## Suggested Actions
- [ ] Review the file content
- [ ] Categorize the file type
- [ ] Assign appropriate priority
- [ ] Move to In_Progress_Tasks when ready to work on it

## File Location
The original file has been archived at:
{COMPLETED_TASKS_FOLDER}/{file_name}

"""

        # Write the task file
        with open(task_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Task file created: {task_filename}")

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error creating task file for {file_path}: {str(e)}")

def move_to_archive(file_path):
    """
    Move the original file to the 03_Completed_Tasks folder

    Args:
        file_path (Path): Path to the file to move
    """
    try:
        # Create destination path in completed tasks folder
        destination_path = completed_tasks_path / file_path.name

        # If a file with the same name already exists, add a timestamp
        if destination_path.exists():
            timestamp = datetime.now().strftime('_%Y%m%d_%H%M%S')
            stem = file_path.stem
            suffix = file_path.suffix
            new_name = f"{stem}{timestamp}{suffix}"
            destination_path = completed_tasks_path / new_name

        # Move the file
        file_path.rename(destination_path)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] File moved to archive: {destination_path.name}")

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error moving file {file_path} to archive: {str(e)}")

def check_inbox(processed_files):
    """
    Scan the Inbox folder for new files and process them

    Args:
        processed_files (set): Set of files already processed to avoid duplicates
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning Inbox folder...")

    try:
        # Get all files in the inbox folder
        inbox_files = list(inbox_path.glob('*'))

        # Count new files processed in this scan
        new_files_count = 0

        for file_path in inbox_files:
            # Skip directories
            if file_path.is_dir():
                continue

            # Check if this file has already been processed
            if file_path in processed_files:
                continue

            # Process the new file
            print(f"[{datetime.now().strftime('%H:%M:%S')}] New file detected: {file_path.name}")

            # Create a task file for this new file
            create_task_file(file_path)

            # Move the original file to the completed tasks folder
            move_to_archive(file_path)

            # Add to processed files to avoid duplicate processing
            processed_files.add(file_path)

            new_files_count += 1

        if new_files_count == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No new files found in Inbox")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Processed {new_files_count} new file(s)")

    except FileNotFoundError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Inbox folder not found: {inbox_path}")
    except PermissionError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Permission denied accessing Inbox folder: {inbox_path}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error scanning Inbox: {str(e)}")

def setup_directories():
    """
    Create required directories if they don't exist
    """
    directories = [inbox_path, incoming_tasks_path, completed_tasks_path]

    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            print(f"📁 [{datetime.now().strftime('%H:%M:%S')}] Created directory: {directory}")

def signal_handler(sig, frame):
    """
    Handle graceful shutdown when Ctrl+C is pressed
    """
    print(f"\n🛑 [{datetime.now().strftime('%H:%M:%S')}] Shutting down file watcher...")
    print("✅ File watcher stopped successfully!")
    sys.exit(0)

def main():
    """
    Main function that runs the file watching loop
    """
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Setup required directories
    setup_directories()

    # Print startup message (using ASCII characters for Windows compatibility)
    print("="*60)
    print(f"AI-Robot Personal AI Employee - File Watcher Started")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Vault Path: {VAULT_PATH}")
    print(f"Inbox: {inbox_path}")
    print(f"Tasks: {incoming_tasks_path}")
    print(f"Archive: {completed_tasks_path}")
    print("="*60)

    # Set to keep track of processed files to avoid duplicates
    processed_files = set()

    # Main monitoring loop
    try:
        while True:
            # Check the inbox for new files
            check_inbox(processed_files)

            # Wait for 10 seconds before next check
            print(f"Zzz [{datetime.now().strftime('%H:%M:%S')}] Sleeping for 10 seconds...")
            time.sleep(10)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        signal_handler(None, None)

if __name__ == "__main__":
    main()