#!/usr/bin/env python3
"""
Risk Radar for Personal AI Employee System

This module continuously scans for risks and generates risk reports.
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import yaml
import json
from typing import Dict, List, Optional
from collections import Counter

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

class RiskRadar:
    def __init__(self):
        self.setup_reports_directory()

    def setup_reports_directory(self):
        """Create reports directory if it doesn't exist"""
        reports_path.mkdir(parents=True, exist_ok=True)

    def scan_failed_tasks(self) -> List[Dict]:
        """Scan for failed tasks and analyze patterns"""
        failed_risks = []
        
        if failed_tasks_path.exists():
            for task_file in failed_tasks_path.glob('*.md'):
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse metadata
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            yaml_content = parts[1]
                            try:
                                metadata = yaml.safe_load(yaml_content)
                                
                                risk = {
                                    'type': 'task_failure',
                                    'task_file': task_file.name,
                                    'task_type': metadata.get('type', 'unknown'),
                                    'priority': metadata.get('priority', 'normal'),
                                    'retry_count': metadata.get('retry_count', 0),
                                    'failure_reason': metadata.get('failure_reason', 'unknown'),
                                    'last_updated': metadata.get('last_updated', 'unknown'),
                                    'confidence': 0.8
                                }
                                
                                # Calculate risk level based on retry count and priority
                                if risk['retry_count'] > 5:
                                    risk['severity'] = 'high'
                                elif risk['retry_count'] > 2:
                                    risk['severity'] = 'medium'
                                else:
                                    risk['severity'] = 'low'
                                
                                failed_risks.append(risk)
                            except yaml.YAMLError:
                                continue
        
        return failed_risks

    def scan_delayed_tasks(self) -> List[Dict]:
        """Scan for tasks that have been delayed or stuck"""
        delayed_risks = []
        
        # Check in-progress tasks that have been there too long
        if in_progress_tasks_path.exists():
            for task_file in in_progress_tasks_path.glob('*.md'):
                try:
                    # Get file modification time
                    mod_time = datetime.fromtimestamp(task_file.stat().st_mtime)
                    age_hours = (datetime.now() - mod_time).total_seconds() / 3600
                    
                    with open(task_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse metadata
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            yaml_content = parts[1]
                            try:
                                metadata = yaml.safe_load(yaml_content)
                                
                                # Consider tasks in progress for more than 24 hours as potentially delayed
                                if age_hours > 24:
                                    risk = {
                                        'type': 'task_delay',
                                        'task_file': task_file.name,
                                        'task_type': metadata.get('type', 'unknown'),
                                        'priority': metadata.get('priority', 'normal'),
                                        'age_hours': round(age_hours, 2),
                                        'status': metadata.get('status', 'in_progress'),
                                        'assigned_to': metadata.get('assigned_to', 'system'),
                                        'confidence': 0.7
                                    }
                                    
                                    # Severity based on age
                                    if age_hours > 72:
                                        risk['severity'] = 'high'
                                    elif age_hours > 24:
                                        risk['severity'] = 'medium'
                                    else:
                                        risk['severity'] = 'low'
                                    
                                    delayed_risks.append(risk)
                            except yaml.YAMLError:
                                continue
                except Exception as e:
                    print(f"Error analyzing delayed task {task_file}: {e}")
        
        return delayed_risks

    def scan_approval_bottlenecks(self) -> List[Dict]:
        """Scan for approval bottlenecks"""
        bottleneck_risks = []
        
        if approval_workflows_path.exists():
            for task_file in approval_workflows_path.glob('*.md'):
                try:
                    # Get file modification time
                    mod_time = datetime.fromtimestamp(task_file.stat().st_mtime)
                    age_hours = (datetime.now() - mod_time).total_seconds() / 3600
                    
                    with open(task_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse metadata
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            yaml_content = parts[1]
                            try:
                                metadata = yaml.safe_load(yaml_content)
                                
                                risk = {
                                    'type': 'approval_bottleneck',
                                    'task_file': task_file.name,
                                    'task_type': metadata.get('type', 'unknown'),
                                    'priority': metadata.get('priority', 'normal'),
                                    'age_hours': round(age_hours, 2),
                                    'requester': metadata.get('requester', 'system'),
                                    'approval_required_by': metadata.get('approval_required_by', 'unknown'),
                                    'confidence': 0.9
                                }
                                
                                # Severity based on age
                                if age_hours > 48:
                                    risk['severity'] = 'high'
                                elif age_hours > 12:
                                    risk['severity'] = 'medium'
                                else:
                                    risk['severity'] = 'low'
                                
                                bottleneck_risks.append(risk)
                            except yaml.YAMLError:
                                continue
                except Exception as e:
                    print(f"Error analyzing approval bottleneck {task_file}: {e}")
        
        return bottleneck_risks

    def analyze_retry_logs(self) -> List[Dict]:
        """Analyze retry logs for patterns"""
        retry_risks = []
        
        # Look for recent retry logs
        for log_file in logs_path.glob("retry_log_*.json"):
            try:
                # Check if this is a recent log file (last 7 days)
                mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if datetime.now() - mod_time > timedelta(days=7):
                    continue
                
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                
                # Group by task file and count retries
                retry_counts = Counter(log['task_file'] for log in logs)
                
                for task_file, count in retry_counts.items():
                    if count > 5:  # Significant retry activity
                        risk = {
                            'type': 'high_retry_activity',
                            'task_file': task_file,
                            'retry_count': count,
                            'log_file': log_file.name,
                            'confidence': 0.8
                        }
                        
                        # Severity based on retry count
                        if count > 10:
                            risk['severity'] = 'high'
                        elif count > 5:
                            risk['severity'] = 'medium'
                        else:
                            risk['severity'] = 'low'
                        
                        retry_risks.append(risk)
            except Exception as e:
                print(f"Error analyzing retry log {log_file}: {e}")
        
        return retry_risks

    def categorize_risks(self, risks: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize risks by severity"""
        categorized = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        for risk in risks:
            severity = risk.get('severity', 'medium')
            if severity in categorized:
                categorized[severity].append(risk)
            else:
                categorized['medium'].append(risk)  # Default to medium
        
        return categorized

    def generate_risk_report(self) -> str:
        """Generate a comprehensive risk report"""
        # Scan for all types of risks
        failed_risks = self.scan_failed_tasks()
        delayed_risks = self.scan_delayed_tasks()
        bottleneck_risks = self.scan_approval_bottlenecks()
        retry_risks = self.analyze_retry_logs()
        
        # Combine all risks
        all_risks = failed_risks + delayed_risks + bottleneck_risks + retry_risks
        
        # Categorize risks
        categorized_risks = self.categorize_risks(all_risks)
        
        # Generate report content
        report_content = f"""# Risk Radar Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- **Total Risks Identified**: {len(all_risks)}
- **High Severity**: {len(categorized_risks['high'])}
- **Medium Severity**: {len(categorized_risks['medium'])}
- **Low Severity**: {len(categorized_risks['low'])}

## High Severity Risks
"""
        
        if categorized_risks['high']:
            for risk in categorized_risks['high']:
                report_content += f"""
### {risk['type'].replace('_', ' ').title()}: {risk['task_file']}
- **Type**: {risk['type']}
- **Severity**: {risk['severity'].upper()}
- **Details**: 
  - Task Type: {risk.get('task_type', 'N/A')}
  - Priority: {risk.get('priority', 'N/A')}
"""
                if risk['type'] == 'task_delay':
                    report_content += f"  - Age: {risk.get('age_hours', 0)} hours\n"
                elif risk['type'] == 'task_failure':
                    report_content += f"  - Retry Count: {risk.get('retry_count', 0)}\n"
                elif risk['type'] == 'approval_bottleneck':
                    report_content += f"  - Waiting for: {risk.get('age_hours', 0)} hours\n"
                elif risk['type'] == 'high_retry_activity':
                    report_content += f"  - Retry Count: {risk.get('retry_count', 0)}\n"
                
                report_content += f"  - Confidence: {risk.get('confidence', 0.5)}\n"
        else:
            report_content += "- No high severity risks identified\n"
        
        report_content += f"""

## Medium Severity Risks
"""
        
        if categorized_risks['medium']:
            for risk in categorized_risks['medium']:
                report_content += f"""
### {risk['type'].replace('_', ' ').title()}: {risk['task_file']}
- **Type**: {risk['type']}
- **Severity**: {risk['severity'].upper()}
- **Details**: 
  - Task Type: {risk.get('task_type', 'N/A')}
  - Priority: {risk.get('priority', 'N/A')}
"""
                if risk['type'] == 'task_delay':
                    report_content += f"  - Age: {risk.get('age_hours', 0)} hours\n"
                elif risk['type'] == 'task_failure':
                    report_content += f"  - Retry Count: {risk.get('retry_count', 0)}\n"
                elif risk['type'] == 'approval_bottleneck':
                    report_content += f"  - Waiting for: {risk.get('age_hours', 0)} hours\n"
                elif risk['type'] == 'high_retry_activity':
                    report_content += f"  - Retry Count: {risk.get('retry_count', 0)}\n"
                
                report_content += f"  - Confidence: {risk.get('confidence', 0.5)}\n"
        else:
            report_content += "- No medium severity risks identified\n"
        
        report_content += f"""

## Low Severity Risks
"""
        
        if categorized_risks['low']:
            for risk in categorized_risks['low']:
                report_content += f"""
### {risk['type'].replace('_', ' ').title()}: {risk['task_file']}
- **Type**: {risk['type']}
- **Severity**: {risk['severity'].upper()}
- **Details**: 
  - Task Type: {risk.get('task_type', 'N/A')}
  - Priority: {risk.get('priority', 'N/A')}
"""
                if risk['type'] == 'task_delay':
                    report_content += f"  - Age: {risk.get('age_hours', 0)} hours\n"
                elif risk['type'] == 'task_failure':
                    report_content += f"  - Retry Count: {risk.get('retry_count', 0)}\n"
                elif risk['type'] == 'approval_bottleneck':
                    report_content += f"  - Waiting for: {risk.get('age_hours', 0)} hours\n"
                elif risk['type'] == 'high_retry_activity':
                    report_content += f"  - Retry Count: {risk.get('retry_count', 0)}\n"
                
                report_content += f"  - Confidence: {risk.get('confidence', 0.5)}\n"
        else:
            report_content += "- No low severity risks identified\n"
        
        report_content += f"""

## Recommendations
Based on the identified risks, the following actions are recommended:

1. **Immediate Attention**: Address all high severity risks promptly
2. **Monitoring**: Keep an eye on medium severity risks for escalation
3. **Process Improvement**: Investigate root causes of recurring risks
4. **Resource Allocation**: Ensure adequate resources for high-priority tasks

---
*Automatically generated by Risk Radar System*
"""
        
        return report_content

    def save_risk_report(self, content: str):
        """Save the risk report to a file"""
        report_file = reports_path / f"Risk_Radar_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Risk radar report saved to: {report_file}")
        return report_file

    def run_risk_scan(self):
        """Run a complete risk scan and generate report"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running risk scan")
        
        # Generate report
        report_content = self.generate_risk_report()
        
        # Save report
        report_file = self.save_risk_report(report_content)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Risk scan completed. Report: {report_file}")
        
        return report_file

def main():
    """Main function to run the risk radar"""
    print("="*60)
    print("RISK RADAR SYSTEM")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    radar = RiskRadar()
    radar.run_risk_scan()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Risk radar scan completed")

if __name__ == "__main__":
    main()