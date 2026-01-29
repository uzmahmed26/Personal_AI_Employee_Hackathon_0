#!/usr/bin/env python3
"""
Department AI Employees for Company-Scale AI Organization

This module creates virtual AI roles for different departments:
- Sales_AI
- Ops_AI
- Support_AI
- Finance_AI
Each with its own task scope, memory, and trust score.
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
DEPARTMENTS = ["Sales", "Operations", "Support", "Finance"]
MEMORY_FOLDER = "Memory"
LOGS_FOLDER = "Logs"

# Department-specific configurations
DEPARTMENT_CONFIGS = {
    "Sales": {
        "keywords": ["sales", "revenue", "customer", "prospect", "lead", "deal", "pipeline", "conversion"],
        "folder": "06_Sales_Tasks",
        "priority_keywords": ["hot_lead", "deal_close", "revenue_target"],
        "risk_factors": ["missed_quota", "lost_deal", "pipeline_gap"]
    },
    "Operations": {
        "keywords": ["ops", "process", "efficiency", "workflow", "optimization", "resource", "schedule", "delivery"],
        "folder": "07_Ops_Tasks",
        "priority_keywords": ["disruption", "delay", "bottleneck", "capacity"],
        "risk_factors": ["inefficiency", "cost_overrun", "timeline_slip"]
    },
    "Support": {
        "keywords": ["support", "ticket", "issue", "problem", "resolution", "customer", "service", "complaint"],
        "folder": "08_Support_Tasks",
        "priority_keywords": ["escalation", "sla_violation", "critical_issue", "dissatisfied_customer"],
        "risk_factors": ["response_time", "resolution_rate", "customer_satisfaction"]
    },
    "Finance": {
        "keywords": ["finance", "budget", "expense", "revenue", "forecast", "audit", "compliance", "payment"],
        "folder": "09_Finance_Tasks",
        "priority_keywords": ["budget_variance", "cash_flow", "audit_deadline", "compliance_issue"],
        "risk_factors": ["overspend", "revenue_shortfall", "compliance_violation"]
    }
}

class DepartmentAI:
    def __init__(self, dept_name: str):
        self.dept_name = dept_name
        self.config = DEPARTMENT_CONFIGS[dept_name]
        self.folder_path = Path(VAULT_PATH) / self.config["folder"]
        self.memory_path = Path(VAULT_PATH) / MEMORY_FOLDER / f"{dept_name.lower()}_memory.json"
        self.trust_score = 0.7  # Default trust score
        self.task_count = 0
        self.success_count = 0
        self.setup_department()
        self.load_memory()

    def setup_department(self):
        """Create department-specific folder and structures"""
        self.folder_path.mkdir(parents=True, exist_ok=True)
        
        # Create department-specific subfolders
        (self.folder_path / "Incoming").mkdir(exist_ok=True)
        (self.folder_path / "In_Progress").mkdir(exist_ok=True)
        (self.folder_path / "Completed").mkdir(exist_ok=True)
        (self.folder_path / "Failed").mkdir(exist_ok=True)

    def load_memory(self):
        """Load department memory from file"""
        if self.memory_path.exists():
            try:
                with open(self.memory_path, 'r') as f:
                    data = json.load(f)
                    self.trust_score = data.get('trust_score', 0.7)
                    self.task_count = data.get('task_count', 0)
                    self.success_count = data.get('success_count', 0)
            except Exception as e:
                print(f"Error loading {self.dept_name} memory: {e}")

    def save_memory(self):
        """Save department memory to file"""
        data = {
            'trust_score': self.trust_score,
            'task_count': self.task_count,
            'success_count': self.success_count,
            'last_updated': datetime.now().isoformat(),
            'dept_name': self.dept_name
        }
        
        with open(self.memory_path, 'w') as f:
            json.dump(data, f, indent=2)

    def parse_yaml_frontmatter(self, content: str) -> tuple:
        """
        Parse YAML frontmatter from markdown content
        """
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                content_without_frontmatter = parts[2].strip()
                try:
                    yaml_data = yaml.safe_load(yaml_content)
                    return yaml_data, content_without_frontmatter
                except yaml.YAMLError:
                    return {}, content
        return {}, content

    def get_task_metadata(self, file_path: Path) -> dict:
        """Get task metadata from YAML frontmatter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            yaml_data, _ = self.parse_yaml_frontmatter(content)
            return yaml_data or {}
        except Exception as e:
            print(f"Error reading task metadata from {file_path}: {e}")
            return {}

    def update_task_metadata(self, file_path: Path, updates: dict) -> bool:
        """Update task metadata in YAML frontmatter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            yaml_data, content_without_frontmatter = self.parse_yaml_frontmatter(content)

            if yaml_data:
                for key, value in updates.items():
                    yaml_data[key] = value
                yaml_data['last_updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                yaml_data['department'] = self.dept_name

                updated_content = "---\n" + yaml.dump(yaml_data, default_flow_style=False) + "---\n" + content_without_frontmatter

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                return True
            else:
                print(f"No YAML frontmatter found in {file_path}")
                return False
        except Exception as e:
            print(f"Error updating task metadata in {file_path}: {e}")
            return False

    def is_task_relevant(self, task_content: str, task_metadata: dict = None) -> bool:
        """Check if a task is relevant to this department"""
        content_lower = task_content.lower()
        
        # Check keywords in content
        for keyword in self.config["keywords"]:
            if keyword.lower() in content_lower:
                return True
        
        # Check keywords in metadata if provided
        if task_metadata:
            for keyword in self.config["keywords"]:
                for value in task_metadata.values():
                    if isinstance(value, str) and keyword.lower() in value.lower():
                        return True
        
        return False

    def route_task(self, task_file_path: Path) -> bool:
        """Route a task to this department if relevant"""
        try:
            with open(task_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            yaml_data, content_without_frontmatter = self.parse_yaml_frontmatter(content)
            
            if self.is_task_relevant(content, yaml_data):
                # Move task to department's incoming folder
                dest_path = self.folder_path / "Incoming" / task_file_path.name
                task_file_path.rename(dest_path)
                
                # Update metadata to reflect department assignment
                self.update_task_metadata(dest_path, {
                    'department': self.dept_name,
                    'routing_timestamp': datetime.now().isoformat(),
                    'initial_routing_score': 0.8  # High confidence in routing
                })
                
                print(f"Task routed to {self.dept_name}: {task_file_path.name}")
                return True
        except Exception as e:
            print(f"Error routing task to {self.dept_name}: {e}")
        
        return False

    def process_task(self, task_file_path: Path):
        """Process a task assigned to this department"""
        self.task_count += 1
        
        try:
            # Update task status to in-progress
            self.update_task_metadata(task_file_path, {
                'status': 'in_progress',
                'department_processing_start': datetime.now().isoformat()
            })
            
            # Simulate processing based on department logic
            success = self.simulate_processing_logic(task_file_path)
            
            if success:
                # Move to completed
                completed_path = self.folder_path / "Completed" / task_file_path.name
                task_file_path.rename(completed_path)
                
                # Update completion metadata
                self.update_task_metadata(completed_path, {
                    'status': 'completed',
                    'department_processing_end': datetime.now().isoformat(),
                    'processing_success': True
                })
                
                self.success_count += 1
                print(f"Task completed by {self.dept_name}: {task_file_path.name}")
            else:
                # Move to failed
                failed_path = self.folder_path / "Failed" / task_file_path.name
                task_file_path.rename(failed_path)
                
                # Update failure metadata
                self.update_task_metadata(failed_path, {
                    'status': 'failed',
                    'department_processing_end': datetime.now().isoformat(),
                    'processing_success': False,
                    'failure_reason': 'department_processing_error'
                })
                
                print(f"Task failed in {self.dept_name}: {task_file_path.name}")
        except Exception as e:
            print(f"Error processing task in {self.dept_name}: {e}")

    def simulate_processing_logic(self, task_file_path: Path) -> bool:
        """Simulate department-specific processing logic"""
        # This is a simplified simulation - in a real system, each department
        # would have its own complex processing logic
        metadata = self.get_task_metadata(task_file_path)
        
        # Calculate success probability based on various factors
        base_success_rate = 0.85
        
        # Adjust based on priority keywords
        content = ""
        try:
            with open(task_file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
        except:
            pass
        
        priority_boost = 0
        for keyword in self.config["priority_keywords"]:
            if keyword.lower() in content:
                priority_boost = 0.15
                break
        
        # Adjust based on risk factors
        risk_penalty = 0
        for factor in self.config["risk_factors"]:
            if factor.lower() in content:
                risk_penalty = 0.2
                break
        
        # Calculate final success probability
        success_prob = min(1.0, max(0.1, base_success_rate + priority_boost - risk_penalty))
        
        # Simulate success/failure based on probability
        import random
        return random.random() < success_prob

    def update_trust_score(self):
        """Update department's trust score based on performance"""
        if self.task_count > 0:
            success_rate = self.success_count / self.task_count
            # Weight recent performance more heavily
            self.trust_score = 0.7 * self.trust_score + 0.3 * success_rate
            # Ensure score stays between 0 and 1
            self.trust_score = max(0.0, min(1.0, self.trust_score))
        
        self.save_memory()

    def get_autonomy_level(self) -> int:
        """Get autonomy level based on trust score"""
        if self.trust_score >= 0.85:
            return 4  # Self-direct
        elif self.trust_score >= 0.7:
            return 3  # Execute
        elif self.trust_score >= 0.5:
            return 2  # Recommend
        else:
            return 1  # Observe only

    def get_dept_summary(self) -> dict:
        """Get summary of department performance"""
        return {
            'department': self.dept_name,
            'trust_score': round(self.trust_score, 3),
            'autonomy_level': self.get_autonomy_level(),
            'tasks_processed': self.task_count,
            'success_rate': round(self.success_count / max(1, self.task_count), 3),
            'active_tasks': len(list((self.folder_path / "In_Progress").glob('*.md'))),
            'pending_tasks': len(list((self.folder_path / "Incoming").glob('*.md'))),
            'completed_tasks': len(list((self.folder_path / "Completed").glob('*.md'))),
            'failed_tasks': len(list((self.folder_path / "Failed").glob('*.md')))
        }

class DepartmentAIRouter:
    def __init__(self):
        self.departments = {dept: DepartmentAI(dept) for dept in DEPARTMENTS}
        self.setup_executive_council()

    def setup_executive_council(self):
        """Create executive council folder"""
        council_path = Path(VAULT_PATH) / "Executive_Council"
        council_path.mkdir(parents=True, exist_ok=True)

    def route_task_by_type(self, task_file_path: Path):
        """Route task to appropriate department based on type and content"""
        try:
            with open(task_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to determine best department match
            dept_scores = {}
            for dept_name, dept_ai in self.departments.items():
                score = dept_ai.is_task_relevant(content, {})
                if score:
                    dept_scores[dept_name] = dept_ai.get_task_metadata(task_file_path).get('initial_routing_score', 0.5)
            
            # Route to department with highest score
            if dept_scores:
                best_dept = max(dept_scores, key=dept_scores.get)
                routed = self.departments[best_dept].route_task(task_file_path)
                if routed:
                    return True
        
        except Exception as e:
            print(f"Error in task routing: {e}")
        
        return False

    def process_department_tasks(self):
        """Process tasks for all departments"""
        for dept_name, dept_ai in self.departments.items():
            # Process incoming tasks
            incoming_tasks = list((dept_ai.folder_path / "Incoming").glob('*.md'))
            for task_file in incoming_tasks:
                dept_ai.process_task(task_file)
            
            # Update trust scores
            dept_ai.update_trust_score()

    def get_all_dept_summaries(self) -> List[dict]:
        """Get summaries for all departments"""
        summaries = []
        for dept_name, dept_ai in self.departments.items():
            summaries.append(dept_ai.get_dept_summary())
        return summaries

def main():
    """Main function to run the department AI router"""
    print("="*60)
    print("DEPARTMENT AI EMPLOYEES SYSTEM")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    router = DepartmentAIRouter()
    
    # Process tasks for all departments
    router.process_department_tasks()
    
    # Print department summaries
    summaries = router.get_all_dept_summaries()
    for summary in summaries:
        print(f"\n{summary['department']} Summary:")
        print(f"  Trust Score: {summary['trust_score']}")
        print(f"  Autonomy Level: {summary['autonomy_level']}")
        print(f"  Success Rate: {summary['success_rate']}")
        print(f"  Active Tasks: {summary['active_tasks']}")
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Department AI processing completed")

if __name__ == "__main__":
    main()