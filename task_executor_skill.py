#!/usr/bin/env python3
"""
Task Executor Skill for Autonomous AI Employee System

This module implements the Autonomous AI Employee Task Executor skill
that creates, processes, and manages tasks through the intelligent workflow.
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import yaml
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/task_executor.log'),
        logging.StreamHandler()
    ]
)

# Configuration constants
VAULT_PATH = Path(__file__).parent
INCOMING_TASKS_FOLDER = VAULT_PATH / "01_Incoming_Tasks"
IN_PROGRESS_TASKS_FOLDER = VAULT_PATH / "02_In_Progress_Tasks"
COMPLETED_TASKS_FOLDER = VAULT_PATH / "03_Completed_Tasks"
APPROVAL_WORKFLOWS_FOLDER = VAULT_PATH / "04_Approval_Workflows"
FAILED_TASKS_FOLDER = VAULT_PATH / "05_Failed_Tasks"
DECISION_LEDGER_FOLDER = VAULT_PATH / "Decision_Ledger"
MEMORY_FOLDER = VAULT_PATH / "Memory"
BUSINESS_GOALS_FILE = VAULT_PATH / "Business_Goals.md"

# Ensure directories exist
for folder in [INCOMING_TASKS_FOLDER, IN_PROGRESS_TASKS_FOLDER, COMPLETED_TASKS_FOLDER,
               APPROVAL_WORKFLOWS_FOLDER, FAILED_TASKS_FOLDER, DECISION_LEDGER_FOLDER, MEMORY_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)


class TaskExecutorSkill:
    """
    Autonomous AI Employee Task Executor Skill
    
    Creates, processes, and manages tasks through the intelligent workflow pipeline.
    """
    
    def __init__(self):
        self.business_goals = self.load_business_goals()
        self.memory_data = self.load_memory()
        logging.info("Task Executor Skill initialized")
    
    def load_business_goals(self) -> List[Dict]:
        """Load business goals from Business_Goals.md"""
        goals = []
        if BUSINESS_GOALS_FILE.exists():
            try:
                with open(BUSINESS_GOALS_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                current_goal = None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('##'):
                        goal_title = line[2:].strip()
                        current_goal = {
                            'title': goal_title,
                            'description': '',
                            'keywords': [],
                            'priority': 'medium'
                        }
                        goals.append(current_goal)
                    elif line.startswith('- **Priority:**') and current_goal:
                        current_goal['priority'] = line.replace('- **Priority:**', '').strip().lower()
                    elif line.startswith('- **Keywords:**') and current_goal:
                        keywords_str = line.replace('- **Keywords:**', '').strip()
                        current_goal['keywords'] = [k.strip() for k in keywords_str.split(',')]
                    elif current_goal and line and not line.startswith('-'):
                        if current_goal['description']:
                            current_goal['description'] += ' ' + line
                        else:
                            current_goal['description'] = line
            except Exception as e:
                logging.error(f"Error loading business goals: {e}")
        
        return goals
    
    def load_memory(self) -> Dict:
        """Load memory data (success/failure patterns)"""
        memory = {
            'success_patterns': {},
            'failure_patterns': {}
        }
        
        success_file = MEMORY_FOLDER / "success_patterns.json"
        failure_file = MEMORY_FOLDER / "failure_patterns.json"
        
        if success_file.exists():
            try:
                with open(success_file, 'r') as f:
                    memory['success_patterns'] = json.load(f)
            except:
                pass
        
        if failure_file.exists():
            try:
                with open(failure_file, 'r') as f:
                    memory['failure_patterns'] = json.load(f)
            except:
                pass
        
        return memory
    
    def generate_task_id(self) -> str:
        """Generate unique task ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:6]
        return f"task_{timestamp}_{unique_id}"
    
    def calculate_goal_alignment(self, task_metadata: Dict, task_content: str) -> Tuple[float, float, List[str]]:
        """
        Calculate alignment with business goals
        
        Returns:
            tuple: (alignment_score, business_value, aligned_goals)
        """
        alignment_score = 0.0
        aligned_goals = []
        
        task_text = f"{task_metadata.get('subject', '')} {task_metadata.get('filename', '')} {task_metadata.get('type', '')} {task_content}".lower()
        
        for goal in self.business_goals:
            goal_weight = 1.0
            if goal.get('priority') == 'high':
                goal_weight = 1.5
            elif goal.get('priority') == 'low':
                goal_weight = 0.7
            
            keyword_matches = sum(1 for keyword in goal.get('keywords', []) if keyword.lower() in task_text)
            
            if keyword_matches > 0:
                goal_alignment = min(1.0, keyword_matches / max(1, len(goal.get('keywords', []))))
                alignment_score += goal_alignment * goal_weight
                aligned_goals.append(goal['title'])
        
        if self.business_goals:
            alignment_score = alignment_score / len(self.business_goals)
        
        priority_multiplier = {
            'critical': 2.0,
            'high': 1.5,
            'medium': 1.0,
            'low': 0.7
        }.get(task_metadata.get('priority', 'medium'), 1.0)
        
        business_value = min(1.0, alignment_score * priority_multiplier)
        
        return round(alignment_score, 2), round(business_value, 2), aligned_goals
    
    def assess_risk(self, task_metadata: Dict, task_content: str) -> Tuple[str, List[str]]:
        """
        Assess task risk level
        
        Returns:
            tuple: (risk_level, risk_factors)
        """
        risk_factors = []
        risk_score = 0.0
        
        # Check for financial implications
        if any(keyword in task_content.lower() for keyword in ['budget', 'cost', 'payment', '$', 'financial']):
            risk_factors.append('financial_implications')
            risk_score += 0.3
        
        # Check for approval requirement
        if task_metadata.get('approval', False):
            risk_factors.append('requires_approval')
            risk_score += 0.2
        
        # Check for high priority
        if task_metadata.get('priority') in ['critical', 'high']:
            risk_factors.append('high_priority')
            risk_score += 0.2
        
        # Check for legal/compliance
        if any(keyword in task_content.lower() for keyword in ['legal', 'compliance', 'contract', 'agreement']):
            risk_factors.append('legal_compliance')
            risk_score += 0.3
        
        # Determine risk level
        if risk_score >= 0.6:
            risk_level = 'high'
        elif risk_score >= 0.3:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return risk_level, risk_factors
    
    def create_task_file(self, task_metadata: Dict, task_content: str, destination_folder: Path = None) -> Path:
        """
        Create a task file with YAML frontmatter
        
        Args:
            task_metadata: Dictionary containing task metadata
            task_content: Markdown content for the task
            destination_folder: Optional folder to save the task (default: 01_Incoming_Tasks)
        
        Returns:
            Path: Path to the created task file
        """
        if destination_folder is None:
            destination_folder = INCOMING_TASKS_FOLDER
        
        # Ensure metadata has required fields
        if 'task_id' not in task_metadata:
            task_metadata['task_id'] = self.generate_task_id()
        if 'created' not in task_metadata:
            task_metadata['created'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        if 'status' not in task_metadata:
            task_metadata['status'] = 'pending_review'
        
        # Calculate business alignment
        alignment_score, business_value, aligned_goals = self.calculate_goal_alignment(task_metadata, task_content)
        task_metadata['goal_alignment_score'] = alignment_score
        task_metadata['business_value'] = business_value
        if aligned_goals:
            task_metadata['aligned_goals'] = aligned_goals
        
        # Assess risk
        risk_level, risk_factors = self.assess_risk(task_metadata, task_content)
        task_metadata['risk_level'] = risk_level
        if risk_factors:
            task_metadata['risk_factors'] = risk_factors
        
        # Build YAML frontmatter
        yaml_content = yaml.dump(task_metadata, default_flow_style=False, allow_unicode=True)
        
        # Create full task content
        full_content = f"---\n{yaml_content}---\n\n{task_content}"
        
        # Generate filename from task_id
        filename = f"{task_metadata['task_id']}.md"
        task_path = destination_folder / filename
        
        # Write task file
        with open(task_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        logging.info(f"Task created: {filename} in {destination_folder.name}")
        
        return task_path
    
    def log_decision(self, decision_type: str, decision_data: Dict) -> Path:
        """
        Log a decision to the Decision Ledger
        
        Args:
            decision_type: Type of decision
            decision_data: Dictionary containing decision details
        
        Returns:
            Path: Path to the ledger file
        """
        date_str = datetime.now().strftime('%Y%m%d')
        ledger_file = DECISION_LEDGER_FOLDER / f"decision_ledger_{date_str}.md"
        
        decision_entry = {
            'timestamp': datetime.now().isoformat(),
            'decision_type': decision_type,
            'why': decision_data.get('why', 'Unknown reason'),
            'data_used': decision_data.get('data_used', []),
            'expected_outcome': decision_data.get('expected_outcome', 'Unknown outcome'),
            'task_file': decision_data.get('task_file', 'N/A'),
            'confidence': decision_data.get('confidence', 0.5),
            'system_state': decision_data.get('system_state', {})
        }
        
        # Format as markdown
        entry_markdown = f"""
## Decision Entry: {decision_entry['timestamp']}

- **Type**: {decision_entry['decision_type']}
- **Why**: {decision_entry['why']}
- **Data Used**: {', '.join(decision_entry['data_used']) if decision_entry['data_used'] else 'N/A'}
- **Expected Outcome**: {decision_entry['expected_outcome']}
- **Associated Task**: {decision_entry['task_file']}
- **Confidence Level**: {decision_entry['confidence']}
- **System State**: {json.dumps(decision_entry['system_state'], indent=2)}

---
"""
        
        # Append to ledger
        with open(ledger_file, 'a', encoding='utf-8') as f:
            f.write(entry_markdown)
        
        logging.info(f"Decision logged: {decision_type}")
        
        return ledger_file
    
    def execute_task(self, task_type: str, description: str, priority: str = 'medium',
                    approval_required: bool = False, metadata: Dict = None) -> Dict:
        """
        Execute the task creation workflow
        
        Args:
            task_type: Type of task (file_arrival, email, approval_required, etc.)
            description: Task description
            priority: Priority level (critical, high, medium, low)
            approval_required: Whether human approval is needed
            metadata: Additional metadata
        
        Returns:
            Dict: Task creation result with summary
        """
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'type': task_type,
            'priority': priority,
            'approval': approval_required
        })
        
        # Create task content
        task_content = f"""## Task: {task_type.replace('_', ' ').title()}

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** {priority.title()}
**Approval Required:** {'Yes' if approval_required else 'No'}

### Description
{description}

### Action Required
Process this task according to standard operating procedures.

---
*Generated by Task Executor Skill*
"""
        
        # Create task file
        task_path = self.create_task_file(metadata, task_content)
        
        # Log decision
        self.log_decision('task_creation', {
            'why': f"New task created: {task_type} with {priority} priority",
            'data_used': [task_type, priority, str(approval_required)],
            'expected_outcome': 'Task will be processed by Ralph Loop',
            'task_file': task_path.name,
            'confidence': 0.9,
            'system_state': {
                'action': 'task_creation',
                'task_type': task_type,
                'priority': priority,
                'approval_required': approval_required
            }
        })
        
        # Determine next steps
        if approval_required:
            # Move to approval workflows
            approval_path = APPROVAL_WORKFLOWS_FOLDER / task_path.name
            task_path.rename(approval_path)
            next_steps = [
                "Task moved to 04_Approval_Workflows/",
                "Awaiting human approval",
                "Set `approved: true` to proceed"
            ]
            status = 'awaiting_approval'
        else:
            next_steps = [
                "Task will be processed by Ralph Loop",
                "Auto-routing based on confidence score",
                "Check 02_In_Progress_Tasks/ for progress"
            ]
            status = 'pending_review'
        
        # Build summary
        summary = {
            'success': True,
            'task_id': metadata['task_id'],
            'task_type': task_type,
            'priority': priority,
            'status': status,
            'location': str(task_path.parent.name),
            'business_alignment': {
                'goal_alignment_score': metadata.get('goal_alignment_score', 0),
                'business_value': metadata.get('business_value', 0),
                'aligned_goals': metadata.get('aligned_goals', [])
            },
            'risk_assessment': {
                'risk_level': metadata.get('risk_level', 'low'),
                'risk_factors': metadata.get('risk_factors', [])
            },
            'next_steps': next_steps,
            'decision_log': f"Decision_Ledger/decision_ledger_{datetime.now().strftime('%Y%m%d')}.md"
        }
        
        return summary
    
    def format_summary(self, summary: Dict) -> str:
        """Format task creation summary as markdown"""
        markdown = f"""## ✅ Task Created Successfully

**Task ID:** `{summary['task_id']}`
**Type:** {summary['task_type']}
**Priority:** {summary['priority']}
**Status:** {summary['status']}
**Location:** {summary['location']}

### Business Alignment
- **Goal Alignment Score:** {summary['business_alignment']['goal_alignment_score']}
- **Business Value:** {summary['business_alignment']['business_value']}
- **Aligned Goals:** {', '.join(summary['business_alignment']['aligned_goals']) if summary['business_alignment']['aligned_goals'] else 'None identified'}

### Risk Assessment
- **Risk Level:** {summary['risk_assessment']['risk_level']}
- **Risk Factors:** {', '.join(summary['risk_assessment']['risk_factors']) if summary['risk_assessment']['risk_factors'] else 'None'}

### Next Steps
"""
        for step in summary['next_steps']:
            markdown += f"- {step}\n"
        
        markdown += f"\n### Decision Log\nDecision recorded in: `{summary['decision_log']}`\n"
        
        return markdown


def main():
    """Main function to demonstrate the Task Executor Skill"""
    # Fix Windows console encoding
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("="*60)
    print("TASK EXECUTOR SKILL - Autonomous AI Employee System")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    executor = TaskExecutorSkill()
    
    # Example 1: File processing task
    print("\n[TASK] Creating Example Task 1: File Processing\n")
    summary1 = executor.execute_task(
        task_type='file_arrival',
        description='Process quarterly report PDF from Inbox',
        priority='high',
        approval_required=False,
        metadata={
            'filename': 'quarterly_report_Q4_2025.pdf',
            'size': '3.2 MB'
        }
    )
    print(executor.format_summary(summary1))
    
    # Example 2: Approval required task
    print("\n[TASK] Creating Example Task 2: Approval Required\n")
    summary2 = executor.execute_task(
        task_type='approval_required',
        description='Marketing budget approval request for $50,000 Q1 campaign',
        priority='critical',
        approval_required=True,
        metadata={
            'approval_type': 'financial',
            'amount': 50000,
            'currency': 'USD',
            'approver': 'CEO',
            'deadline': '2026-02-25'
        }
    )
    print(executor.format_summary(summary2))
    
    print("\n[SUCCESS] Task Executor Skill demonstration completed!")
    print(f"Check 01_Incoming_Tasks/ and 04_Approval_Workflows/ for created tasks")
    print(f"Check Decision_Ledger/ for decision logs")


if __name__ == "__main__":
    main()
