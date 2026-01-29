#!/usr/bin/env python3
"""
Ralph Loop - Auto Retry Mechanism for Personal AI Employee System

This module implements an autonomous retry loop that processes tasks
until they reach completion status, with a maximum of 10 retries.
Enhanced with intelligence from task_intelligence module.
"""

import time
import os
from pathlib import Path
from datetime import datetime
import yaml
import json
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/ralph_loop.log'),
        logging.StreamHandler()
    ]
)

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
INCOMING_TASKS_FOLDER = "01_Incoming_Tasks"
IN_PROGRESS_TASKS_FOLDER = "02_In_Progress_Tasks"
COMPLETED_TASKS_FOLDER = "03_Completed_Tasks"
APPROVAL_WORKFLOWS_FOLDER = "04_Approval_Workflows"
FAILED_TASKS_FOLDER = "05_Failed_Tasks"
LOGS_FOLDER = "Logs"
MEMORY_FOLDER = "Memory"

# Convert to Path objects
incoming_tasks_path = Path(VAULT_PATH) / INCOMING_TASKS_FOLDER
in_progress_tasks_path = Path(VAULT_PATH) / IN_PROGRESS_TASKS_FOLDER
completed_tasks_path = Path(VAULT_PATH) / COMPLETED_TASKS_FOLDER
approval_workflows_path = Path(VAULT_PATH) / APPROVAL_WORKFLOWS_FOLDER
failed_tasks_path = Path(VAULT_PATH) / FAILED_TASKS_FOLDER
logs_path = Path(VAULT_PATH) / LOGS_FOLDER
memory_path = Path(VAULT_PATH) / MEMORY_FOLDER

class RalphLoop:
    def __init__(self):
        self.max_retries = 10
        self.setup_logs_directory()
        self.load_intelligence()

    def setup_logs_directory(self):
        """Create logs directory if it doesn't exist"""
        logs_path.mkdir(parents=True, exist_ok=True)
        failed_tasks_path.mkdir(parents=True, exist_ok=True)

    def load_intelligence(self):
        """Load intelligence data from memory"""
        self.intelligence_data = {}
        # Load success patterns
        success_file = memory_path / "success_patterns.json"
        if success_file.exists():
            try:
                with open(success_file, 'r') as f:
                    self.intelligence_data['success_patterns'] = json.load(f)
            except:
                self.intelligence_data['success_patterns'] = {}

        # Load failure patterns
        failure_file = memory_path / "failure_patterns.json"
        if failure_file.exists():
            try:
                with open(failure_file, 'r') as f:
                    self.intelligence_data['failure_patterns'] = json.load(f)
            except:
                self.intelligence_data['failure_patterns'] = {}

    def parse_yaml_frontmatter(self, content: str) -> tuple:
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

    def get_task_metadata(self, file_path: Path) -> dict:
        """
        Get task metadata from YAML frontmatter

        Args:
            file_path (Path): Path to the task file

        Returns:
            dict: Task metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            yaml_data, _ = self.parse_yaml_frontmatter(content)
            return yaml_data or {}
        except Exception as e:
            logging.error(f"Error reading task metadata from {file_path}: {e}")
            return {}

    def update_task_metadata(self, file_path: Path, updates: dict) -> bool:
        """
        Update task metadata in YAML frontmatter

        Args:
            file_path (Path): Path to the task file
            updates (dict): Updates to apply to the metadata

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            yaml_data, content_without_frontmatter = self.parse_yaml_frontmatter(content)

            if yaml_data:
                # Apply updates
                for key, value in updates.items():
                    yaml_data[key] = value
                yaml_data['last_updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

                # Reconstruct the file with updated YAML frontmatter
                updated_content = "---\n" + yaml.dump(yaml_data, default_flow_style=False) + "---\n" + content_without_frontmatter

                # Write the updated content back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                return True
            else:
                logging.warning(f"No YAML frontmatter found in {file_path}")
                return False
        except Exception as e:
            logging.error(f"Error updating task metadata in {file_path}: {e}")
            return False

    def move_task_to_folder(self, task_file_path: Path, destination_folder: Path) -> bool:
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
            logging.info(f"Moved task: {task_file_path.name} -> {destination_path.parent.name}/")
            return True
        except Exception as e:
            logging.error(f"Error moving task {task_file_path}: {e}")
            return False

    def log_retry_attempt(self, task_file_path: Path, attempt: int, reason: str):
        """
        Log a retry attempt for a task

        Args:
            task_file_path (Path): Path to the task file
            attempt (int): Attempt number
            reason (str): Reason for retry
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'task_file': task_file_path.name,
            'attempt': attempt,
            'reason': reason
        }

        log_file = logs_path / f"retry_log_{datetime.now().strftime('%Y%m%d')}.json"

        # Load existing logs if file exists
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []

        # Append new log entry
        logs.append(log_entry)

        # Write logs back to file
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def analyze_retry_history(self, task_file_path: Path) -> int:
        """Analyze retry history for a task"""
        retry_count = 0
        task_name = task_file_path.name

        # Look for retry logs containing this task
        for log_file in logs_path.glob("retry_log_*.json"):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)

                for log_entry in logs:
                    if log_entry.get('task_file') == task_name:
                        retry_count += 1
            except:
                continue

        return retry_count

    def apply_intelligence_to_task(self, task_file_path: Path):
        """Apply intelligence to a task based on learned patterns"""
        metadata = self.get_task_metadata(task_file_path)

        # Get intelligence recommendations
        task_type = metadata.get('type', 'unknown')
        priority = metadata.get('priority', 'normal')

        # Apply learned patterns to adjust task properties
        updates = {}

        # Adjust based on success patterns
        if task_type in self.intelligence_data.get('success_patterns', {}):
            success_info = self.intelligence_data['success_patterns'][task_type]
            avg_confidence = success_info.get('avg_confidence', 0.5)
            updates['confidence_score'] = round(avg_confidence, 2)

        # Adjust based on failure patterns
        if task_type in self.intelligence_data.get('failure_patterns', {}):
            failure_info = self.intelligence_data['failure_patterns'][task_type]
            avg_retry_count = failure_info.get('avg_retry_count', 0)
            updates['risk_factor'] = min(1.0, avg_retry_count / 10.0)  # Normalize to 0-1 range

        # Update retry count
        retry_count = self.analyze_retry_history(task_file_path)
        updates['retry_count'] = retry_count

        # Apply updates if any
        if updates:
            self.update_task_metadata(task_file_path, updates)

    def process_task(self, task_file_path: Path) -> str:
        """
        Process a single task based on its type and intelligent rules

        Args:
            task_file_path (Path): Path to the task file

        Returns:
            str: New status for the task ('completed', 'in_progress', 'pending_review', etc.)
        """
        # Apply intelligence to the task first
        self.apply_intelligence_to_task(task_file_path)

        metadata = self.get_task_metadata(task_file_path)

        # Check if task requires approval
        requires_approval = metadata.get('approval', False)
        if requires_approval:
            # Move to approval workflows folder
            self.move_task_to_folder(task_file_path, approval_workflows_path)
            logging.info(f"Task {task_file_path.name} requires approval, moved to approval workflows")
            return 'awaiting_approval'

        # Check retry count - if too high, move to failed tasks
        retry_count = metadata.get('retry_count', 0)
        if retry_count >= self.max_retries:
            # Move to failed tasks folder
            self.move_task_to_folder(task_file_path, failed_tasks_path)
            logging.warning(f"Task {task_file_path.name} failed after {retry_count} retries, moved to failed tasks")
            return 'failed'

        # Apply business rules based on task type and intelligence
        task_type = metadata.get('type', 'generic')
        confidence_score = metadata.get('confidence_score', 0.5)

        if task_type == 'file_arrival':
            # For file arrival tasks, consider confidence score
            if confidence_score > 0.7:
                return 'completed'
            else:
                return 'in_progress'  # Need more verification
        elif task_type == 'email':
            # For email tasks, determine if action is needed
            priority = metadata.get('priority', 'normal')
            risk_factor = metadata.get('risk_factor', 0.0)

            if priority in ['high', 'critical']:
                # High priority emails might need more processing
                if risk_factor > 0.5:
                    # High risk, mark for manual review
                    updates = {'requires_manual_review': True}
                    self.update_task_metadata(task_file_path, updates)
                    return 'pending_review'
                else:
                    return 'in_progress'
            else:
                # Lower priority emails can be marked as completed if confidence is high
                if confidence_score > 0.6:
                    return 'completed'
                else:
                    return 'in_progress'
        else:
            # For other task types, use intelligence
            if confidence_score > 0.8:
                return 'completed'
            elif confidence_score > 0.5:
                return 'in_progress'
            else:
                # Low confidence, mark for review
                updates = {'requires_manual_review': True}
                self.update_task_metadata(task_file_path, updates)
                return 'pending_review'

    def check_approval_status(self, task_file_path: Path) -> bool:
        """
        Check if a task in approval workflows has been approved

        Args:
            task_file_path (Path): Path to the task file in approval workflows

        Returns:
            bool: True if approved, False otherwise
        """
        metadata = self.get_task_metadata(task_file_path)
        return metadata.get('approved', False)

    def run_autonomous_cycle(self):
        """
        Run one cycle of the autonomous task processing
        """
        logging.info(f"Starting Ralph Loop autonomous cycle")

        # Reload intelligence data
        self.load_intelligence()

        # Process incoming tasks
        incoming_tasks = list(incoming_tasks_path.glob('*.md'))
        for task_file in incoming_tasks:
            metadata = self.get_task_metadata(task_file)
            status = metadata.get('status', 'pending_review')

            # Only process tasks that aren't already in progress or completed
            if status in ['pending_review', 'needs_action']:
                logging.info(f"Processing incoming task: {task_file.name}")

                # Determine new status based on intelligent rules
                new_status = self.process_task(task_file)

                if new_status == 'awaiting_approval':
                    # Task moved to approval workflows, skip further processing
                    continue
                elif new_status == 'in_progress':
                    # Move to in-progress folder
                    self.move_task_to_folder(task_file, in_progress_tasks_path)
                    # Update the status in the new location
                    new_task_path = in_progress_tasks_path / task_file.name
                    self.update_task_metadata(new_task_path, {'status': 'in_progress'})
                elif new_status == 'completed':
                    # Move directly to completed
                    self.move_task_to_folder(task_file, completed_tasks_path)
                    # Update the status in the new location
                    new_task_path = completed_tasks_path / task_file.name
                    self.update_task_metadata(new_task_path, {'status': 'completed'})
                elif new_status == 'failed':
                    # Already moved to failed tasks by process_task
                    pass
                else:
                    # Update status in current location
                    self.update_task_metadata(task_file, {'status': new_status})

        # Process in-progress tasks
        in_progress_tasks = list(in_progress_tasks_path.glob('*.md'))
        for task_file in in_progress_tasks:
            metadata = self.get_task_metadata(task_file)
            status = metadata.get('status', 'in_progress')

            # Check if task should be completed
            if status == 'in_progress':
                # Apply intelligent rules to determine if task is completed
                new_status = self.process_task(task_file)

                if new_status == 'completed':
                    # Move to completed folder
                    self.move_task_to_folder(task_file, completed_tasks_path)
                    # Update the status in the new location
                    new_task_path = completed_tasks_path / task_file.name
                    self.update_task_metadata(new_task_path, {'status': 'completed'})
                elif new_status == 'awaiting_approval':
                    # Move to approval workflows folder
                    self.move_task_to_folder(task_file, approval_workflows_path)
                elif new_status == 'failed':
                    # Already moved to failed tasks by process_task
                    pass
                elif new_status == 'pending_review':
                    # Move back to incoming for review
                    self.move_task_to_folder(task_file, incoming_tasks_path)
                    new_task_path = incoming_tasks_path / task_file.name
                    self.update_task_metadata(new_task_path, {'status': 'pending_review'})

        # Process approval workflows
        approval_tasks = list(approval_workflows_path.glob('*.md'))
        for task_file in approval_tasks:
            metadata = self.get_task_metadata(task_file)

            # Check if task has been approved
            if metadata.get('approved', False):
                logging.info(f"Approved task: {task_file.name}")

                # Move to in-progress or completed based on original status
                original_status = metadata.get('original_status', 'in_progress')

                if original_status == 'completed':
                    self.move_task_to_folder(task_file, completed_tasks_path)
                    new_task_path = completed_tasks_path / task_file.name
                    self.update_task_metadata(new_task_path, {'status': 'completed'})
                else:
                    self.move_task_to_folder(task_file, in_progress_tasks_path)
                    new_task_path = in_progress_tasks_path / task_file.name
                    self.update_task_metadata(new_task_path, {'status': 'in_progress'})

    def run_with_retry(self, max_cycles: int = None):
        """
        Run the Ralph Loop with retry capability

        Args:
            max_cycles (int): Maximum number of cycles to run (None for infinite)
        """
        cycle_count = 0

        while max_cycles is None or cycle_count < max_cycles:
            try:
                self.run_autonomous_cycle()

                # Wait before next cycle
                time.sleep(30)  # Check every 30 seconds

                cycle_count += 1
            except KeyboardInterrupt:
                logging.info("Ralph Loop interrupted by user")
                break
            except Exception as e:
                logging.error(f"Error in Ralph Loop: {e}")
                time.sleep(60)  # Wait a minute before retrying after error

def main():
    """Main function to run the Ralph Loop"""
    logging.info("RALPH LOOP - Intelligent Task Processor started")

    ralph = RalphLoop()
    ralph.run_with_retry()

if __name__ == "__main__":
    main()