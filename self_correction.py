#!/usr/bin/env python3
"""
Self-Correction Mode for Personal AI Employee System

This module implements self-correction when tasks fail repeatedly,
analyzing failures and adjusting processing strategies automatically.
"""

import os
import time
from pathlib import Path
from datetime import datetime
import yaml
import json
from typing import Dict, List, Optional

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
INCOMING_TASKS_FOLDER = "01_Incoming_Tasks"
IN_PROGRESS_TASKS_FOLDER = "02_In_Progress_Tasks"
COMPLETED_TASKS_FOLDER = "03_Completed_Tasks"
FAILED_TASKS_FOLDER = "05_Failed_Tasks"
MEMORY_FOLDER = "Memory"
LOGS_FOLDER = "Logs"

# Convert to Path objects
incoming_tasks_path = Path(VAULT_PATH) / INCOMING_TASKS_FOLDER
in_progress_tasks_path = Path(VAULT_PATH) / IN_PROGRESS_TASKS_FOLDER
completed_tasks_path = Path(VAULT_PATH) / COMPLETED_TASKS_FOLDER
failed_tasks_path = Path(VAULT_PATH) / FAILED_TASKS_FOLDER
memory_path = Path(VAULT_PATH) / MEMORY_FOLDER
logs_path = Path(VAULT_PATH) / LOGS_FOLDER

class SelfCorrectionMode:
    def __init__(self):
        self.failure_threshold = 3
        self.setup_failed_tasks_directory()
        self.setup_memory_directory()

    def setup_failed_tasks_directory(self):
        """Create failed tasks directory if it doesn't exist"""
        failed_tasks_path.mkdir(parents=True, exist_ok=True)

    def setup_memory_directory(self):
        """Create memory directory if it doesn't exist"""
        memory_path.mkdir(parents=True, exist_ok=True)

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
            print(f"Error reading task metadata from {file_path}: {e}")
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
                print(f"No YAML frontmatter found in {file_path}")
                return False
        except Exception as e:
            print(f"Error updating task metadata in {file_path}: {e}")
            return False

    def analyze_retry_logs(self) -> Dict[str, List[Dict]]:
        """Analyze retry logs to identify frequently failing tasks"""
        failure_analysis = {}
        
        # Look for all retry log files
        for log_file in logs_path.glob("retry_log_*.json"):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                
                # Group logs by task file
                for log_entry in logs:
                    task_file = log_entry.get('task_file')
                    if task_file:
                        if task_file not in failure_analysis:
                            failure_analysis[task_file] = []
                        failure_analysis[task_file].append(log_entry)
            except Exception as e:
                print(f"Error reading retry log {log_file}: {e}")
        
        return failure_analysis

    def identify_failing_tasks(self) -> List[str]:
        """Identify tasks that have failed more than the threshold"""
        failure_analysis = self.analyze_retry_logs()
        failing_tasks = []
        
        for task_file, attempts in failure_analysis.items():
            if len(attempts) >= self.failure_threshold:
                failing_tasks.append(task_file)
        
        return failing_tasks

    def write_failure_analysis(self, failing_tasks: List[str]):
        """Write failure analysis for each failing task"""
        for task_file in failing_tasks:
            # Create analysis content
            analysis_content = f"""# Failure Analysis for {task_file}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Failure Summary
- **Task Name**: {task_file}
- **Number of Failed Attempts**: {len(self.get_attempts_for_task(task_file))}
- **Failure Threshold**: {self.failure_threshold} attempts

## Failure Patterns Identified
"""
            
            attempts = self.get_attempts_for_task(task_file)
            for i, attempt in enumerate(attempts, 1):
                analysis_content += f"- Attempt {i}: {attempt.get('reason', 'Unknown reason')} at {attempt.get('timestamp', 'Unknown time')}\n"
            
            analysis_content += f"""
## Recommended Actions
1. Review the task content and requirements
2. Check for any external dependencies that might be causing failures
3. Consider simplifying the task or breaking it into smaller components
4. Evaluate if the task is still relevant and necessary

## Next Steps
- The system will attempt to process this task with an adjusted strategy
- If continued failures occur, manual intervention may be required
"""

            # Write analysis to file
            analysis_file = memory_path / f"failure_analysis_{task_file.replace('.md', '')}.md"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                f.write(analysis_content)
            
            print(f"Failure analysis written for {task_file}")

    def get_attempts_for_task(self, task_file: str) -> List[Dict]:
        """Get all attempts for a specific task from logs"""
        all_attempts = []
        
        for log_file in logs_path.glob("retry_log_*.json"):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                
                for log_entry in logs:
                    if log_entry.get('task_file') == task_file:
                        all_attempts.append(log_entry)
            except Exception as e:
                print(f"Error reading retry log {log_file}: {e}")
        
        return all_attempts

    def adjust_processing_strategy(self, failing_tasks: List[str]):
        """Adjust processing strategy for failing tasks"""
        for task_file in failing_tasks:
            # Find the actual task file in the system
            task_path = None
            
            # Check in incoming tasks
            for file_path in incoming_tasks_path.glob('*.md'):
                if file_path.name == task_file:
                    task_path = file_path
                    break
            
            # Check in progress tasks
            if not task_path:
                for file_path in in_progress_tasks_path.glob('*.md'):
                    if file_path.name == task_file:
                        task_path = file_path
                        break
            
            if task_path:
                # Get current metadata
                metadata = self.get_task_metadata(task_path)
                
                # Adjust strategy - lower priority, mark for manual review
                updates = {
                    'priority': 'low',  # Lower priority to reduce system stress
                    'requires_manual_review': True,
                    'adjusted_strategy': True,
                    'strategy_adjustment_reason': f'Original strategy failed after {self.failure_threshold} attempts',
                    'next_attempt_strategy': 'manual_assistance_required'
                }
                
                # Update the task
                self.update_task_metadata(task_path, updates)
                
                print(f"Adjusted processing strategy for {task_file}")
            else:
                print(f"Could not find task file {task_file} to adjust strategy")

    def move_persistent_failures(self, failing_tasks: List[str]):
        """Move tasks that consistently fail to a special folder"""
        for task_file in failing_tasks:
            # Find the actual task file in the system
            task_path = None
            
            # Check in incoming tasks
            for file_path in incoming_tasks_path.glob('*.md'):
                if file_path.name == task_file:
                    task_path = file_path
                    break
            
            # Check in progress tasks
            if not task_path:
                for file_path in in_progress_tasks_path.glob('*.md'):
                    if file_path.name == task_file:
                        task_path = file_path
                        break
            
            if task_path:
                # Move to failed tasks folder
                destination_path = failed_tasks_path / task_path.name
                task_path.rename(destination_path)
                
                print(f"Moved persistent failure {task_file} to failed tasks folder")

    def run_self_correction_cycle(self):
        """Run one cycle of self-correction analysis"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running self-correction cycle")
        
        # Identify tasks that have failed repeatedly
        failing_tasks = self.identify_failing_tasks()
        
        if failing_tasks:
            print(f"Found {len(failing_tasks)} tasks with repeated failures")
            
            # Write failure analysis for each
            self.write_failure_analysis(failing_tasks)
            
            # Adjust processing strategies
            self.adjust_processing_strategy(failing_tasks)
            
            # Move persistent failures to special folder
            self.move_persistent_failures(failing_tasks)
        else:
            print("No tasks found with repeated failures")

def main():
    """Main function to run the self-correction mode"""
    print("="*60)
    print("SELF-CORRECTION MODE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    correction = SelfCorrectionMode()
    correction.run_self_correction_cycle()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Self-correction cycle completed")

if __name__ == "__main__":
    main()