#!/usr/bin/env python3
"""
Production Health Monitor for Company-Scale AI Organization

This module generates System_Health.md with production metrics.
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import json
import yaml
from typing import Dict, List, Optional

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
MEMORY_FOLDER = "Memory"
LOGS_FOLDER = "Logs"
REPORTS_FOLDER = "Reports"
GOVERNANCE_FOLDER = "Governance"

# Department names
DEPARTMENTS = ["Sales", "Operations", "Support", "Finance"]

class ProductionHealthMonitor:
    def __init__(self):
        self.memory_path = Path(VAULT_PATH) / MEMORY_FOLDER
        self.logs_path = Path(VAULT_PATH) / LOGS_FOLDER
        self.reports_path = Path(VAULT_PATH) / REPORTS_FOLDER
        self.governance_path = Path(VAULT_PATH) / GOVERNANCE_FOLDER
        self.setup_health_monitor()

    def setup_health_monitor(self):
        """Setup production health monitor"""
        self.reports_path.mkdir(parents=True, exist_ok=True)

    def get_uptime(self) -> str:
        """Get system uptime information"""
        # In a real system, this would track actual process uptime
        # For this implementation, we'll return a mock value
        return "System operational since last restart"

    def count_errors(self) -> int:
        """Count errors from log files"""
        error_count = 0
        
        # Look for error logs in the logs directory
        for log_file in self.logs_path.glob("*.log"):
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Count error occurrences
                error_count += content.lower().count('error')
                error_count += content.lower().count('exception')
                error_count += content.lower().count('traceback')
            except Exception as e:
                print(f"Error reading log file {log_file}: {e}")
        
        return error_count

    def count_retries(self) -> int:
        """Count retry attempts from retry logs"""
        retry_count = 0
        
        # Look for retry logs
        for log_file in self.logs_path.glob("retry_log_*.json"):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                retry_count += len(logs)
            except Exception as e:
                print(f"Error reading retry log {log_file}: {e}")
        
        return retry_count

    def get_trust_scores_per_department(self) -> Dict[str, float]:
        """Get trust scores for each department"""
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

    def detect_slow_degradation(self) -> List[str]:
        """Detect signs of slow degradation over time"""
        degradation_signs = []
        
        # Check for increasing error rates over time
        recent_error_count = self.count_errors()
        if recent_error_count > 10:  # Threshold for concern
            degradation_signs.append(f"High error count detected: {recent_error_count}")
        
        # Check for increasing retry rates
        recent_retry_count = self.count_retries()
        if recent_retry_count > 50:  # Threshold for concern
            degradation_signs.append(f"High retry count detected: {recent_retry_count}")
        
        # Check trust scores for degradation
        trust_scores = self.get_trust_scores_per_department()
        for dept, score in trust_scores.items():
            if score < 0.4:  # Low trust score
                degradation_signs.append(f"Low trust score for {dept}: {score:.2f}")
        
        # Check for stale files (tasks not progressing)
        stale_tasks = self.check_for_stale_tasks()
        if stale_tasks > 5:  # Threshold for concern
            degradation_signs.append(f"High number of stale tasks detected: {stale_tasks}")
        
        return degradation_signs

    def check_for_stale_tasks(self) -> int:
        """Check for tasks that haven't been updated recently"""
        stale_count = 0
        cutoff_date = datetime.now() - timedelta(days=7)  # Tasks older than 7 days
        
        # Check various task directories
        task_dirs = [
            Path(VAULT_PATH) / "01_Incoming_Tasks",
            Path(VAULT_PATH) / "02_In_Progress_Tasks",
            Path(VAULT_PATH) / "06_Sales_Tasks" / "In_Progress",
            Path(VAULT_PATH) / "07_Ops_Tasks" / "In_Progress",
            Path(VAULT_PATH) / "08_Support_Tasks" / "In_Progress",
            Path(VAULT_PATH) / "09_Finance_Tasks" / "In_Progress"
        ]
        
        for task_dir in task_dirs:
            if task_dir.exists():
                for task_file in task_dir.glob("*.md"):
                    try:
                        mod_time = datetime.fromtimestamp(task_file.stat().st_mtime)
                        if mod_time < cutoff_date:
                            stale_count += 1
                    except Exception as e:
                        print(f"Error checking file age {task_file}: {e}")
        
        return stale_count

    def generate_system_health_report(self) -> str:
        """Generate the system health report"""
        uptime = self.get_uptime()
        error_count = self.count_errors()
        retry_count = self.count_retries()
        trust_scores = self.get_trust_scores_per_department()
        degradation_signs = self.detect_slow_degradation()
        
        report = f"""# System Health Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Status

- **Uptime**: {uptime}
- **Current Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Report Generation**: Daily automated report

## Production Metrics

### Errors
- **Total Errors Detected**: {error_count}
- **Status**: {'⚠️ Concerning' if error_count > 10 else '✅ Normal'}

### Retries
- **Total Retry Attempts**: {retry_count}
- **Status**: {'⚠️ Concerning' if retry_count > 50 else '✅ Normal'}

### Department Trust Scores
"""
        
        for dept, score in trust_scores.items():
            status = '⚠️ Low' if score < 0.4 else '✅ Healthy' if score > 0.7 else '🟡 Moderate'
            report += f"- **{dept}**: {score:.2f} ({status})\n"
        
        report += f"""

## Degradation Detection

### Signs of Slow Degradation
"""
        
        if degradation_signs:
            for sign in degradation_signs:
                report += f"- ⚠️ {sign}\n"
        else:
            report += "- ✅ No degradation signs detected\n"
        
        report += f"""

## Department Performance

### Task Processing
"""
        
        for dept in DEPARTMENTS:
            dept_tasks = self.get_department_task_counts(dept)
            report += f"""
#### {dept} Department
- **Incoming Tasks**: {dept_tasks['incoming']}
- **In Progress**: {dept_tasks['in_progress']}
- **Completed**: {dept_tasks['completed']}
- **Failed**: {dept_tasks['failed']}
"""
        
        report += f"""

## Recommendations

"""
        
        if error_count > 10:
            report += "- Investigate recent errors and their root causes\n"
        if retry_count > 50:
            report += "- Review retry logic and identify recurring failures\n"
        for dept, score in trust_scores.items():
            if score < 0.4:
                report += f"- Provide additional support to {dept} department\n"
        if not degradation_signs:
            report += "- Continue current operational approach\n"
        
        report += f"""

## Action Items

"""
        
        action_items = self.generate_action_items(error_count, retry_count, trust_scores, degradation_signs)
        if action_items:
            for item in action_items:
                report += f"- {item}\n"
        else:
            report += "- No immediate action items\n"
        
        report += f"""

## Health Trends

This report is generated daily to monitor the health of the Company-Scale AI Organization.
Regular monitoring helps detect degradation patterns early and maintain optimal performance.

---
*Automatically generated by Production Health Monitor*
"""

        return report

    def get_department_task_counts(self, dept: str) -> Dict[str, int]:
        """Get task counts for a department"""
        counts = {
            'incoming': 0,
            'in_progress': 0,
            'completed': 0,
            'failed': 0
        }
        
        dept_folder = None
        if dept == "Sales":
            dept_folder = Path(VAULT_PATH) / "06_Sales_Tasks"
        elif dept == "Operations":
            dept_folder = Path(VAULT_PATH) / "07_Ops_Tasks"
        elif dept == "Support":
            dept_folder = Path(VAULT_PATH) / "08_Support_Tasks"
        elif dept == "Finance":
            dept_folder = Path(VAULT_PATH) / "09_Finance_Tasks"
        
        if dept_folder and dept_folder.exists():
            counts['incoming'] = len(list((dept_folder / "Incoming").glob("*.md")))
            counts['in_progress'] = len(list((dept_folder / "In_Progress").glob("*.md")))
            counts['completed'] = len(list((dept_folder / "Completed").glob("*.md")))
            counts['failed'] = len(list((dept_folder / "Failed").glob("*.md")))
        
        return counts

    def generate_action_items(self, error_count: int, retry_count: int, trust_scores: Dict[str, float], degradation_signs: List[str]) -> List[str]:
        """Generate action items based on health metrics"""
        action_items = []
        
        if error_count > 10:
            action_items.append("Investigate and resolve error sources")
        if retry_count > 50:
            action_items.append("Review and optimize retry mechanisms")
        
        for dept, score in trust_scores.items():
            if score < 0.4:
                action_items.append(f"Conduct performance review for {dept} department")
            elif score > 0.9:
                action_items.append(f"Consider increasing autonomy level for {dept} department")
        
        for sign in degradation_signs:
            if "stale tasks" in sign:
                action_items.append("Review task processing workflows")
        
        if not action_items:
            action_items.append("Continue monitoring - system appears healthy")
        
        return action_items

    def save_system_health_report(self, report_content: str):
        """Save the system health report to a file"""
        report_file = self.reports_path / f"System_Health_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"System health report saved to: {report_file}")
        return report_file

    def run_health_monitor_cycle(self):
        """Run the production health monitoring cycle"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running production health monitoring cycle")
        
        # Generate system health report
        report_content = self.generate_system_health_report()
        
        # Save the report
        report_file = self.save_system_health_report(report_content)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Production health monitoring cycle completed. Report: {report_file}")
        
        return report_file

def main():
    """Main function to run the production health monitor"""
    print("="*60)
    print("PRODUCTION HEALTH MONITOR")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    monitor = ProductionHealthMonitor()
    monitor.run_health_monitor_cycle()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Production health monitoring completed")

if __name__ == "__main__":
    main()