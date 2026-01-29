#!/usr/bin/env python3
"""
Learning Memory for Personal AI Employee System

This module stores and retrieves learning patterns to improve
decision-making over time.
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
MEMORY_FOLDER = "Memory"
LOGS_FOLDER = "Logs"
COMPLETED_TASKS_FOLDER = "03_Completed_Tasks"
FAILED_TASKS_FOLDER = "05_Failed_Tasks"

# Convert to Path objects
memory_path = Path(VAULT_PATH) / MEMORY_FOLDER
logs_path = Path(VAULT_PATH) / LOGS_FOLDER
completed_tasks_path = Path(VAULT_PATH) / COMPLETED_TASKS_FOLDER
failed_tasks_path = Path(VAULT_PATH) / FAILED_TASKS_FOLDER

class LearningMemory:
    def __init__(self):
        self.setup_memory_directory()
        self.load_memory()

    def setup_memory_directory(self):
        """Create memory directory if it doesn't exist"""
        memory_path.mkdir(parents=True, exist_ok=True)

    def load_memory(self):
        """Load memory from stored files"""
        self.memory = {
            'success_patterns': {},
            'failure_patterns': {},
            'approval_patterns': {},
            'task_type_performance': {},
            'priority_effectiveness': {},
            'processing_strategies': {},
            'learning_timestamp': datetime.now().isoformat()
        }
        
        # Load each memory component
        for key in self.memory.keys():
            if key != 'learning_timestamp':  # Skip the timestamp
                file_path = memory_path / f"{key}.json"
                if file_path.exists():
                    try:
                        with open(file_path, 'r') as f:
                            self.memory[key] = json.load(f)
                    except Exception as e:
                        print(f"Error loading {key} from memory: {e}")
                        self.memory[key] = {}

    def save_memory(self):
        """Save memory to stored files"""
        for key, data in self.memory.items():
            if key != 'learning_timestamp':  # Don't save the timestamp as a separate file
                file_path = memory_path / f"{key}.json"
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
        
        # Update the timestamp
        self.memory['learning_timestamp'] = datetime.now().isoformat()

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

    def learn_from_success(self, task_file_path: Path):
        """Learn from successfully completed tasks"""
        metadata = self.get_task_metadata(task_file_path)
        
        task_type = metadata.get('type', 'unknown')
        priority = metadata.get('priority', 'normal')
        effort = metadata.get('estimated_effort', 'medium')
        confidence = metadata.get('confidence_score', 0.5)
        
        # Update success patterns
        if task_type not in self.memory['success_patterns']:
            self.memory['success_patterns'][task_type] = {
                'count': 0,
                'avg_confidence': 0,
                'successful_strategies': []
            }
        
        success_info = self.memory['success_patterns'][task_type]
        success_info['count'] += 1
        success_info['avg_confidence'] = (success_info['avg_confidence'] * (success_info['count'] - 1) + confidence) / success_info['count']
        
        # Record successful strategy
        strategy = f"{priority}_{effort}"
        if strategy not in success_info['successful_strategies']:
            success_info['successful_strategies'].append(strategy)
        
        # Update task type performance
        if task_type not in self.memory['task_type_performance']:
            self.memory['task_type_performance'][task_type] = {
                'success_rate': 0,
                'avg_completion_time': 0,
                'total_completed': 0
            }
        
        perf = self.memory['task_type_performance'][task_type]
        perf['total_completed'] += 1
        # Simplified success rate calculation - assume all completed tasks are successful
        perf['success_rate'] = min(1.0, perf['success_rate'] + (1.0 / perf['total_completed']))

    def learn_from_failure(self, task_file_path: Path):
        """Learn from failed tasks"""
        metadata = self.get_task_metadata(task_file_path)
        
        task_type = metadata.get('type', 'unknown')
        priority = metadata.get('priority', 'normal')
        effort = metadata.get('estimated_effort', 'medium')
        retry_count = metadata.get('retry_count', 0)
        
        # Update failure patterns
        if task_type not in self.memory['failure_patterns']:
            self.memory['failure_patterns'][task_type] = {
                'count': 0,
                'avg_retry_count': 0,
                'common_failure_modes': []
            }
        
        failure_info = self.memory['failure_patterns'][task_type]
        failure_info['count'] += 1
        failure_info['avg_retry_count'] = (failure_info['avg_retry_count'] * (failure_info['count'] - 1) + retry_count) / failure_info['count']
        
        # Record failure mode
        failure_mode = f"{priority}_{effort}_retry_{retry_count}"
        if failure_mode not in failure_info['common_failure_modes']:
            failure_info['common_failure_modes'].append(failure_mode)

    def learn_from_approvals(self, task_file_path: Path):
        """Learn from approval patterns"""
        metadata = self.get_task_metadata(task_file_path)
        
        requires_approval = metadata.get('approval', False)
        if requires_approval:
            approved = metadata.get('approved', False)
            task_type = metadata.get('type', 'unknown')
            priority = metadata.get('priority', 'normal')
            
            # Update approval patterns
            approval_key = f"{task_type}_{priority}"
            if approval_key not in self.memory['approval_patterns']:
                self.memory['approval_patterns'][approval_key] = {
                    'total_requests': 0,
                    'approved_count': 0,
                    'avg_approval_time': 0
                }
            
            approval_info = self.memory['approval_patterns'][approval_key]
            approval_info['total_requests'] += 1
            if approved:
                approval_info['approved_count'] += 1

    def learn_from_logs(self):
        """Learn from system logs"""
        # Analyze retry logs
        for log_file in logs_path.glob("retry_log_*.json"):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                
                for log_entry in logs:
                    reason = log_entry.get('reason', 'unknown')
                    task_file = log_entry.get('task_file', 'unknown')
                    
                    # Learn from failure reasons
                    if reason not in self.memory['failure_patterns']:
                        self.memory['failure_patterns'][reason] = {
                            'count': 0,
                            'related_tasks': []
                        }
                    
                    self.memory['failure_patterns'][reason]['count'] += 1
                    if task_file not in self.memory['failure_patterns'][reason]['related_tasks']:
                        self.memory['failure_patterns'][reason]['related_tasks'].append(task_file)
            except Exception as e:
                print(f"Error analyzing log {log_file}: {e}")

    def update_processing_strategies(self):
        """Update processing strategies based on learned patterns"""
        # Analyze success vs failure patterns to improve strategies
        for task_type, success_data in self.memory['success_patterns'].items():
            if task_type in self.memory['failure_patterns']:
                failure_data = self.memory['failure_patterns'][task_type]
                
                # Calculate success/failure ratio
                success_count = success_data['count']
                failure_count = failure_data['count']
                total = success_count + failure_count
                
                if total > 0:
                    success_rate = success_count / total
                    
                    # Update processing strategy based on success rate
                    if success_rate > 0.8:  # High success rate
                        strategy_key = f"{task_type}_high_success"
                        if strategy_key not in self.memory['processing_strategies']:
                            self.memory['processing_strategies'][strategy_key] = {
                                'confidence': 'high',
                                'recommended_priority': 'normal',
                                'success_rate': success_rate
                            }
                    elif success_rate < 0.5:  # Low success rate
                        strategy_key = f"{task_type}_low_success"
                        if strategy_key not in self.memory['processing_strategies']:
                            self.memory['processing_strategies'][strategy_key] = {
                                'confidence': 'low',
                                'recommended_priority': 'low',
                                'success_rate': success_rate,
                                'requires_review': True
                            }

    def learn_from_completed_tasks(self):
        """Learn from all completed tasks"""
        if completed_tasks_path.exists():
            for task_file in completed_tasks_path.glob('*.md'):
                self.learn_from_success(task_file)

    def learn_from_failed_tasks(self):
        """Learn from all failed tasks"""
        if failed_tasks_path.exists():
            for task_file in failed_tasks_path.glob('*.md'):
                self.learn_from_failure(task_file)

    def run_learning_cycle(self):
        """Run one cycle of learning from system data"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running learning memory cycle")
        
        # Load existing memory
        self.load_memory()
        
        # Learn from completed tasks
        self.learn_from_completed_tasks()
        
        # Learn from failed tasks
        self.learn_from_failed_tasks()
        
        # Learn from approval workflows
        # For this, we'll check tasks in completed that had approvals
        if completed_tasks_path.exists():
            for task_file in completed_tasks_path.glob('*.md'):
                metadata = self.get_task_metadata(task_file)
                if metadata.get('approval', False):
                    self.learn_from_approvals(task_file)
        
        # Learn from system logs
        self.learn_from_logs()
        
        # Update processing strategies based on learning
        self.update_processing_strategies()
        
        # Save updated memory
        self.save_memory()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Learning memory cycle completed")
        print(f"Memory updated with new patterns and strategies")

    def get_recommendations(self, task_metadata: dict) -> dict:
        """Get recommendations based on memory for a specific task"""
        recommendations = {}
        
        task_type = task_metadata.get('type', 'unknown')
        priority = task_metadata.get('priority', 'normal')
        
        # Get success patterns for this task type
        if task_type in self.memory['success_patterns']:
            success_data = self.memory['success_patterns'][task_type]
            recommendations['expected_success_rate'] = min(1.0, success_data['avg_confidence'])
            recommendations['successful_strategies'] = success_data.get('successful_strategies', [])
        
        # Get failure patterns for this task type
        if task_type in self.memory['failure_patterns']:
            failure_data = self.memory['failure_patterns'][task_type]
            recommendations['failure_risk'] = failure_data['avg_retry_count'] / 10.0  # Normalize
            recommendations['avoid_strategies'] = failure_data.get('common_failure_modes', [])
        
        # Get approval patterns
        approval_key = f"{task_type}_{priority}"
        if approval_key in self.memory['approval_patterns']:
            approval_data = self.memory['approval_patterns'][approval_key]
            if approval_data['total_requests'] > 0:
                approval_rate = approval_data['approved_count'] / approval_data['total_requests']
                recommendations['expected_approval_rate'] = approval_rate
        
        # Get processing strategy
        strategy_key = f"{task_type}_high_success"
        if strategy_key in self.memory['processing_strategies']:
            strategy = self.memory['processing_strategies'][strategy_key]
            recommendations['processing_strategy'] = strategy
        else:
            strategy_key = f"{task_type}_low_success"
            if strategy_key in self.memory['processing_strategies']:
                strategy = self.memory['processing_strategies'][strategy_key]
                recommendations['processing_strategy'] = strategy
                recommendations['requires_attention'] = True
        
        return recommendations

def main():
    """Main function to run the learning memory"""
    print("="*60)
    print("LEARNING MEMORY SYSTEM")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    memory = LearningMemory()
    memory.run_learning_cycle()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Learning memory cycle completed")

if __name__ == "__main__":
    main()