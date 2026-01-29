#!/usr/bin/env python3
"""
Trust Score System for Personal AI Employee System

This module maintains and manages a system trust score based on performance.
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import yaml
import json
from typing import Dict, List, Optional

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
MEMORY_FOLDER = "Memory"
LOGS_FOLDER = "Logs"
COMPLETED_TASKS_FOLDER = "03_Completed_Tasks"
FAILED_TASKS_FOLDER = "05_Failed_Tasks"
APPROVAL_WORKFLOWS_FOLDER = "04_Approval_Workflows"

# Convert to Path objects
memory_path = Path(VAULT_PATH) / MEMORY_FOLDER
logs_path = Path(VAULT_PATH) / LOGS_FOLDER
completed_tasks_path = Path(VAULT_PATH) / COMPLETED_TASKS_FOLDER
failed_tasks_path = Path(VAULT_PATH) / FAILED_TASKS_FOLDER
approval_workflows_path = Path(VAULT_PATH) / APPROVAL_WORKFLOWS_FOLDER

class TrustScoreSystem:
    def __init__(self):
        self.default_trust_score = 0.7  # Start with moderate trust
        self.trust_threshold = 0.5  # Below this, require approval
        self.max_trust_score = 1.0
        self.min_trust_score = 0.0
        self.setup_memory_directory()
        self.current_trust_score = self.load_trust_score()

    def setup_memory_directory(self):
        """Create memory directory if it doesn't exist"""
        memory_path.mkdir(parents=True, exist_ok=True)

    def load_trust_score(self) -> float:
        """Load the current trust score from memory"""
        trust_file = memory_path / "trust_score.json"
        if trust_file.exists():
            try:
                with open(trust_file, 'r') as f:
                    data = json.load(f)
                    return data.get('trust_score', self.default_trust_score)
            except Exception as e:
                print(f"Error loading trust score: {e}")
        
        # If no file exists, return default
        return self.default_trust_score

    def save_trust_score(self, score: float):
        """Save the current trust score to memory"""
        trust_file = memory_path / "trust_score.json"
        data = {
            'trust_score': score,
            'updated_at': datetime.now().isoformat(),
            'score_history': self.get_trust_history() + [score]
        }
        
        with open(trust_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_trust_history(self) -> List[float]:
        """Get the history of trust scores"""
        trust_file = memory_path / "trust_score.json"
        if trust_file.exists():
            try:
                with open(trust_file, 'r') as f:
                    data = json.load(f)
                    return data.get('score_history', [])
            except Exception as e:
                print(f"Error loading trust history: {e}")
        
        return []

    def calculate_task_success_rate(self) -> float:
        """Calculate the task success rate"""
        total_tasks = 0
        successful_tasks = 0
        
        # Count completed tasks (successful)
        if completed_tasks_path.exists():
            for task_file in completed_tasks_path.glob('*.md'):
                total_tasks += 1
                successful_tasks += 1
        
        # Count failed tasks
        if failed_tasks_path.exists():
            for task_file in failed_tasks_path.glob('*.md'):
                total_tasks += 1
                # Don't count failed tasks as successful
        
        if total_tasks == 0:
            return 0.8  # Default if no tasks processed yet
        
        return successful_tasks / total_tasks

    def calculate_approval_success_rate(self) -> float:
        """Calculate the approval success rate"""
        total_approval_tasks = 0
        approved_tasks = 0
        
        if approval_workflows_path.exists():
            for task_file in approval_workflows_path.glob('*.md'):
                total_approval_tasks += 1
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            yaml_content = parts[1]
                            try:
                                metadata = yaml.safe_load(yaml_content)
                                if metadata.get('approved', False):
                                    approved_tasks += 1
                            except yaml.YAMLError:
                                continue
                except Exception:
                    continue
        
        if total_approval_tasks == 0:
            return 1.0  # Default if no approval tasks
        
        return approved_tasks / total_approval_tasks if total_approval_tasks > 0 else 0.0

    def calculate_retry_frequency(self) -> float:
        """Calculate normalized retry frequency (lower is better)"""
        total_retry_attempts = 0
        task_count = 0
        
        # Look for retry logs
        for log_file in logs_path.glob("retry_log_*.json"):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                
                total_retry_attempts += len(logs)
                task_count += len(set(log['task_file'] for log in logs))  # Unique tasks
            except Exception as e:
                print(f"Error reading retry log {log_file}: {e}")
        
        if task_count == 0:
            return 0.1  # Low retry rate if no data
        
        avg_retries_per_task = total_retry_attempts / task_count
        # Normalize to 0-1 scale (assume anything over 5 retries per task is bad)
        return min(1.0, avg_retries_per_task / 5.0)

    def update_trust_score(self):
        """Update the trust score based on system performance"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating trust score")
        
        # Calculate various performance metrics
        success_rate = self.calculate_task_success_rate()
        approval_rate = self.calculate_approval_success_rate()
        retry_frequency = self.calculate_retry_frequency()
        
        print(f"Performance metrics - Success: {success_rate:.2f}, Approval: {approval_rate:.2f}, Retries: {retry_frequency:.2f}")
        
        # Calculate new trust score based on weighted factors
        # Success rate contributes positively (weight: 0.5)
        # Approval rate contributes positively (weight: 0.2)
        # Low retry frequency contributes positively (weight: 0.3)
        # Invert retry frequency so lower is better
        new_trust_score = (
            success_rate * 0.5 +
            approval_rate * 0.2 +
            (1.0 - retry_frequency) * 0.3
        )
        
        # Ensure score stays within bounds
        new_trust_score = max(self.min_trust_score, min(self.max_trust_score, new_trust_score))
        
        # Apply smoothing to prevent drastic changes
        smoothing_factor = 0.3
        smoothed_score = (self.current_trust_score * (1 - smoothing_factor) + 
                         new_trust_score * smoothing_factor)
        
        # Update the current trust score
        self.current_trust_score = smoothed_score
        
        # Save the updated score
        self.save_trust_score(self.current_trust_score)
        
        print(f"Trust score updated: {self.current_trust_score:.3f}")

    def is_autonomy_allowed(self) -> bool:
        """Check if full autonomy is allowed based on trust score"""
        return self.current_trust_score >= self.trust_threshold

    def get_autonomy_level(self) -> str:
        """Get the current autonomy level based on trust score"""
        if self.current_trust_score >= 0.8:
            return "full_autonomy"
        elif self.current_trust_score >= 0.6:
            return "reduced_autonomy"
        elif self.current_trust_score >= 0.4:
            return "supervised_operation"
        else:
            return "manual_control_required"

    def get_trust_score(self) -> float:
        """Get the current trust score"""
        return self.current_trust_score

    def run_trust_update_cycle(self):
        """Run a cycle to update the trust score"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running trust score update cycle")
        
        # Update the trust score based on system performance
        self.update_trust_score()
        
        # Log the current state
        autonomy_level = self.get_autonomy_level()
        print(f"Current trust score: {self.current_trust_score:.3f}")
        print(f"Autonomy level: {autonomy_level}")
        
        return {
            'trust_score': self.current_trust_score,
            'autonomy_level': autonomy_level,
            'is_autonomy_allowed': self.is_autonomy_allowed()
        }

def main():
    """Main function to run the trust score system"""
    print("="*60)
    print("TRUST SCORE SYSTEM")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    trust_system = TrustScoreSystem()
    result = trust_system.run_trust_update_cycle()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Trust score: {result['trust_score']:.3f}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Autonomy level: {result['autonomy_level']}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Autonomy allowed: {result['is_autonomy_allowed']}")
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Trust score update completed")

if __name__ == "__main__":
    main()