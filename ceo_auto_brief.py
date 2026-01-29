#!/usr/bin/env python3
"""
CEO Auto-Brief Mode for Personal AI Employee System

This module automatically generates action requests for the CEO when high risks are detected.
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
REPORTS_FOLDER = "Reports"
INCOMING_TASKS_FOLDER = "01_Incoming_Tasks"
IN_PROGRESS_TASKS_FOLDER = "02_In_Progress_Tasks"
COMPLETED_TASKS_FOLDER = "03_Completed_Tasks"
FAILED_TASKS_FOLDER = "05_Failed_Tasks"
APPROVAL_WORKFLOWS_FOLDER = "04_Approval_Workflows"
LOGS_FOLDER = "Logs"
MEMORY_FOLDER = "Memory"

# Convert to Path objects
reports_path = Path(VAULT_PATH) / REPORTS_FOLDER
incoming_tasks_path = Path(VAULT_PATH) / INCOMING_TASKS_FOLDER
in_progress_tasks_path = Path(VAULT_PATH) / IN_PROGRESS_TASKS_FOLDER
completed_tasks_path = Path(VAULT_PATH) / COMPLETED_TASKS_FOLDER
failed_tasks_path = Path(VAULT_PATH) / FAILED_TASKS_FOLDER
approval_workflows_path = Path(VAULT_PATH) / APPROVAL_WORKFLOWS_FOLDER
logs_path = Path(VAULT_PATH) / LOGS_FOLDER
memory_path = Path(VAULT_PATH) / MEMORY_FOLDER

class CEOAutoBriefMode:
    def __init__(self):
        self.setup_reports_directory()
        self.high_risk_threshold = 3  # Number of high risks to trigger CEO action

    def setup_reports_directory(self):
        """Create reports directory if it doesn't exist"""
        reports_path.mkdir(parents=True, exist_ok=True)

    def analyze_latest_risk_report(self) -> Dict:
        """Analyze the latest risk report to determine if CEO action is needed"""
        risk_summary = {
            'high_risks': 0,
            'medium_risks': 0,
            'low_risks': 0,
            'high_risk_items': [],
            'medium_risk_items': [],
            'low_risk_items': []
        }
        
        # Find the most recent risk report
        latest_report = None
        latest_date = datetime.min
        
        for report_file in reports_path.glob("Risk_Radar_*.md"):
            try:
                # Extract date from filename (format: Risk_Radar_YYYYMMDD.md)
                date_str = report_file.name.split('_')[2].split('.')[0]
                report_date = datetime.strptime(date_str, '%Y%m%d')
                
                if report_date > latest_date:
                    latest_date = report_date
                    latest_report = report_file
            except Exception as e:
                print(f"Error parsing report date from {report_file}: {e}")
        
        if not latest_report:
            print("No risk reports found")
            return risk_summary
        
        try:
            with open(latest_report, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple parsing to count risks by severity
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('## High Severity Risks'):
                    current_section = 'high'
                elif line.startswith('## Medium Severity Risks'):
                    current_section = 'medium'
                elif line.startswith('## Low Severity Risks'):
                    current_section = 'low'
                elif line.startswith('### ') and current_section:
                    if current_section == 'high':
                        risk_summary['high_risks'] += 1
                        risk_summary['high_risk_items'].append(line[4:])  # Remove '### '
                    elif current_section == 'medium':
                        risk_summary['medium_risks'] += 1
                        risk_summary['medium_risk_items'].append(line[4:])  # Remove '### '
                    elif current_section == 'low':
                        risk_summary['low_risks'] += 1
                        risk_summary['low_risk_items'].append(line[4:])  # Remove '### '
        except Exception as e:
            print(f"Error analyzing risk report {latest_report}: {e}")
        
        return risk_summary

    def should_trigger_ceo_action(self, risk_summary: Dict) -> bool:
        """Determine if CEO action should be triggered based on risk levels"""
        # Trigger CEO action if there are more than threshold high risks
        return risk_summary['high_risks'] >= self.high_risk_threshold

    def generate_ceo_action_request(self, risk_summary: Dict) -> str:
        """Generate a CEO action request based on risks"""
        urgent_items = risk_summary['high_risk_items'][:5]  # Limit to top 5 urgent items
        
        action_request = f"""# CEO Action Request

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## URGENT: Executive Decision Required

The system has identified **{risk_summary['high_risks']} HIGH RISK** items that require your immediate attention.

### Critical Issues Requiring Decision

"""
        
        for i, item in enumerate(urgent_items, 1):
            action_request += f"{i}. **{item}**\n\n"
        
        action_request += f"""
## Impact Assessment

- **Operational Impact**: {risk_summary['high_risks']} high-risk items may affect system performance
- **Timeline Risk**: Delays in resolution could cascade to other tasks
- **Resource Impact**: May require allocation of additional resources

## Recommended Decisions Needed

"""
        
        # Generate specific decision points based on risk types
        if risk_summary['high_risks'] > 0:
            action_request += "1. **Approve escalation protocols** for high-risk tasks\n"
            action_request += "2. **Allocate additional resources** to address critical failures\n"
            action_request += "3. **Review approval processes** to reduce bottlenecks\n"
        
        action_request += f"""
## Deadline for Response

**Required by**: {datetime.now() + timedelta(days=1):%Y-%m-%d} (within 24 hours)

Failure to address these items may result in:
- Extended system downtime
- Missed business objectives
- Compromised task completion rates

## Supporting Information

- Total High Risks: {risk_summary['high_risks']}
- Total Medium Risks: {risk_summary['medium_risks']}
- Total Low Risks: {risk_summary['low_risks']}
- Latest Risk Report: Risk_Radar_{datetime.now().strftime('%Y%m%d')}.md

---
*This request was automatically generated by CEO Auto-Brief Mode*
*System Status: Awaiting executive decision*
"""

        return action_request

    def save_ceo_action_request(self, content: str):
        """Save the CEO action request to a file"""
        request_file = reports_path / f"CEO_Action_Request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(request_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"CEO action request saved to: {request_file}")
        return request_file

    def run_auto_brief_cycle(self):
        """Run the auto-brief cycle to check for CEO action needs"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running CEO auto-brief cycle")
        
        # Analyze the latest risk report
        risk_summary = self.analyze_latest_risk_report()
        
        print(f"Risk analysis: {risk_summary['high_risks']} high, {risk_summary['medium_risks']} medium, {risk_summary['low_risks']} low risks")
        
        # Check if CEO action is needed
        if self.should_trigger_ceo_action(risk_summary):
            print("High risk threshold exceeded - generating CEO action request")
            
            # Generate and save CEO action request
            action_request = self.generate_ceo_action_request(risk_summary)
            request_file = self.save_ceo_action_request(action_request)
            
            print(f"CEO action request generated: {request_file}")
            return True
        else:
            print("Risk levels acceptable - no CEO action required")
            return False

def main():
    """Main function to run the CEO auto-brief mode"""
    print("="*60)
    print("CEO AUTO-BRIEF MODE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    auto_brief = CEOAutoBriefMode()
    triggered = auto_brief.run_auto_brief_cycle()
    
    if triggered:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] CEO action request generated")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] No CEO action required")
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] CEO auto-brief cycle completed")

if __name__ == "__main__":
    main()