#!/usr/bin/env python3
"""
Autonomy Level Manager for Company-Scale AI Organization

This module manages autonomy levels for each department based on trust scores.
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
MEMORY_FOLDER = "Memory"
LOGS_FOLDER = "Logs"

# Department names
DEPARTMENTS = ["Sales", "Operations", "Support", "Finance"]

class AutonomyLevelManager:
    def __init__(self):
        self.memory_path = Path(VAULT_PATH) / MEMORY_FOLDER
        self.logs_path = Path(VAULT_PATH) / LOGS_FOLDER
        self.setup_manager()

    def setup_manager(self):
        """Setup autonomy manager structures"""
        self.logs_path.mkdir(parents=True, exist_ok=True)

    def get_current_trust_scores(self) -> Dict[str, float]:
        """Get current trust scores for all departments"""
        trust_scores = {}
        
        for dept in DEPARTMENTS:
            dept_memory_path = self.memory_path / f"{dept.lower()}_memory.json"
            if dept_memory_path.exists():
                try:
                    with open(dept_memory_path, 'r') as f:
                        dept_data = json.load(f)
                        trust_scores[dept] = dept_data.get('trust_score', 0.5)
                except Exception as e:
                    print(f"Error loading {dept} trust score: {e}")
                    trust_scores[dept] = 0.5  # Default value
            else:
                trust_scores[dept] = 0.5  # Default value
        
        return trust_scores

    def get_autonomy_level(self, trust_score: float) -> int:
        """Get autonomy level based on trust score"""
        if trust_score >= 0.85:
            return 4  # Self-direct
        elif trust_score >= 0.7:
            return 3  # Execute
        elif trust_score >= 0.5:
            return 2  # Recommend
        else:
            return 1  # Observe only

    def get_autonomy_description(self, level: int) -> str:
        """Get description of autonomy level"""
        descriptions = {
            1: "Observe only - Monitor activities without taking action",
            2: "Recommend - Suggest actions but require approval",
            3: "Execute - Perform actions independently",
            4: "Self-direct - Set own objectives and priorities"
        }
        return descriptions.get(level, "Unknown level")

    def adjust_autonomy_levels(self) -> Dict[str, Dict]:
        """Adjust autonomy levels for all departments based on trust scores"""
        trust_scores = self.get_current_trust_scores()
        adjustments = {}
        
        for dept, trust_score in trust_scores.items():
            current_level = self.get_autonomy_level(trust_score)
            
            # Load previous autonomy level if available
            prev_level = self.get_previous_autonomy_level(dept)
            
            # Determine if adjustment is needed
            adjustment_needed = current_level != prev_level
            
            adjustments[dept] = {
                'trust_score': trust_score,
                'current_level': current_level,
                'previous_level': prev_level,
                'adjustment_needed': adjustment_needed,
                'description': self.get_autonomy_description(current_level),
                'timestamp': datetime.now().isoformat()
            }
            
            # Save new autonomy level
            if adjustment_needed:
                self.save_autonomy_level(dept, current_level)
                print(f"Autonomy level adjusted for {dept}: {prev_level} -> {current_level}")
        
        return adjustments

    def get_previous_autonomy_level(self, dept: str) -> int:
        """Get the previous autonomy level for a department"""
        dept_memory_path = self.memory_path / f"{dept.lower()}_memory.json"
        if dept_memory_path.exists():
            try:
                with open(dept_memory_path, 'r') as f:
                    dept_data = json.load(f)
                    return dept_data.get('autonomy_level', 2)  # Default to level 2
            except Exception as e:
                print(f"Error loading {dept} previous autonomy level: {e}")
        
        return 2  # Default to level 2

    def save_autonomy_level(self, dept: str, level: int):
        """Save the current autonomy level for a department"""
        dept_memory_path = self.memory_path / f"{dept.lower()}_memory.json"
        
        # Load existing data
        dept_data = {}
        if dept_memory_path.exists():
            try:
                with open(dept_memory_path, 'r') as f:
                    dept_data = json.load(f)
            except Exception as e:
                print(f"Error loading {dept} data for autonomy update: {e}")
        
        # Update autonomy level
        dept_data['autonomy_level'] = level
        dept_data['last_autonomy_update'] = datetime.now().isoformat()
        
        # Save updated data
        with open(dept_memory_path, 'w') as f:
            json.dump(dept_data, f, indent=2)

    def log_autonomy_adjustment(self, adjustments: Dict[str, Dict]):
        """Log autonomy adjustments to the decision ledger"""
        log_entries = []
        
        for dept, adj_data in adjustments.items():
            if adj_data['adjustment_needed']:
                log_entry = {
                    'timestamp': adj_data['timestamp'],
                    'event_type': 'autonomy_adjustment',
                    'department': dept,
                    'previous_level': adj_data['previous_level'],
                    'new_level': adj_data['current_level'],
                    'trust_score': adj_data['trust_score'],
                    'reason': f"Trust score of {adj_data['trust_score']:.2f} warrants level change",
                    'description': adj_data['description']
                }
                log_entries.append(log_entry)
        
        if log_entries:
            # Save to autonomy adjustment log
            log_file = self.logs_path / f"autonomy_adjustment_log_{datetime.now().strftime('%Y%m')}.json"
            
            # Load existing logs if file exists
            logs = []
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                except:
                    logs = []
            
            # Append new log entries
            logs.extend(log_entries)
            
            # Write logs back to file
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            print(f"Logged {len(log_entries)} autonomy adjustments")

    def generate_autonomy_report(self, adjustments: Dict[str, Dict]) -> str:
        """Generate a report of autonomy levels"""
        report = f"""# Autonomy Level Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Current Autonomy Levels

"""
        
        for dept, adj_data in adjustments.items():
            report += f"""
### {dept} Department
- **Trust Score**: {adj_data['trust_score']:.2f}
- **Autonomy Level**: {adj_data['current_level']} - {adj_data['description']}
- **Previous Level**: {adj_data['previous_level']}
- **Adjustment Needed**: {'Yes' if adj_data['adjustment_needed'] else 'No'}
- **Last Updated**: {adj_data['timestamp']}

"""
        
        report += f"""
## Autonomy Level Definitions

- **Level 1 (Observe only)**: Monitor activities without taking action
- **Level 2 (Recommend)**: Suggest actions but require approval
- **Level 3 (Execute)**: Perform actions independently
- **Level 4 (Self-direct)**: Set own objectives and priorities

## Summary

- **Departments with Level 4 (Self-direct)**: {[dept for dept, adj in adjustments.items() if adj['current_level'] == 4]}
- **Departments with Level 3 (Execute)**: {[dept for dept, adj in adjustments.items() if adj['current_level'] == 3]}
- **Departments with Level 2 (Recommend)**: {[dept for dept, adj in adjustments.items() if adj['current_level'] == 2]}
- **Departments with Level 1 (Observe)**: {[dept for dept, adj in adjustments.items() if adj['current_level'] == 1]}

---
*Automatically generated by Autonomy Level Manager*
"""
        
        return report

    def save_autonomy_report(self, report_content: str):
        """Save the autonomy report to a file"""
        report_file = self.logs_path / f"Autonomy_Level_Report_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Autonomy level report saved to: {report_file}")
        return report_file

    def run_autonomy_management_cycle(self):
        """Run the autonomy management cycle"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running autonomy level management cycle")
        
        # Adjust autonomy levels based on trust scores
        adjustments = self.adjust_autonomy_levels()
        
        # Log adjustments
        self.log_autonomy_adjustment(adjustments)
        
        # Generate and save report
        report_content = self.generate_autonomy_report(adjustments)
        report_file = self.save_autonomy_report(report_content)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Autonomy management cycle completed. Report: {report_file}")
        
        return {
            'adjustments_made': sum(1 for adj in adjustments.values() if adj['adjustment_needed']),
            'total_departments': len(adjustments),
            'report_file': report_file
        }

def main():
    """Main function to run the autonomy level manager"""
    print("="*60)
    print("AUTONOMY LEVEL MANAGER")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    manager = AutonomyLevelManager()
    result = manager.run_autonomy_management_cycle()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Autonomy management completed")
    print(f"  Adjustments made: {result['adjustments_made']}")
    print(f"  Total departments: {result['total_departments']}")
    print(f"  Report: {result['report_file']}")

if __name__ == "__main__":
    main()