#!/usr/bin/env python3
"""
Script to update the status of all in-progress tasks to completed
"""

import os
from pathlib import Path
import yaml
import re
from datetime import datetime

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
IN_PROGRESS_TASKS_FOLDER = "02_In_Progress_Tasks"

# Convert to Path objects
in_progress_tasks_path = Path(VAULT_PATH) / IN_PROGRESS_TASKS_FOLDER

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
            yaml_data['completed_date'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            yaml_data['last_updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

            # Reconstruct the file with updated YAML frontmatter
            updated_content = "---\n" + yaml.dump(yaml_data, default_flow_style=False) + "---\n" + content_without_frontmatter

            # Write the updated content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            print(f"Updated status to '{new_status}' for: {file_path.name}")
            return True
        else:
            print(f"No YAML frontmatter found in {file_path}")
            return False
    except Exception as e:
        print(f"Error updating task status in {file_path}: {e}")
        return False

def main():
    """Main function to update all in-progress task statuses to completed"""
    print("Updating all in-progress tasks to completed status...")
    
    # Get all task files in the in-progress tasks folder
    task_files = list(in_progress_tasks_path.glob('*.md'))
    
    updated_count = 0
    
    for task_file in task_files:
        if update_task_status(task_file, 'completed'):
            updated_count += 1
    
    print(f"Successfully updated {updated_count} tasks to 'completed' status.")
    print("Now run the task_processor.py to move these tasks to the completed folder.")

if __name__ == "__main__":
    main()