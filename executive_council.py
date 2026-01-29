#!/usr/bin/env python3
"""
Executive Council Mode for Company-Scale AI Organization

This module manages the executive council that reviews department briefs
and generates strategic summaries.
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
EXECUTIVE_COUNCIL_FOLDER = "Executive_Council"
REPORTS_FOLDER = "Reports"
MEMORY_FOLDER = "Memory"
LOGS_FOLDER = "Logs"

# Department names
DEPARTMENTS = ["Sales", "Operations", "Support", "Finance"]

class ExecutiveCouncil:
    def __init__(self):
        self.council_path = Path(VAULT_PATH) / EXECUTIVE_COUNCIL_FOLDER
        self.reports_path = Path(VAULT_PATH) / REPORTS_FOLDER
        self.memory_path = Path(VAULT_PATH) / MEMORY_FOLDER
        self.logs_path = Path(VAULT_PATH) / LOGS_FOLDER
        self.setup_executive_council()

    def setup_executive_council(self):
        """Create executive council folder and structures"""
        self.council_path.mkdir(parents=True, exist_ok=True)
        self.reports_path.mkdir(parents=True, exist_ok=True)

    def collect_department_briefs(self) -> List[Dict]:
        """Collect briefs from all departments"""
        briefs = []
        
        for dept in DEPARTMENTS:
            # Look for department briefs in their memory
            dept_memory_path = self.memory_path / f"{dept.lower()}_memory.json"
            if dept_memory_path.exists():
                try:
                    with open(dept_memory_path, 'r') as f:
                        dept_data = json.load(f)
                    
                    brief = {
                        'department': dept,
                        'brief_data': dept_data,
                        'timestamp': dept_data.get('last_updated', datetime.now().isoformat()),
                        'trust_score': dept_data.get('trust_score', 0.5),
                        'task_metrics': {
                            'tasks_processed': dept_data.get('task_count', 0),
                            'success_count': dept_data.get('success_count', 0),
                            'success_rate': dept_data.get('success_count', 0) / max(1, dept_data.get('task_count', 1))
                        }
                    }
                    briefs.append(brief)
                except Exception as e:
                    print(f"Error reading {dept} brief: {e}")
        
        return briefs

    def detect_conflicts(self, briefs: List[Dict]) -> List[Dict]:
        """Detect potential conflicts between departments"""
        conflicts = []
        
        # Compare trust scores and autonomy levels
        dept_data = {}
        for brief in briefs:
            dept_name = brief['department']
            dept_data[dept_name] = brief
        
        # Check for conflicting priorities (simplified example)
        if 'Sales' in dept_data and 'Finance' in dept_data:
            sales_trust = dept_data['Sales']['trust_score']
            finance_trust = dept_data['Finance']['trust_score']
            
            # If both are high trust but have different priorities, flag potential conflict
            if sales_trust > 0.8 and finance_trust > 0.8:
                # Check if they have conflicting metrics (e.g., sales pushing for growth vs finance for cost control)
                conflicts.append({
                    'conflict_type': 'growth_vs_cost',
                    'departments_involved': ['Sales', 'Finance'],
                    'description': 'Both departments have high trust scores but may have conflicting priorities on growth vs cost control',
                    'severity': 'medium',
                    'recommendation': 'Align growth targets with budget constraints'
                })
        
        # Check for resource conflicts
        if 'Operations' in dept_data and 'Sales' in dept_data:
            ops_trust = dept_data['Operations']['trust_score']
            sales_trust = dept_data['Sales']['trust_score']
            
            if ops_trust > 0.7 and sales_trust > 0.7:
                conflicts.append({
                    'conflict_type': 'resource_allocation',
                    'departments_involved': ['Operations', 'Sales'],
                    'description': 'Both departments may compete for similar resources',
                    'severity': 'low',
                    'recommendation': 'Establish clear resource allocation protocols'
                })
        
        return conflicts

    def generate_council_summary(self, briefs: List[Dict], conflicts: List[Dict]) -> str:
        """Generate the executive council summary"""
        summary_content = f"""# Executive Council Summary

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Department Briefs

"""
        
        for brief in briefs:
            dept_name = brief['department']
            trust_score = brief['trust_score']
            success_rate = brief['task_metrics']['success_rate']
            tasks_processed = brief['task_metrics']['tasks_processed']
            
            summary_content += f"""
### {dept_name} Department
- **Trust Score**: {trust_score:.2f}
- **Success Rate**: {success_rate:.2f}
- **Tasks Processed**: {tasks_processed}
- **Autonomy Level**: {self.get_autonomy_level_from_trust(trust_score)}
- **Status**: {self.get_dept_status(trust_score, success_rate)}
"""
        
        summary_content += f"""

## Detected Conflicts

"""
        
        if conflicts:
            for conflict in conflicts:
                summary_content += f"""
### {conflict['conflict_type'].replace('_', ' ').title()}
- **Departments**: {', '.join(conflict['departments_involved'])}
- **Description**: {conflict['description']}
- **Severity**: {conflict['severity'].upper()}
- **Recommendation**: {conflict['recommendation']}
"""
        else:
            summary_content += "- No significant conflicts detected\n"
        
        summary_content += f"""

## Trade-offs Identified

"""
        
        # Identify trade-offs between departments
        trade_offs = self.identify_trade_offs(briefs)
        if trade_offs:
            for trade_off in trade_offs:
                summary_content += f"""
- **{trade_off['type']}**: {trade_off['description']}
  - **Impact**: {trade_off['impact']}
  - **Consideration**: {trade_off['consideration']}
"""
        else:
            summary_content += "- No significant trade-offs identified\n"
        
        summary_content += f"""

## Recommendations

"""
        
        # Generate recommendations based on briefs and conflicts
        recommendations = self.generate_recommendations(briefs, conflicts)
        for rec in recommendations:
            summary_content += f"- {rec}\n"
        
        summary_content += f"""

## Action Items

"""
        
        # Generate action items
        action_items = self.generate_action_items(conflicts)
        if action_items:
            for item in action_items:
                summary_content += f"- {item}\n"
        else:
            summary_content += "- No immediate action items\n"
        
        summary_content += f"""

---
*Automatically generated by Executive Council System*
"""

        return summary_content

    def get_autonomy_level_from_trust(self, trust_score: float) -> str:
        """Convert trust score to autonomy level"""
        if trust_score >= 0.85:
            return "Level 4: Self-direct"
        elif trust_score >= 0.7:
            return "Level 3: Execute"
        elif trust_score >= 0.5:
            return "Level 2: Recommend"
        else:
            return "Level 1: Observe only"

    def get_dept_status(self, trust_score: float, success_rate: float) -> str:
        """Get department status based on metrics"""
        if trust_score >= 0.8 and success_rate >= 0.8:
            return "Strong"
        elif trust_score >= 0.6 and success_rate >= 0.6:
            return "Stable"
        elif trust_score >= 0.4 or success_rate >= 0.4:
            return "Caution"
        else:
            return "At Risk"

    def identify_trade_offs(self, briefs: List[Dict]) -> List[Dict]:
        """Identify trade-offs between departments"""
        trade_offs = []
        
        # Example trade-offs based on department metrics
        dept_metrics = {brief['department']: brief for brief in briefs}
        
        # Growth vs Cost trade-off
        if 'Sales' in dept_metrics and 'Finance' in dept_metrics:
            sales_data = dept_metrics['Sales']
            finance_data = dept_metrics['Finance']
            
            if sales_data['trust_score'] > 0.7 and finance_data['trust_score'] > 0.7:
                trade_offs.append({
                    'type': 'Growth vs Cost Control',
                    'description': 'Sales department focused on growth while Finance focuses on cost control',
                    'impact': 'Potential tension in budget allocation and growth targets',
                    'consideration': 'Balance growth investments with financial sustainability'
                })
        
        # Speed vs Quality trade-off
        if 'Operations' in dept_metrics and 'Support' in dept_metrics:
            ops_data = dept_metrics['Operations']
            support_data = dept_metrics['Support']
            
            if ops_data['trust_score'] > 0.7 and support_data['trust_score'] > 0.7:
                trade_offs.append({
                    'type': 'Speed vs Quality',
                    'description': 'Operations focused on speed while Support focused on quality/resolution',
                    'impact': 'Potential tension between delivery speed and service quality',
                    'consideration': 'Align SLAs and performance metrics across departments'
                })
        
        return trade_offs

    def generate_recommendations(self, briefs: List[Dict], conflicts: List[Dict]) -> List[str]:
        """Generate recommendations based on briefs and conflicts"""
        recommendations = []
        
        # Add recommendations based on department performance
        for brief in briefs:
            dept_name = brief['department']
            trust_score = brief['trust_score']
            success_rate = brief['task_metrics']['success_rate']
            
            if trust_score < 0.5 or success_rate < 0.5:
                recommendations.append(f"Provide additional support to {dept_name} department to improve performance")
            elif trust_score > 0.8 and success_rate > 0.8:
                recommendations.append(f"Consider increasing autonomy level for {dept_name} department")
        
        # Add recommendations based on conflicts
        for conflict in conflicts:
            if conflict['severity'] == 'high':
                recommendations.append(f"Escalate {conflict['conflict_type']} conflict to executive leadership")
            elif conflict['severity'] == 'medium':
                recommendations.append(f"Schedule cross-departmental meeting for {', '.join(conflict['departments_involved'])}")
        
        # Add general recommendations
        if not recommendations:
            recommendations.append("Continue current operational approach")
            recommendations.append("Monitor department performance metrics regularly")
        
        return recommendations

    def generate_action_items(self, conflicts: List[Dict]) -> List[str]:
        """Generate action items based on conflicts"""
        action_items = []
        
        for conflict in conflicts:
            if conflict['severity'] == 'high':
                action_items.append(f"Resolve {conflict['conflict_type']} conflict immediately")
            elif conflict['severity'] == 'medium':
                action_items.append(f"Address {conflict['conflict_type']} conflict within 2 weeks")
        
        return action_items

    def save_council_summary(self, content: str):
        """Save the council summary to a file"""
        summary_file = self.council_path / f"Council_Summary_{datetime.now().strftime('%Y%m%d')}.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Executive council summary saved to: {summary_file}")
        return summary_file

    def run_executive_council_cycle(self):
        """Run the executive council cycle"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running executive council cycle")
        
        # Collect department briefs
        briefs = self.collect_department_briefs()
        print(f"Collected {len(briefs)} department briefs")
        
        # Detect conflicts
        conflicts = self.detect_conflicts(briefs)
        print(f"Detected {len(conflicts)} conflicts")
        
        # Generate summary
        summary_content = self.generate_council_summary(briefs, conflicts)
        
        # Save summary
        summary_file = self.save_council_summary(summary_content)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Executive council cycle completed. Summary: {summary_file}")
        
        return summary_file

def main():
    """Main function to run the executive council"""
    print("="*60)
    print("EXECUTIVE COUNCIL MODE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    council = ExecutiveCouncil()
    council.run_executive_council_cycle()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Executive council cycle completed")

if __name__ == "__main__":
    main()