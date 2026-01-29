#!/usr/bin/env python3
"""
Task Intelligence Layer for Personal AI Employee System

This module adds decision-making intelligence to task processing
by analyzing task history and automatically prioritizing tasks.
"""

import os
import time
from pathlib import Path
from datetime import datetime
import yaml
import json
from typing import Dict, List, Optional
from collections import Counter
import re

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
INCOMING_TASKS_FOLDER = "01_Incoming_Tasks"
IN_PROGRESS_TASKS_FOLDER = "02_In_Progress_Tasks"
COMPLETED_TASKS_FOLDER = "03_Completed_Tasks"
MEMORY_FOLDER = "Memory"
LOGS_FOLDER = "Logs"

# Convert to Path objects
incoming_tasks_path = Path(VAULT_PATH) / INCOMING_TASKS_FOLDER
in_progress_tasks_path = Path(VAULT_PATH) / IN_PROGRESS_TASKS_FOLDER
completed_tasks_path = Path(VAULT_PATH) / COMPLETED_TASKS_FOLDER
memory_path = Path(VAULT_PATH) / MEMORY_FOLDER
logs_path = Path(VAULT_PATH) / LOGS_FOLDER

class TaskIntelligence:
    def __init__(self):
        self.setup_memory_directory()
        self.load_memory()

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

    def load_memory(self):
        """Load memory from stored files"""
        self.success_patterns = {}
        self.failure_patterns = {}
        self.approval_patterns = {}
        
        # Load success patterns
        success_file = memory_path / "success_patterns.json"
        if success_file.exists():
            try:
                with open(success_file, 'r') as f:
                    self.success_patterns = json.load(f)
            except:
                self.success_patterns = {}
        
        # Load failure patterns
        failure_file = memory_path / "failure_patterns.json"
        if failure_file.exists():
            try:
                with open(failure_file, 'r') as f:
                    self.failure_patterns = json.load(f)
            except:
                self.failure_patterns = {}
        
        # Load approval patterns
        approval_file = memory_path / "approval_patterns.json"
        if approval_file.exists():
            try:
                with open(approval_file, 'r') as f:
                    self.approval_patterns = json.load(f)
            except:
                self.approval_patterns = {}

    def save_memory(self):
        """Save memory to stored files"""
        # Save success patterns
        success_file = memory_path / "success_patterns.json"
        with open(success_file, 'w') as f:
            json.dump(self.success_patterns, f, indent=2)
        
        # Save failure patterns
        failure_file = memory_path / "failure_patterns.json"
        with open(failure_file, 'w') as f:
            json.dump(self.failure_patterns, f, indent=2)
        
        # Save approval patterns
        approval_file = memory_path / "approval_patterns.json"
        with open(approval_file, 'w') as f:
            json.dump(self.approval_patterns, f, indent=2)

    def analyze_completed_tasks(self):
        """Analyze completed tasks to identify patterns"""
        if not completed_tasks_path.exists():
            return

        # Count task types and outcomes
        task_outcomes = Counter()
        task_types = Counter()
        task_priorities = Counter()
        
        for file_path in completed_tasks_path.iterdir():
            if file_path.is_file() and file_path.suffix == '.md':
                try:
                    metadata = self.get_task_metadata(file_path)
                    
                    task_type = metadata.get('type', 'unknown')
                    priority = metadata.get('priority', 'normal')
                    status = metadata.get('status', 'completed')
                    
                    task_types[task_type] += 1
                    task_priorities[priority] += 1
                    task_outcomes[f"{task_type}:{status}"] += 1
                except Exception as e:
                    print(f"Error analyzing completed task {file_path}: {e}")

        # Store patterns in memory
        self.success_patterns['task_types'] = dict(task_types)
        self.success_patterns['priorities'] = dict(task_priorities)
        self.success_patterns['outcomes'] = dict(task_outcomes)

    def calculate_confidence_score(self, task_metadata: dict) -> float:
        """Calculate confidence score based on historical patterns"""
        # Default confidence
        confidence = 0.7
        
        # Adjust based on task type
        task_type = task_metadata.get('type', 'unknown')
        if task_type in self.success_patterns.get('task_types', {}):
            # Higher frequency tasks get higher confidence
            type_freq = self.success_patterns['task_types'][task_type]
            confidence += min(type_freq * 0.05, 0.2)  # Cap at 0.2 bonus
        
        # Adjust based on priority
        priority = task_metadata.get('priority', 'normal')
        if priority == 'high':
            confidence += 0.1
        elif priority == 'critical':
            confidence += 0.2
        elif priority == 'low':
            confidence -= 0.1
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))

    def estimate_effort(self, task_metadata: dict) -> str:
        """Estimate effort level based on task characteristics"""
        # Default effort
        effort = "medium"
        
        # Adjust based on priority
        priority = task_metadata.get('priority', 'normal')
        if priority == 'critical':
            effort = "high"
        elif priority == 'high':
            effort = "medium-high"
        elif priority == 'low':
            effort = "low"
        
        # Adjust based on task type
        task_type = task_metadata.get('type', 'unknown')
        if task_type == 'complex_project':
            effort = "high"
        elif task_type == 'routine':
            effort = "low"
        elif task_type == 'email':
            # Emails vary, adjust based on length of subject/content
            subject = task_metadata.get('subject', '')
            if len(subject) > 50:  # Long subject might indicate complexity
                effort = "medium-high"
        
        return effort

    def calculate_urgency(self, task_metadata: dict) -> float:
        """Calculate urgency score based on various factors"""
        urgency = 0.5  # Base urgency
        
        # Urgency based on priority
        priority = task_metadata.get('priority', 'normal')
        if priority == 'critical':
            urgency = 0.9
        elif priority == 'high':
            urgency = 0.7
        elif priority == 'low':
            urgency = 0.3
        
        # Check for urgency keywords in subject/content
        subject = task_metadata.get('subject', '').lower()
        content_preview = task_metadata.get('content_preview', '').lower()
        
        urgent_keywords = [
            'urgent', 'asap', 'immediate', 'today', 'now', 'deadline', 
            'critical', 'emergency', 'crucial', 'important', 'needed'
        ]
        
        combined_text = subject + " " + content_preview
        for keyword in urgent_keywords:
            if keyword in combined_text:
                urgency = min(1.0, urgency + 0.2)
                break
        
        # Cap urgency at 1.0
        return min(1.0, urgency)

    def analyze_retries(self, task_file_path: Path) -> int:
        """Analyze retry logs to determine how many times a task has failed"""
        retry_count = 0
        retry_logs = logs_path / f"retry_log_{datetime.now().strftime('%Y%m%d')}.json"
        
        if retry_logs.exists():
            try:
                with open(retry_logs, 'r') as f:
                    logs = json.load(f)
                
                # Count retries for this specific task
                for log_entry in logs:
                    if log_entry.get('task_file') == task_file_path.name:
                        retry_count += 1
            except:
                pass  # If log file is malformed, return 0
        
        return retry_count

    def prioritize_task(self, task_file_path: Path):
        """Analyze and prioritize a single task"""
        metadata = self.get_task_metadata(task_file_path)
        
        # Calculate urgency
        urgency = self.calculate_urgency(metadata)
        
        # Calculate confidence score
        confidence = self.calculate_confidence_score(metadata)
        
        # Estimate effort
        estimated_effort = self.estimate_effort(metadata)
        
        # Analyze retry history
        retry_count = self.analyze_retries(task_file_path)
        
        # Update task metadata with intelligence
        updates = {
            'confidence_score': round(confidence, 2),
            'estimated_effort': estimated_effort,
            'retry_count': retry_count,
            'calculated_urgency': round(urgency, 2)
        }
        
        # Adjust priority based on calculated urgency if it's significantly higher
        current_priority = metadata.get('priority', 'normal')
        if urgency > 0.8 and current_priority != 'critical':
            updates['priority'] = 'critical'
        elif urgency > 0.6 and current_priority not in ['critical', 'high']:
            if current_priority != 'high':
                updates['priority'] = 'high'
        
        self.update_task_metadata(task_file_path, updates)

    def run_intelligence_cycle(self):
        """Run one cycle of task intelligence analysis"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running task intelligence cycle")
        
        # Analyze completed tasks to learn patterns
        self.analyze_completed_tasks()
        
        # Process incoming tasks
        incoming_tasks = list(incoming_tasks_path.glob('*.md'))
        for task_file in incoming_tasks:
            self.prioritize_task(task_file)
        
        # Process in-progress tasks
        in_progress_tasks = list(in_progress_tasks_path.glob('*.md'))
        for task_file in in_progress_tasks:
            self.prioritize_task(task_file)
        
        # Save learned patterns
        self.save_memory()

def main():
    """Main function to run the task intelligence"""
    print("="*60)
    print("TASK INTELLIGENCE LAYER")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    intelligence = TaskIntelligence()
    intelligence.run_intelligence_cycle()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Task intelligence cycle completed")

if __name__ == "__main__":
    main()