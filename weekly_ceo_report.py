#!/usr/bin/env python3
"""
Weekly CEO Report Generator for Personal AI Employee System

This script reads completed tasks and logs to create a comprehensive
weekly report for executives.
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import yaml
import json
from collections import Counter

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
COMPLETED_TASKS_FOLDER = "03_Completed_Tasks"
LOGS_FOLDER = "Logs"
REPORTS_FOLDER = "Reports"

# Convert to Path objects
completed_tasks_path = Path(VAULT_PATH) / COMPLETED_TASKS_FOLDER
logs_path = Path(VAULT_PATH) / LOGS_FOLDER
reports_path = Path(VAULT_PATH) / REPORTS_FOLDER

def parse_yaml_frontmatter(content: str) -> tuple:
    """
    Parse YAML frontmatter from markdown content

    Args:
        content (str): Full markdown content

    Returns:
        tuple: (yaml_data dict, content_without_frontmatter str)
    """
    if content.startswith("---"):
        # Find the end of YAML frontmatter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_content = parts[1]
            content_without_frontmatter = parts[2].strip()
            try:
                yaml_data = yaml.safe_load(yaml_content)
                return yaml_data, content_without_frontmatter
            except yaml.YAMLError:
                # If YAML parsing fails, return empty dict
                return {}, content
    return {}, content

def get_completed_tasks_this_week():
    """
    Get completed tasks from this week
    
    Returns:
        list: List of completed task dictionaries
    """
    tasks = []
    current_time = datetime.now()
    week_start = current_time - timedelta(days=current_time.weekday())  # Monday
    week_end = week_start + timedelta(days=7)  # Next Monday

    if completed_tasks_path.exists():
        for file_path in completed_tasks_path.iterdir():
            if file_path.is_file() and file_path.suffix == '.md':
                try:
                    # Get file modification time
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    # Check if file was modified this week
                    if week_start <= mod_time <= week_end:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        yaml_data, content_without_frontmatter = parse_yaml_frontmatter(content)
                        
                        task_info = {
                            'name': file_path.name,
                            'metadata': yaml_data,
                            'content_preview': content_without_frontmatter[:200] + "..." if len(content_without_frontmatter) > 200 else content_without_frontmatter,
                            'completed_time': mod_time
                        }
                        tasks.append(task_info)
                except Exception as e:
                    print(f"Error reading task {file_path}: {e}")

    return tasks

def get_retry_logs_this_week():
    """
    Get retry logs from this week
    
    Returns:
        list: List of retry log entries
    """
    logs = []
    current_time = datetime.now()
    week_start = current_time - timedelta(days=current_time.weekday())  # Monday
    week_end = week_start + timedelta(days=7)  # Next Monday

    # Look for log files from this week
    for log_file in logs_path.glob(f"retry_log_*.json"):
        try:
            with open(log_file, 'r') as f:
                file_logs = json.load(f)
                
            for log_entry in file_logs:
                log_time = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00'))
                
                # Check if log entry is from this week
                if week_start <= log_time <= week_end:
                    logs.append(log_entry)
        except Exception as e:
            print(f"Error reading log file {log_file}: {e}")

    return logs

def generate_weekly_report():
    """
    Generate the weekly CEO report
    """
    print("Generating weekly CEO report...")
    
    # Get completed tasks for this week
    completed_tasks = get_completed_tasks_this_week()
    
    # Get retry logs for this week
    retry_logs = get_retry_logs_this_week()
    
    # Calculate statistics
    total_completed = len(completed_tasks)
    total_retries = len(retry_logs)
    
    # Count by task type
    task_types = Counter()
    priorities = Counter()
    
    for task in completed_tasks:
        task_type = task['metadata'].get('type', 'unknown')
        priority = task['metadata'].get('priority', 'normal')
        task_types[task_type] += 1
        priorities[priority] += 1
    
    # Generate report content
    report_content = f"""# Weekly CEO Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- **Total Tasks Completed:** {total_completed}
- **Total Retry Attempts:** {total_retries}
- **Report Period:** {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}

## Task Completion by Type
"""
    
    for task_type, count in task_types.items():
        report_content += f"- {task_type.replace('_', ' ').title()}: {count}\n"
    
    report_content += f"""
## Task Completion by Priority
"""
    for priority, count in priorities.items():
        report_content += f"- {priority.title()}: {count}\n"
    
    report_content += f"""
## Top Completed Tasks
"""
    # Sort tasks by completion time (most recent first)
    sorted_tasks = sorted(completed_tasks, key=lambda x: x['completed_time'], reverse=True)
    
    for i, task in enumerate(sorted_tasks[:10]):  # Show top 10
        task_type = task['metadata'].get('type', 'unknown')
        priority = task['metadata'].get('priority', 'normal')
        report_content += f"- **{task['name']}** ({task_type}, {priority}) - {task['completed_time'].strftime('%m/%d %H:%M')}\n"
    
    if retry_logs:
        report_content += f"""
## Retry Analysis
- **Tasks Requiring Retries:** {len(set(log['task_file'] for log in retry_logs))}
- **Most Retried Tasks:**
"""
        retry_counts = Counter(log['task_file'] for log in retry_logs)
        for task_file, count in retry_counts.most_common(5):
            report_content += f"  - {task_file}: {count} retries\n"
    
    report_content += f"""
## System Health
- **Efficiency:** {len(completed_tasks) / max(1, len(retry_logs)):.2f} tasks completed per retry attempt
- **Average Completion Time:** N/A (requires more detailed timing data)

---
*Generated by Personal AI Employee System*
"""

    # Create reports directory if it doesn't exist
    reports_path.mkdir(parents=True, exist_ok=True)
    
    # Create report filename with current date
    report_filename = f"Weekly_CEO_Report_{datetime.now().strftime('%Y%m%d')}.md"
    report_file_path = reports_path / report_filename
    
    # Write report to file
    with open(report_file_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"Weekly CEO report generated: {report_file_path}")
    return report_file_path

def main():
    """Main function to run the report generator"""
    print("="*60)
    print("Weekly CEO Report Generator")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    report_path = generate_weekly_report()
    
    print(f"\nReport saved to: {report_path}")
    print("Weekly CEO Report generation completed!")

if __name__ == "__main__":
    main()