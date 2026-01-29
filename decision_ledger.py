#!/usr/bin/env python3
"""
Decision Ledger for Personal AI Employee System

This module logs all major system decisions with context and expected outcomes.
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
DECISION_LEDGER_FOLDER = "Decision_Ledger"
LOGS_FOLDER = "Logs"
MEMORY_FOLDER = "Memory"

# Convert to Path objects
decision_ledger_path = Path(VAULT_PATH) / DECISION_LEDGER_FOLDER
logs_path = Path(VAULT_PATH) / LOGS_FOLDER
memory_path = Path(VAULT_PATH) / MEMORY_FOLDER

class DecisionLedger:
    def __init__(self):
        self.setup_decision_ledger_directory()

    def setup_decision_ledger_directory(self):
        """Create decision ledger directory if it doesn't exist"""
        decision_ledger_path.mkdir(parents=True, exist_ok=True)

    def log_decision(self, decision_type: str, decision_data: Dict):
        """
        Log a major system decision
        
        Args:
            decision_type (str): Type of decision (e.g., 'task_prioritization', 'strategy_change', 'approval_needed')
            decision_data (dict): Data about the decision including:
                - why: reason for the decision
                - data_used: data that informed the decision
                - expected_outcome: expected result
                - task_file: associated task file (optional)
                - confidence: confidence in the decision
        """
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
        
        # Create filename based on date
        date_str = datetime.now().strftime('%Y%m%d')
        ledger_file = decision_ledger_path / f"decision_ledger_{date_str}.md"
        
        # Format as markdown
        decision_markdown = f"""
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
        
        # Append to ledger file
        with open(ledger_file, 'a', encoding='utf-8') as f:
            f.write(decision_markdown)
        
        print(f"Decision logged: {decision_type} for {decision_entry['task_file']}")

    def log_task_prioritization(self, task_file: str, old_priority: str, new_priority: str, 
                               reason: str, data_used: List[str], confidence: float = 0.7):
        """Log a task prioritization decision"""
        decision_data = {
            'why': f"Changed priority from {old_priority} to {new_priority} because {reason}",
            'data_used': data_used,
            'expected_outcome': f"Task will be processed with {new_priority} priority",
            'task_file': task_file,
            'confidence': confidence,
            'system_state': {
                'action': 'priority_change',
                'old_priority': old_priority,
                'new_priority': new_priority
            }
        }
        
        self.log_decision('task_prioritization', decision_data)

    def log_strategy_change(self, task_file: str, old_strategy: str, new_strategy: str,
                          reason: str, data_used: List[str], confidence: float = 0.6):
        """Log a processing strategy change"""
        decision_data = {
            'why': f"Changed strategy from {old_strategy} to {new_strategy} because {reason}",
            'data_used': data_used,
            'expected_outcome': f"Task will be processed using {new_strategy} strategy",
            'task_file': task_file,
            'confidence': confidence,
            'system_state': {
                'action': 'strategy_change',
                'old_strategy': old_strategy,
                'new_strategy': new_strategy
            }
        }
        
        self.log_decision('strategy_change', decision_data)

    def log_approval_needed(self, task_file: str, reason: str, data_used: List[str], confidence: float = 0.8):
        """Log a decision that requires human approval"""
        decision_data = {
            'why': f"Human approval required because {reason}",
            'data_used': data_used,
            'expected_outcome': "Task will be moved to approval workflow",
            'task_file': task_file,
            'confidence': confidence,
            'system_state': {
                'action': 'requires_approval',
                'reason': reason
            }
        }
        
        self.log_decision('approval_needed', decision_data)

    def log_failure_analysis(self, task_file: str, failure_reason: str, retry_count: int,
                           corrective_action: str, data_used: List[str], confidence: float = 0.5):
        """Log a failure analysis and corrective action"""
        decision_data = {
            'why': f"Task failed after {retry_count} attempts due to {failure_reason}, applying {corrective_action}",
            'data_used': data_used,
            'expected_outcome': f"Corrective action '{corrective_action}' will resolve the issue",
            'task_file': task_file,
            'confidence': confidence,
            'system_state': {
                'action': 'failure_correction',
                'failure_reason': failure_reason,
                'retry_count': retry_count,
                'corrective_action': corrective_action
            }
        }
        
        self.log_decision('failure_analysis', decision_data)

    def log_business_alignment_decision(self, task_file: str, alignment_score: float, business_value: float,
                                     action_taken: str, data_used: List[str], confidence: float = 0.7):
        """Log a business goal alignment decision"""
        decision_data = {
            'why': f"Business alignment score: {alignment_score}, value: {business_value}. Action: {action_taken}",
            'data_used': data_used,
            'expected_outcome': f"Task will be processed according to business alignment ({action_taken})",
            'task_file': task_file,
            'confidence': confidence,
            'system_state': {
                'action': 'business_alignment',
                'alignment_score': alignment_score,
                'business_value': business_value,
                'action_taken': action_taken
            }
        }
        
        self.log_decision('business_alignment', decision_data)

    def get_recent_decisions(self, days_back: int = 7) -> List[Dict]:
        """Get recent decisions from the ledger"""
        decisions = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        for ledger_file in decision_ledger_path.glob("decision_ledger_*.md"):
            try:
                # Extract date from filename
                date_str = ledger_file.name.split('_')[2].split('.')[0]  # Gets YYYYMMDD
                file_date = datetime.strptime(date_str, '%Y%m%d')
                
                if file_date >= cutoff_date:
                    with open(ledger_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Simple parsing of decision entries
                    entries = content.split('## Decision Entry:')
                    for entry in entries[1:]:  # Skip first empty element
                        decisions.append(entry.strip())
            except Exception as e:
                print(f"Error reading ledger file {ledger_file}: {e}")
        
        return decisions

def main():
    """Main function to test the decision ledger"""
    print("="*60)
    print("DECISION LEDGER SYSTEM")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    ledger = DecisionLedger()
    
    # Example of logging a decision
    ledger.log_decision(
        decision_type='test_decision',
        decision_data={
            'why': 'Testing the decision logging system',
            'data_used': ['test_data', 'mock_values'],
            'expected_outcome': 'Decision should be logged successfully',
            'task_file': 'test_task.md',
            'confidence': 0.9,
            'system_state': {'test': True}
        }
    )
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Decision ledger initialized")

if __name__ == "__main__":
    from datetime import timedelta  # Import here to avoid conflicts
    main()