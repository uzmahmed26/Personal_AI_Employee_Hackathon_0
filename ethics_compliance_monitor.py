#!/usr/bin/env python3
"""
Ethics & Compliance Monitor for Company-Scale AI Organization

This module scans tasks and decisions for ethical and compliance issues.
"""

import os
import time
from pathlib import Path
from datetime import datetime
import json
import yaml
from typing import Dict, List, Optional

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
MEMORY_FOLDER = "Memory"
LOGS_FOLDER = "Logs"
REPORTS_FOLDER = "Reports"
GOVERNANCE_FOLDER = "Governance"

class EthicsComplianceMonitor:
    def __init__(self):
        self.memory_path = Path(VAULT_PATH) / MEMORY_FOLDER
        self.logs_path = Path(VAULT_PATH) / LOGS_FOLDER
        self.reports_path = Path(VAULT_PATH) / REPORTS_FOLDER
        self.governance_path = Path(VAULT_PATH) / GOVERNANCE_FOLDER
        self.setup_monitor()

    def setup_monitor(self):
        """Setup ethics and compliance monitor"""
        self.logs_path.mkdir(parents=True, exist_ok=True)
        self.reports_path.mkdir(parents=True, exist_ok=True)
        
        # Define ethical and compliance rules
        self.ethics_rules = {
            'financial_risk_keywords': [
                'fraud', 'embezzlement', 'theft', 'misappropriation', 'kickback',
                'bribe', 'corruption', 'conflict of interest', 'insider trading',
                'market manipulation', 'tax evasion', 'money laundering'
            ],
            'customer_harm_keywords': [
                'discrimination', 'harassment', 'abuse', 'exploitation', 'privacy violation',
                'data breach', 'security vulnerability', 'unsafe product', 'harmful content',
                'misleading information', 'false advertising', 'price gouging'
            ],
            'policy_violation_keywords': [
                'violation', 'breach', 'non-compliance', 'regulatory violation',
                'ethics violation', 'code of conduct', 'policy breach', 'procedure violation',
                'authorization bypass', 'unauthorized access', 'data misuse'
            ]
        }

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

    def scan_content_for_ethics_issues(self, content: str, metadata: dict = None) -> List[Dict]:
        """Scan content for ethics and compliance issues"""
        issues = []
        content_lower = content.lower()
        
        # Check for financial risk keywords
        for keyword in self.ethics_rules['financial_risk_keywords']:
            if keyword.lower() in content_lower:
                issues.append({
                    'type': 'financial_risk',
                    'keyword': keyword,
                    'severity': 'high',
                    'description': f'Potential financial risk identified: {keyword}',
                    'location': 'content'
                })
        
        # Check for customer harm keywords
        for keyword in self.ethics_rules['customer_harm_keywords']:
            if keyword.lower() in content_lower:
                issues.append({
                    'type': 'customer_harm',
                    'keyword': keyword,
                    'severity': 'high',
                    'description': f'Potential customer harm identified: {keyword}',
                    'location': 'content'
                })
        
        # Check for policy violations
        for keyword in self.ethics_rules['policy_violation_keywords']:
            if keyword.lower() in content_lower:
                issues.append({
                    'type': 'policy_violation',
                    'keyword': keyword,
                    'severity': 'medium',
                    'description': f'Potential policy violation identified: {keyword}',
                    'location': 'content'
                })
        
        # Check metadata if provided
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, str):
                    value_lower = value.lower()
                    # Check for financial risks in metadata
                    for keyword in self.ethics_rules['financial_risk_keywords']:
                        if keyword.lower() in value_lower:
                            issues.append({
                                'type': 'financial_risk',
                                'keyword': keyword,
                                'severity': 'high',
                                'description': f'Potential financial risk in metadata ({key}): {keyword}',
                                'location': f'metadata.{key}'
                            })
                    
                    # Check for customer harm in metadata
                    for keyword in self.ethics_rules['customer_harm_keywords']:
                        if keyword.lower() in value_lower:
                            issues.append({
                                'type': 'customer_harm',
                                'keyword': keyword,
                                'severity': 'high',
                                'description': f'Potential customer harm in metadata ({key}): {keyword}',
                                'location': f'metadata.{key}'
                            })
                    
                    # Check for policy violations in metadata
                    for keyword in self.ethics_rules['policy_violation_keywords']:
                        if keyword.lower() in value_lower:
                            issues.append({
                                'type': 'policy_violation',
                                'keyword': keyword,
                                'severity': 'medium',
                                'description': f'Potential policy violation in metadata ({key}): {keyword}',
                                'location': f'metadata.{key}'
                            })
        
        return issues

    def downgrade_autonomy(self, department: str, reason: str):
        """Downgrade autonomy level for a department"""
        dept_memory_path = self.memory_path / f"{department.lower()}_memory.json"
        
        if dept_memory_path.exists():
            try:
                with open(dept_memory_path, 'r') as f:
                    dept_data = json.load(f)
                
                # Get current autonomy level and reduce by 1 (minimum level 1)
                current_level = dept_data.get('autonomy_level', 2)
                new_level = max(1, current_level - 1)
                
                dept_data['autonomy_level'] = new_level
                dept_data['last_autonomy_downgrade'] = {
                    'timestamp': datetime.now().isoformat(),
                    'reason': reason,
                    'previous_level': current_level,
                    'new_level': new_level
                }
                
                with open(dept_memory_path, 'w') as f:
                    json.dump(dept_data, f, indent=2)
                
                print(f"Autonomy downgraded for {department}: {current_level} -> {new_level} due to: {reason}")
                return True
            except Exception as e:
                print(f"Error downgrading autonomy for {department}: {e}")
        
        return False

    def alert_ceo_via_brief(self, issues: List[Dict]):
        """Create a CEO alert brief for detected issues"""
        if not issues:
            return None
        
        # Group issues by type
        grouped_issues = {}
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in grouped_issues:
                grouped_issues[issue_type] = []
            grouped_issues[issue_type].append(issue)
        
        brief_content = f"""# CEO Ethics & Compliance Alert

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

The Ethics & Compliance Monitor has detected potential issues that require your immediate attention:

- **Financial Risk Issues**: {len([i for i in issues if i['type'] == 'financial_risk'])}
- **Customer Harm Issues**: {len([i for i in issues if i['type'] == 'customer_harm'])}
- **Policy Violation Issues**: {len([i for i in issues if i['type'] == 'policy_violation'])}
- **Total Issues**: {len(issues)}

## Detailed Issues

"""
        
        for issue_type, issue_list in grouped_issues.items():
            brief_content += f"\n### {issue_type.replace('_', ' ').title()} Issues\n"
            for issue in issue_list:
                brief_content += f"- **Keyword**: {issue['keyword']}\n"
                brief_content += f"  - **Severity**: {issue['severity'].upper()}\n"
                brief_content += f"  - **Description**: {issue['description']}\n"
                brief_content += f"  - **Location**: {issue['location']}\n\n"
        
        brief_content += f"""
## Recommended Actions

Based on these findings, the following actions are recommended:

1. **Immediate Review**: Examine the flagged content for actual violations
2. **Autonomy Adjustment**: Consider reducing autonomy levels for affected departments
3. **Policy Update**: Review and update policies if necessary
4. **Training**: Provide additional ethics training if violations are confirmed

## Next Steps

- Investigate each flagged item
- Determine if actual violations occurred
- Apply appropriate remediation measures
- Update monitoring rules if needed

---
*Automatically generated by Ethics & Compliance Monitor*
"""

        # Save the CEO brief
        brief_file = self.reports_path / f"CEO_Ethics_Alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(brief_file, 'w', encoding='utf-8') as f:
            f.write(brief_content)
        
        print(f"CEO ethics alert brief created: {brief_file}")
        return brief_file

    def scan_task_file(self, task_file_path: Path) -> List[Dict]:
        """Scan a single task file for ethics issues"""
        try:
            with open(task_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            yaml_data, content_without_frontmatter = self.parse_yaml_frontmatter(content)
            
            # Scan both the content and metadata
            issues = self.scan_content_for_ethics_issues(content_without_frontmatter, yaml_data)
            
            # Add file information to issues
            for issue in issues:
                issue['file_path'] = str(task_file_path)
                issue['scan_timestamp'] = datetime.now().isoformat()
            
            return issues
        except Exception as e:
            print(f"Error scanning task file {task_file_path}: {e}")
            return []

    def scan_decision_logs(self) -> List[Dict]:
        """Scan decision logs for ethics issues"""
        issues = []
        
        # Look for decision logs in the logs directory
        for log_file in self.logs_path.glob("*decision*.json"):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                
                for log_entry in logs:
                    # Convert log entry to string for scanning
                    log_str = json.dumps(log_entry, indent=2)
                    entry_issues = self.scan_content_for_ethics_issues(log_str)
                    
                    # Add log file information to issues
                    for issue in entry_issues:
                        issue['log_file'] = str(log_file)
                        issue['scan_timestamp'] = datetime.now().isoformat()
                        issues.append(issue)
            except Exception as e:
                print(f"Error scanning decision log {log_file}: {e}")
        
        return issues

    def run_ethics_compliance_scan(self) -> Dict:
        """Run a comprehensive ethics and compliance scan"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running ethics and compliance scan")
        
        all_issues = []
        
        # Scan all task files in various directories
        task_dirs = [
            Path(VAULT_PATH) / "01_Incoming_Tasks",
            Path(VAULT_PATH) / "02_In_Progress_Tasks", 
            Path(VAULT_PATH) / "03_Completed_Tasks",
            Path(VAULT_PATH) / "06_Sales_Tasks" / "Incoming",
            Path(VAULT_PATH) / "07_Ops_Tasks" / "Incoming",
            Path(VAULT_PATH) / "08_Support_Tasks" / "Incoming",
            Path(VAULT_PATH) / "09_Finance_Tasks" / "Incoming"
        ]
        
        for task_dir in task_dirs:
            if task_dir.exists():
                for task_file in task_dir.glob("*.md"):
                    issues = self.scan_task_file(task_file)
                    all_issues.extend(issues)
        
        # Scan decision logs
        decision_issues = self.scan_decision_logs()
        all_issues.extend(decision_issues)
        
        print(f"Found {len(all_issues)} potential ethics/compliance issues")
        
        # Group issues by department if possible
        dept_issues = {}
        for issue in all_issues:
            # Try to determine department from file path
            file_path = issue.get('file_path', '')
            if 'Sales' in file_path or 'sales' in file_path:
                dept = 'Sales'
            elif 'Ops' in file_path or 'ops' in file_path or 'Operations' in file_path:
                dept = 'Operations'
            elif 'Support' in file_path or 'support' in file_path:
                dept = 'Support'
            elif 'Finance' in file_path or 'finance' in file_path:
                dept = 'Finance'
            else:
                dept = 'General'
            
            if dept not in dept_issues:
                dept_issues[dept] = []
            dept_issues[dept].append(issue)
        
        # Downgrade autonomy for departments with high-severity issues
        for dept, issues in dept_issues.items():
            high_severity_issues = [i for i in issues if i.get('severity') == 'high']
            if high_severity_issues:
                reason = f"Detected {len(high_severity_issues)} high-severity issues"
                self.downgrade_autonomy(dept, reason)
        
        # Create CEO alert if serious issues found
        if all_issues:
            ceo_brief = self.alert_ceo_via_brief(all_issues)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ethics and compliance scan completed")
        
        return {
            'total_issues': len(all_issues),
            'issues_by_department': {dept: len(issues) for dept, issues in dept_issues.items()},
            'high_severity_issues': len([i for i in all_issues if i.get('severity') == 'high']),
            'ceo_alert_created': 'ceo_brief' in locals()
        }

def main():
    """Main function to run the ethics and compliance monitor"""
    print("="*60)
    print("ETHICS & COMPLIANCE MONITOR")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    monitor = EthicsComplianceMonitor()
    result = monitor.run_ethics_compliance_scan()
    
    print(f"\nScan Results:")
    print(f"  Total Issues Found: {result['total_issues']}")
    print(f"  High Severity Issues: {result['high_severity_issues']}")
    print(f"  Issues by Department: {result['issues_by_department']}")
    print(f"  CEO Alert Created: {result['ceo_alert_created']}")
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Ethics and compliance scan completed")

if __name__ == "__main__":
    main()