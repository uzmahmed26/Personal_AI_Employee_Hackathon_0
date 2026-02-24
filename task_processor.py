#!/usr/bin/env python3
"""
Task Processor for Personal AI Employee System

This script processes tasks by moving them between folders based on their status:
- From 01_Incoming_Tasks to 02_In_Progress_Tasks when work begins
- From 02_In_Progress_Tasks to 03_Completed_Tasks when work is finished
- Implements approval gate functionality
"""

import os
import time
import re
from pathlib import Path
from datetime import datetime
import yaml
from typing import Dict, List, Optional

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
INCOMING_TASKS_FOLDER = "01_Incoming_Tasks"
IN_PROGRESS_TASKS_FOLDER = "02_In_Progress_Tasks"
COMPLETED_TASKS_FOLDER = "03_Completed_Tasks"
APPROVAL_WORKFLOWS_FOLDER = "04_Approval_Workflows"

# Convert to Path objects
incoming_tasks_path = Path(VAULT_PATH) / INCOMING_TASKS_FOLDER
in_progress_tasks_path = Path(VAULT_PATH) / IN_PROGRESS_TASKS_FOLDER
completed_tasks_path = Path(VAULT_PATH) / COMPLETED_TASKS_FOLDER
approval_workflows_path = Path(VAULT_PATH) / APPROVAL_WORKFLOWS_FOLDER

def parse_yaml_frontmatter(content: str) -> tuple:
    """
    Parse YAML frontmatter from markdown content

    Args:
        content (str): Full markdown content

    Returns:
        tuple: (yaml_data dict, content_without_frontmatter str)
    """
    if content.startswith("---"):
        # Find the end of YAML frontmatter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_content = parts[1]
            content_without_frontmatter = parts[2].strip()
            try:
                yaml_data = yaml.safe_load(yaml_content)
                return yaml_data, content_without_frontmatter
            except yaml.YAMLError:
                # If YAML parsing fails, return empty dict
                return {}, content
    return {}, content

def get_task_status(file_path: Path) -> str:
    """
    Get the status of a task from its YAML frontmatter

    Args:
        file_path (Path): Path to the task file

    Returns:
        str: Status of the task (pending_review, in_progress, completed, etc.)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        yaml_data, _ = parse_yaml_frontmatter(content)

        if yaml_data and 'status' in yaml_data:
            return yaml_data['status']
        else:
            return 'unknown'
    except Exception as e:
        print(f"Error reading task status from {file_path}: {e}")
        return 'error'

def get_task_approval_status(file_path: Path) -> bool:
    """
    Check if a task requires approval

    Args:
        file_path (Path): Path to the task file

    Returns:
        bool: True if task requires approval, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        yaml_data, _ = parse_yaml_frontmatter(content)

        if yaml_data and 'approval' in yaml_data:
            return yaml_data['approval']
        else:
            return False
    except Exception as e:
        print(f"Error reading approval status from {file_path}: {e}")
        return False

def update_task_status(file_path: Path, new_status: str) -> bool:
    """
    Update the status of a task in its YAML frontmatter

    Args:
        file_path (Path): Path to the task file
        new_status (str): New status to set

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        yaml_data, content_without_frontmatter = parse_yaml_frontmatter(content)

        if yaml_data:
            # Update the status
            yaml_data['status'] = new_status
            yaml_data['last_updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

            # Reconstruct the file with updated YAML frontmatter
            updated_content = "---\n" + yaml.dump(yaml_data, default_flow_style=False) + "---\n" + content_without_frontmatter

            # Write the updated content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            return True
        else:
            print(f"No YAML frontmatter found in {file_path}")
            return False
    except Exception as e:
        print(f"Error updating task status in {file_path}: {e}")
        return False

def move_task_to_folder(task_file_path: Path, destination_folder: Path) -> bool:
    """
    Move a task file to the specified destination folder

    Args:
        task_file_path (Path): Path to the task file to move
        destination_folder (Path): Destination folder path

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure destination folder exists
        destination_folder.mkdir(parents=True, exist_ok=True)

        # Create destination path
        destination_path = destination_folder / task_file_path.name

        # If a file with the same name already exists, add a timestamp
        if destination_path.exists():
            timestamp = datetime.now().strftime('_%Y%m%d_%H%M%S')
            stem = task_file_path.stem
            suffix = task_file_path.suffix
            new_name = f"{stem}{timestamp}{suffix}"
            destination_path = destination_folder / new_name

        # Move the file
        task_file_path.rename(destination_path)
        print(f"Moved task: {task_file_path.name} -> {destination_path.parent.name}/")
        return True
    except Exception as e:
        print(f"Error moving task {task_file_path}: {e}")
        return False

def process_incoming_tasks():
    """
    Process all incoming tasks and move them based on their status
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing incoming tasks...")

    # Get all task files in the incoming tasks folder
    task_files = list(incoming_tasks_path.glob('*.md'))

    for task_file in task_files:
        status = get_task_status(task_file)
        requires_approval = get_task_approval_status(task_file)

        if requires_approval:
            # Move to approval workflows folder
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Moving {task_file.name} to Approval Workflows")
            move_task_to_folder(task_file, approval_workflows_path)
        elif status == 'in_progress':
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Moving {task_file.name} to In Progress Tasks")
            move_task_to_folder(task_file, in_progress_tasks_path)
        elif status == 'completed':
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Moving {task_file.name} to Completed Tasks")
            move_task_to_folder(task_file, completed_tasks_path)
        elif status == 'pending_review':
            # Leave in incoming folder for review
            continue
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Unknown status '{status}' for {task_file.name}, leaving in incoming")

def process_in_progress_tasks():
    """
    Process all in-progress tasks and move them based on their status
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing in-progress tasks...")

    # Get all task files in the in-progress tasks folder
    task_files = list(in_progress_tasks_path.glob('*.md'))

    for task_file in task_files:
        status = get_task_status(task_file)
        requires_approval = get_task_approval_status(task_file)

        if requires_approval:
            # Move to approval workflows folder
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Moving {task_file.name} to Approval Workflows")
            move_task_to_folder(task_file, approval_workflows_path)
        elif status == 'completed':
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Moving {task_file.name} to Completed Tasks")
            move_task_to_folder(task_file, completed_tasks_path)
        elif status == 'pending_review':
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Moving {task_file.name} back to Incoming Tasks for review")
            move_task_to_folder(task_file, incoming_tasks_path)
        else:
            # Leave in in-progress folder
            continue

def process_approval_workflows():
    """
    Process all approval workflow tasks
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing approval workflow tasks...")

    # Get all task files in the approval workflows folder
    task_files = list(approval_workflows_path.glob('*.md'))

    for task_file in task_files:
        # Check if the task has been approved
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()

            yaml_data, _ = parse_yaml_frontmatter(content)

            if yaml_data and yaml_data.get('approved', False):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Task {task_file.name} approved, moving to In Progress")
                # Move to in-progress folder since it's approved
                move_task_to_folder(task_file, in_progress_tasks_path)
                # Update status to in_progress
                updated_task_path = in_progress_tasks_path / task_file.name
                update_task_status(updated_task_path, 'in_progress')
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Task {task_file.name} awaiting approval")
        except Exception as e:
            print(f"Error checking approval status for {task_file}: {e}")

def process_completed_tasks():
    """
    Process all completed tasks (for any post-completion actions)
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing completed tasks...")

    # Get all task files in the completed tasks folder
    task_files = list(completed_tasks_path.glob('*.md'))

    for task_file in task_files:
        # Could add archival or cleanup actions here
        pass

def setup_directories():
    """
    Create required directories if they don't exist
    """
    directories = [incoming_tasks_path, in_progress_tasks_path, completed_tasks_path, approval_workflows_path]

    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            print(f"[FOLDER] [{datetime.now().strftime('%H:%M:%S')}] Created directory: {directory}")

def main():
    """
    Main function to run the task processor continuously
    """
    print("="*60)
    print("Task Processor - Personal AI Employee System")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Vault: {VAULT_PATH}")
    print("="*60)

    # Setup required directories
    setup_directories()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Task processor running (checking every 30 seconds)...")

    try:
        while True:
            process_incoming_tasks()
            process_in_progress_tasks()
            process_approval_workflows()
            process_completed_tasks()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing cycle completed. Sleeping 30s...")
            time.sleep(30)
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Task processor stopped.")

if __name__ == "__main__":
    main()