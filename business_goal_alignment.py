#!/usr/bin/env python3
"""
Business Goal Alignment Engine for Personal AI Employee System

This module aligns tasks with business goals and scores them for strategic value.
"""

import os
import time
from pathlib import Path
from datetime import datetime
import yaml
import json
from typing import Dict, List, Optional
from collections import Counter

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
INCOMING_TASKS_FOLDER = "01_Incoming_Tasks"
IN_PROGRESS_TASKS_FOLDER = "02_In_Progress_Tasks"
COMPLETED_TASKS_FOLDER = "03_Completed_Tasks"
BUSINESS_GOALS_FILE = "Business_Goals.md"
MEMORY_FOLDER = "Memory"
LOGS_FOLDER = "Logs"

# Convert to Path objects
incoming_tasks_path = Path(VAULT_PATH) / INCOMING_TASKS_FOLDER
in_progress_tasks_path = Path(VAULT_PATH) / IN_PROGRESS_TASKS_FOLDER
completed_tasks_path = Path(VAULT_PATH) / COMPLETED_TASKS_FOLDER
business_goals_path = Path(VAULT_PATH) / BUSINESS_GOALS_FILE
memory_path = Path(VAULT_PATH) / MEMORY_FOLDER
logs_path = Path(VAULT_PATH) / LOGS_FOLDER

class BusinessGoalAlignmentEngine:
    def __init__(self):
        self.setup_memory_directory()
        self.business_goals = self.load_business_goals()
        self.load_memory()

    def setup_memory_directory(self):
        """Create memory directory if it doesn't exist"""
        memory_path.mkdir(parents=True, exist_ok=True)

    def load_business_goals(self):
        """Load business goals from Business_Goals.md"""
        goals = []
        if business_goals_path.exists():
            try:
                with open(business_goals_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse goals from markdown
                lines = content.split('\n')
                current_goal = None
                for line in lines:
                    line = line.strip()
                    if line.startswith('#') and 'Business Goals' in line:
                        continue
                    elif line.startswith('##'):
                        # New goal section
                        goal_title = line[2:].strip()  # Remove ##
                        current_goal = {
                            'title': goal_title,
                            'description': '',
                            'keywords': [],
                            'priority': 'medium'
                        }
                        goals.append(current_goal)
                    elif line.startswith('- **Priority:**'):
                        if current_goal:
                            current_goal['priority'] = line.replace('- **Priority:**', '').strip().lower()
                    elif line.startswith('- **Keywords:**'):
                        if current_goal:
                            keywords_str = line.replace('- **Keywords:**', '').strip()
                            current_goal['keywords'] = [k.strip() for k in keywords_str.split(',')]
                    elif current_goal and line and not line.startswith('-'):
                        # Add to description
                        if current_goal['description']:
                            current_goal['description'] += ' ' + line
                        else:
                            current_goal['description'] = line
            except Exception as e:
                print(f"Error loading business goals: {e}")
        
        return goals

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

    def calculate_goal_alignment_score(self, task_metadata: dict, task_content: str = "") -> tuple:
        """
        Calculate alignment score between task and business goals
        
        Returns:
            tuple: (alignment_score, business_value)
        """
        alignment_score = 0.0
        business_value = 0.0
        
        # Combine task metadata and content for keyword matching
        task_text = f"{task_metadata.get('subject', '')} {task_metadata.get('filename', '')} {task_metadata.get('type', '')} {task_content}".lower()
        
        # Calculate alignment with each business goal
        for goal in self.business_goals:
            goal_weight = 1.0
            if goal.get('priority') == 'high':
                goal_weight = 1.5
            elif goal.get('priority') == 'low':
                goal_weight = 0.7
            
            # Check for keywords in the task
            keyword_matches = 0
            for keyword in goal.get('keywords', []):
                if keyword.lower() in task_text:
                    keyword_matches += 1
            
            # Calculate goal-specific alignment
            goal_alignment = min(1.0, keyword_matches / max(1, len(goal.get('keywords', []))))
            alignment_score += goal_alignment * goal_weight
        
        # Normalize alignment score based on number of goals
        if self.business_goals:
            alignment_score = alignment_score / len(self.business_goals)
        
        # Calculate business value based on alignment and priority
        priority_multiplier = 1.0
        priority = task_metadata.get('priority', 'normal')
        if priority == 'high':
            priority_multiplier = 1.5
        elif priority == 'critical':
            priority_multiplier = 2.0
        elif priority == 'low':
            priority_multiplier = 0.7
        
        business_value = alignment_score * priority_multiplier
        
        # Ensure values are between 0 and 1
        alignment_score = max(0.0, min(1.0, alignment_score))
        business_value = max(0.0, min(1.0, business_value))
        
        return alignment_score, business_value

    def de_prioritize_low_value_tasks(self, task_file_path: Path, business_value: float):
        """De-prioritize tasks with low business value"""
        if business_value < 0.3:  # Threshold for low value
            # Update task to have lower priority
            updates = {
                'priority': 'low',
                'business_value': business_value,
                'de_prioritized': True,
                'de_prioritization_reason': 'Low business value alignment'
            }
            self.update_task_metadata(task_file_path, updates)
            print(f"De-prioritized task {task_file_path.name} due to low business value ({business_value:.2f})")

    def process_task_alignment(self, task_file_path: Path):
        """Process a single task for business goal alignment"""
        metadata = self.get_task_metadata(task_file_path)
        
        # Read task content for keyword matching
        try:
            with open(task_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            _, task_content = self.parse_yaml_frontmatter(content)
        except:
            task_content = ""
        
        # Calculate alignment and business value
        alignment_score, business_value = self.calculate_goal_alignment_score(metadata, task_content)
        
        # Update task with alignment data
        updates = {
            'goal_alignment_score': round(alignment_score, 2),
            'business_value': round(business_value, 2),
            'aligned_with_business_goals': True
        }
        
        self.update_task_metadata(task_file_path, updates)
        
        # De-prioritize if business value is low
        self.de_prioritize_low_value_tasks(task_file_path, business_value)
        
        print(f"Processed alignment for {task_file_path.name}: "
              f"Alignment={alignment_score:.2f}, Value={business_value:.2f}")

    def run_alignment_cycle(self):
        """Run one cycle of business goal alignment"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running business goal alignment cycle")
        
        # Process incoming tasks
        incoming_tasks = list(incoming_tasks_path.glob('*.md'))
        for task_file in incoming_tasks:
            self.process_task_alignment(task_file)
        
        # Process in-progress tasks
        in_progress_tasks = list(in_progress_tasks_path.glob('*.md'))
        for task_file in in_progress_tasks:
            self.process_task_alignment(task_file)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Business goal alignment cycle completed")

def main():
    """Main function to run the business goal alignment engine"""
    print("="*60)
    print("BUSINESS GOAL ALIGNMENT ENGINE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    engine = BusinessGoalAlignmentEngine()
    engine.run_alignment_cycle()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Business goal alignment completed")

if __name__ == "__main__":
    main()