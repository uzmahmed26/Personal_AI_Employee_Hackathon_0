#!/usr/bin/env python3
"""
Dashboard for Personal AI Employee System

This script generates a comprehensive dashboard showing the status of all tasks
and system components in the Personal AI Employee system.
"""

import os
import time
from pathlib import Path
from datetime import datetime
import json
from collections import Counter

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
INCOMING_TASKS_FOLDER = "01_Incoming_Tasks"
IN_PROGRESS_TASKS_FOLDER = "02_In_Progress_Tasks"
COMPLETED_TASKS_FOLDER = "03_Completed_Tasks"
APPROVAL_WORKFLOWS_FOLDER = "04_Approval_Workflows"
LOGS_FOLDER = "Logs"

# Convert to Path objects
incoming_tasks_path = Path(VAULT_PATH) / INCOMING_TASKS_FOLDER
in_progress_tasks_path = Path(VAULT_PATH) / IN_PROGRESS_TASKS_FOLDER
completed_tasks_path = Path(VAULT_PATH) / COMPLETED_TASKS_FOLDER
approval_workflows_path = Path(VAULT_PATH) / APPROVAL_WORKFLOWS_FOLDER
logs_path = Path(VAULT_PATH) / LOGS_FOLDER

def count_files_in_directory(directory_path):
    """Count the number of files in a directory"""
    if directory_path.exists():
        return len([f for f in directory_path.iterdir() if f.is_file()])
    return 0

def get_task_details(directory_path):
    """Get detailed information about tasks in a directory"""
    if not directory_path.exists():
        return []
    
    tasks = []
    for file_path in directory_path.iterdir():
        if file_path.is_file() and file_path.suffix == '.md':
            # Read the file to get status and priority
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract status and priority from YAML frontmatter
                status = 'unknown'
                priority = 'normal'
                
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        yaml_content = parts[1]
                        for line in yaml_content.split('\n'):
                            if 'status:' in line:
                                status = line.split('status:')[-1].strip()
                            if 'priority:' in line:
                                priority = line.split('priority:')[-1].strip()
                
                tasks.append({
                    'name': file_path.name,
                    'status': status,
                    'priority': priority,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                })
            except Exception:
                # If there's an error reading the file, add basic info
                tasks.append({
                    'name': file_path.name,
                    'status': 'error_reading',
                    'priority': 'unknown',
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                })
    
    return tasks

def get_system_stats():
    """Get overall system statistics"""
    incoming_count = count_files_in_directory(incoming_tasks_path)
    in_progress_count = count_files_in_directory(in_progress_tasks_path)
    completed_count = count_files_in_directory(completed_tasks_path)
    approval_count = count_files_in_directory(approval_workflows_path)
    
    # Get detailed task information
    incoming_tasks = get_task_details(incoming_tasks_path)
    in_progress_tasks = get_task_details(in_progress_tasks_path)
    completed_tasks = get_task_details(completed_tasks_path)
    
    # Count statuses and priorities
    incoming_statuses = Counter(task['status'] for task in incoming_tasks)
    in_progress_statuses = Counter(task['status'] for task in in_progress_tasks)
    completed_statuses = Counter(task['status'] for task in completed_tasks)
    
    incoming_priorities = Counter(task['priority'] for task in incoming_tasks)
    in_progress_priorities = Counter(task['priority'] for task in in_progress_tasks)
    completed_priorities = Counter(task['priority'] for task in completed_tasks)
    
    return {
        'incoming_count': incoming_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'approval_count': approval_count,
        'incoming_tasks': incoming_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'incoming_statuses': incoming_statuses,
        'in_progress_statuses': in_progress_statuses,
        'completed_statuses': completed_statuses,
        'incoming_priorities': incoming_priorities,
        'in_progress_priorities': in_progress_priorities,
        'completed_priorities': completed_priorities
    }

def print_dashboard(stats):
    """Print the dashboard with system status"""
    print("="*80)
    print("PERSONAL AI EMPLOYEE SYSTEM DASHBOARD")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # System Status Summary
    print("\nSYSTEM STATUS SUMMARY")
    print("-" * 40)
    print(f"Incoming Tasks:     {stats['incoming_count']:>3}")
    print(f"In Progress Tasks:  {stats['in_progress_count']:>3}")
    print(f"Completed Tasks:    {stats['completed_count']:>3}")
    print(f"Approval Queue:     {stats['approval_count']:>3}")

    # Task Breakdown by Status
    print("\nTASK BREAKDOWN BY STATUS")
    print("-" * 40)
    print("Incoming Tasks:")
    for status, count in stats['incoming_statuses'].items():
        print(f"  - {status.capitalize()}: {count}")

    print("In Progress Tasks:")
    for status, count in stats['in_progress_statuses'].items():
        print(f"  - {status.capitalize()}: {count}")

    print("Completed Tasks:")
    for status, count in stats['completed_statuses'].items():
        print(f"  - {status.capitalize()}: {count}")

    # Task Breakdown by Priority
    print("\nTASK BREAKDOWN BY PRIORITY")
    print("-" * 40)
    print("Incoming Tasks:")
    for priority, count in stats['incoming_priorities'].items():
        print(f"  - {priority.capitalize()}: {count}")

    print("In Progress Tasks:")
    for priority, count in stats['in_progress_priorities'].items():
        print(f"  - {priority.capitalize()}: {count}")

    print("Completed Tasks:")
    for priority, count in stats['completed_priorities'].items():
        print(f"  - {priority.capitalize()}: {count}")

    # Recent Tasks
    print("\nRECENT INCOMING TASKS")
    print("-" * 40)
    recent_incoming = sorted(stats['incoming_tasks'], key=lambda x: x['modified'], reverse=True)[:5]
    if recent_incoming:
        for task in recent_incoming:
            print(f"  - {task['name']} | {task['status']} | {task['priority']} | {task['modified'].strftime('%m/%d %H:%M')}")
    else:
        print("  - No recent incoming tasks")

    # In Progress Tasks
    print("\nCURRENTLY IN PROGRESS")
    print("-" * 40)
    if stats['in_progress_tasks']:
        for task in stats['in_progress_tasks']:
            print(f"  - {task['name']} | {task['status']} | {task['priority']}")
    else:
        print("  - No tasks currently in progress")

    # System Health
    print("\nSYSTEM HEALTH")
    print("-" * 40)
    total_tasks = stats['incoming_count'] + stats['in_progress_count'] + stats['completed_count']
    completion_rate = (stats['completed_count'] / max(total_tasks, 1)) * 100 if total_tasks > 0 else 0

    print(f"Total Tasks Processed: {total_tasks}")
    print(f"Completion Rate: {completion_rate:.1f}%")

    if completion_rate >= 80:
        health_status = "Excellent"
    elif completion_rate >= 60:
        health_status = "Good"
    elif completion_rate >= 40:
        health_status = "Fair"
    else:
        health_status = "Needs Attention"

    print(f"System Health: {health_status}")

    print("\nTIPS")
    print("-" * 40)
    if stats['incoming_count'] > 10:
        print("  - Consider processing incoming tasks to reduce backlog")
    if any(task['priority'] in ['high', 'critical'] for task in stats['incoming_tasks']):
        print("  - High priority tasks detected - consider reviewing them soon")
    if stats['in_progress_count'] == 0 and stats['incoming_count'] > 0:
        print("  - You have incoming tasks but nothing in progress - consider starting work")

    print("="*80)

def generate_dashboard_md(stats):
    """Generate a markdown version of the dashboard"""
    md_content = f"""# Personal AI Employee Dashboard

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## System Status Summary

| Category | Count |
|----------|-------|
| 📥 Incoming Tasks | {stats['incoming_count']} |
| 🔄 In Progress Tasks | {stats['in_progress_count']} |
| ✅ Completed Tasks | {stats['completed_count']} |
| 📋 Approval Queue | {stats['approval_count']} |

## Task Breakdown by Status

### Incoming Tasks
"""
    
    for status, count in stats['incoming_statuses'].items():
        md_content += f"- {status.capitalize()}: {count}\n"
    
    md_content += "\n### In Progress Tasks\n"
    for status, count in stats['in_progress_statuses'].items():
        md_content += f"- {status.capitalize()}: {count}\n"
    
    md_content += "\n### Completed Tasks\n"
    for status, count in stats['completed_statuses'].items():
        md_content += f"- {status.capitalize()}: {count}\n"
    
    md_content += "\n## Task Breakdown by Priority\n"
    
    md_content += "\n### Incoming Tasks\n"
    for priority, count in stats['incoming_priorities'].items():
        md_content += f"- {priority.capitalize()}: {count}\n"
    
    md_content += "\n### In Progress Tasks\n"
    for priority, count in stats['in_progress_priorities'].items():
        md_content += f"- {priority.capitalize()}: {count}\n"
    
    md_content += "\n### Completed Tasks\n"
    for priority, count in stats['completed_priorities'].items():
        md_content += f"- {priority.capitalize()}: {count}\n"
    
    md_content += f"""

## System Health

- Total Tasks Processed: {stats['incoming_count'] + stats['in_progress_count'] + stats['completed_count']}
- Completion Rate: {(stats['completed_count'] / max((stats['incoming_count'] + stats['in_progress_count'] + stats['completed_count']), 1)) * 100:.1f}%

## Recent Activity

Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    # Save to dashboard file
    dashboard_file = Path(VAULT_PATH) / "Dashboard_Status.md"
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Dashboard saved to: {dashboard_file}")

def main():
    """Main function to run the dashboard"""
    print("Loading dashboard...")
    
    # Get system statistics
    stats = get_system_stats()
    
    # Print dashboard to console
    print_dashboard(stats)
    
    # Generate markdown version
    generate_dashboard_md(stats)
    
    print(f"\nDashboard generated successfully at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()