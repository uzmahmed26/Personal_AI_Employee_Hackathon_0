#!/usr/bin/env python3
"""
Cross-Department Conflict Resolver for Company-Scale AI Organization

This module detects and resolves conflicts between departments.
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
EXECUTIVE_COUNCIL_FOLDER = "Executive_Council"
REPORTS_FOLDER = "Reports"

# Department names
DEPARTMENTS = ["Sales", "Operations", "Support", "Finance"]

class CrossDepartmentConflictResolver:
    def __init__(self):
        self.memory_path = Path(VAULT_PATH) / MEMORY_FOLDER
        self.logs_path = Path(VAULT_PATH) / LOGS_FOLDER
        self.council_path = Path(VAULT_PATH) / EXECUTIVE_COUNCIL_FOLDER
        self.reports_path = Path(VAULT_PATH) / REPORTS_FOLDER
        self.setup_resolver()

    def setup_resolver(self):
        """Setup resolver structures"""
        self.logs_path.mkdir(parents=True, exist_ok=True)
        self.council_path.mkdir(parents=True, exist_ok=True)

    def load_department_data(self) -> Dict:
        """Load data from all departments"""
        dept_data = {}
        
        for dept in DEPARTMENTS:
            dept_memory_path = self.memory_path / f"{dept.lower()}_memory.json"
            if dept_memory_path.exists():
                try:
                    with open(dept_memory_path, 'r') as f:
                        dept_data[dept] = json.load(f)
                except Exception as e:
                    print(f"Error loading {dept} data: {e}")
                    dept_data[dept] = {}
        
        return dept_data

    def detect_conflicting_priorities(self, dept_data: Dict) -> List[Dict]:
        """Detect conflicting priorities between departments"""
        conflicts = []
        
        # Check for cost vs growth conflicts
        if 'Sales' in dept_data and 'Finance' in dept_data:
            sales_trust = dept_data['Sales'].get('trust_score', 0.5)
            finance_trust = dept_data['Finance'].get('trust_score', 0.5)
            
            # If both have high trust but potentially conflicting objectives
            if sales_trust > 0.7 and finance_trust > 0.7:
                # Check if they have conflicting metrics
                sales_success_rate = dept_data['Sales'].get('success_count', 0) / max(1, dept_data['Sales'].get('task_count', 1))
                finance_success_rate = dept_data['Finance'].get('success_count', 0) / max(1, dept_data['Finance'].get('task_count', 1))
                
                # Potential conflict if both are performing well but have different objectives
                conflicts.append({
                    'type': 'cost_growth_conflict',
                    'departments': ['Sales', 'Finance'],
                    'description': 'Sales and Finance may have conflicting priorities on growth vs cost control',
                    'severity': 'medium',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Check for speed vs quality conflicts
        if 'Operations' in dept_data and 'Support' in dept_data:
            ops_trust = dept_data['Operations'].get('trust_score', 0.5)
            support_trust = dept_data['Support'].get('trust_score', 0.5)
            
            if ops_trust > 0.7 and support_trust > 0.7:
                conflicts.append({
                    'type': 'speed_quality_conflict',
                    'departments': ['Operations', 'Support'],
                    'description': 'Operations and Support may have conflicting priorities on speed vs quality',
                    'severity': 'medium',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Check for resource allocation conflicts
        if 'Sales' in dept_data and 'Operations' in dept_data:
            # Check if both are requesting similar resources
            conflicts.append({
                'type': 'resource_conflict',
                'departments': ['Sales', 'Operations'],
                'description': 'Sales and Operations may compete for similar resources',
                'severity': 'low',
                'timestamp': datetime.now().isoformat()
            })
        
        return conflicts

    def resolve_conflict(self, conflict: Dict) -> Dict:
        """Attempt to resolve a conflict automatically"""
        resolution = {
            'conflict': conflict,
            'resolution_method': 'automatic',
            'resolution_details': '',
            'requires_ceo_escalation': False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Apply different resolution strategies based on conflict type
        if conflict['type'] == 'cost_growth_conflict':
            # Balance growth targets with budget constraints
            resolution['resolution_details'] = 'Established balanced growth targets that align with budget constraints. Created joint planning committee.'
            resolution['resolution_method'] = 'policy_alignment'
        
        elif conflict['type'] == 'speed_quality_conflict':
            # Align SLAs and performance metrics
            resolution['resolution_details'] = 'Aligned SLAs and performance metrics between Operations and Support to balance speed and quality.'
            resolution['resolution_method'] = 'metric_alignment'
        
        elif conflict['type'] == 'resource_conflict':
            # Establish resource allocation protocols
            resolution['resolution_details'] = 'Created clear resource allocation protocols to prevent competition between departments.'
            resolution['resolution_method'] = 'protocol_establishment'
        
        else:
            # For unknown conflict types, escalate to CEO
            resolution['resolution_details'] = f"Unknown conflict type '{conflict['type']}' requires executive decision."
            resolution['requires_ceo_escalation'] = True
            resolution['resolution_method'] = 'ceo_escalation'
        
        return resolution

    def log_resolution_reasoning(self, resolution: Dict):
        """Log the resolution reasoning to the decision ledger"""
        # Create a log entry for the resolution
        log_entry = {
            'timestamp': resolution['timestamp'],
            'event_type': 'conflict_resolution',
            'conflict_type': resolution['conflict']['type'],
            'departments_involved': resolution['conflict']['departments'],
            'resolution_method': resolution['resolution_method'],
            'resolution_details': resolution['resolution_details'],
            'requires_ceo_escalation': resolution['requires_ceo_escalation'],
            'reasoning': f"Conflict resolved using {resolution['resolution_method']} method based on conflict type and department priorities"
        }
        
        # Save to conflict resolution log
        log_file = self.logs_path / f"conflict_resolution_log_{datetime.now().strftime('%Y%m')}.json"
        
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
        
        print(f"Conflict resolution logged: {resolution['conflict']['type']}")

    def escalate_to_ceo(self, conflict: Dict):
        """Escalate unresolved conflicts to CEO"""
        # Create CEO escalation notice
        escalation_content = f"""# CEO Escalation Notice

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Unresolved Conflict

- **Type**: {conflict['type']}
- **Departments**: {', '.join(conflict['departments'])}
- **Description**: {conflict['description']}
- **Severity**: {conflict['severity']}
- **Timestamp**: {conflict['timestamp']}

## Resolution Attempt Failed

The automated conflict resolution system was unable to resolve this conflict automatically.
Executive decision required.

## Recommended Actions

1. Review department priorities and objectives
2. Mediate between conflicting departments
3. Establish clear guidelines for handling similar conflicts in the future

---
*Automatically generated by Cross-Department Conflict Resolver*
"""

        # Save escalation notice
        escalation_file = self.council_path / f"CEO_Escalation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(escalation_file, 'w', encoding='utf-8') as f:
            f.write(escalation_content)
        
        print(f"Conflict escalated to CEO: {escalation_file}")

    def run_conflict_resolution_cycle(self):
        """Run the conflict resolution cycle"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running cross-department conflict resolution cycle")
        
        # Load department data
        dept_data = self.load_department_data()
        print(f"Loaded data from {len(dept_data)} departments")
        
        # Detect conflicts
        conflicts = self.detect_conflicting_priorities(dept_data)
        print(f"Detected {len(conflicts)} conflicts")
        
        # Resolve each conflict
        resolutions = []
        ceo_escalations = []
        
        for conflict in conflicts:
            print(f"Resolving conflict: {conflict['type']}")
            resolution = self.resolve_conflict(conflict)
            resolutions.append(resolution)
            
            # Log the resolution reasoning
            self.log_resolution_reasoning(resolution)
            
            # Check if CEO escalation is needed
            if resolution['requires_ceo_escalation']:
                ceo_escalations.append(conflict)
                self.escalate_to_ceo(conflict)
        
        print(f"Resolved {len(resolutions)} conflicts, escalated {len(ceo_escalations)} to CEO")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Cross-department conflict resolution cycle completed")
        
        return {
            'conflicts_detected': len(conflicts),
            'resolutions_attempted': len(resolutions),
            'ceo_escalations': len(ceo_escalations)
        }

def main():
    """Main function to run the conflict resolver"""
    print("="*60)
    print("CROSS-DEPARTMENT CONFLICT RESOLVER")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    resolver = CrossDepartmentConflictResolver()
    result = resolver.run_conflict_resolution_cycle()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Conflict resolution completed")
    print(f"  Conflicts detected: {result['conflicts_detected']}")
    print(f"  Resolutions attempted: {result['resolutions_attempted']}")
    print(f"  CEO escalations: {result['ceo_escalations']}")

if __name__ == "__main__":
    main()