#!/usr/bin/env python3
"""
Test Script for Personal AI Employee System

This script demonstrates the complete workflow by creating sample files
and showing how they move through the system.
"""

import os
import time
from pathlib import Path
from datetime import datetime
import shutil

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
INBOX_FOLDER = "Inbox"
INCOMING_TASKS_FOLDER = "01_Incoming_Tasks"
IN_PROGRESS_TASKS_FOLDER = "02_In_Progress_Tasks"
COMPLETED_TASKS_FOLDER = "03_Completed_Tasks"

# Convert to Path objects
inbox_path = Path(VAULT_PATH) / INBOX_FOLDER
incoming_tasks_path = Path(VAULT_PATH) / INCOMING_TASKS_FOLDER
in_progress_tasks_path = Path(VAULT_PATH) / IN_PROGRESS_TASKS_FOLDER
completed_tasks_path = Path(VAULT_PATH) / COMPLETED_TASKS_FOLDER

def create_sample_files():
    """Create sample files in the Inbox to trigger the workflow"""
    print("[INFO] Creating sample files in Inbox...")
    
    # Create sample text file
    sample_txt = inbox_path / f"sample_task_{datetime.now().strftime('%H%M%S')}.txt"
    with open(sample_txt, 'w') as f:
        f.write(f"""Sample Task Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a sample task file to test the Personal AI Employee system.

Task Description:
- Process this document
- Extract relevant information
- Create summary report
- Archive when complete

Priority: High
Deadline: 2026-01-30
""")
    
    print(f"   Created: {sample_txt.name}")
    
    # Create sample document file
    sample_doc = inbox_path / f"important_document_{datetime.now().strftime('%H%M%S')}.txt"
    with open(sample_doc, 'w') as f:
        f.write(f"""Important Document: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This document requires immediate attention.

Contents:
1. Review quarterly reports
2. Update budget projections
3. Schedule team meeting
4. Respond to client inquiry

Urgency: Critical
Department: Management
""")
    
    print(f"   Created: {sample_doc.name}")
    
    # Create sample note file
    sample_note = inbox_path / f"meeting_notes_{datetime.now().strftime('%H%M%S')}.txt"
    with open(sample_note, 'w') as f:
        f.write(f"""Meeting Notes: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Team meeting held on {datetime.now().strftime('%Y-%m-%d')}.

Attendees:
- John Smith
- Jane Doe
- Bob Johnson

Action Items:
- [ ] Follow up on project status
- [ ] Prepare presentation materials
- [ ] Schedule next meeting
- [ ] Send meeting minutes

Next Meeting: 2026-02-01
""")
    
    print(f"   Created: {sample_note.name}")
    
    print(f"[SUCCESS] Created {3} sample files in Inbox")
    return [sample_txt, sample_doc, sample_note]

def simulate_task_processing():
    """Simulate moving tasks through the system"""
    print("\n[PROCESS] Simulating task processing...")
    
    # Wait a moment for the file watcher to process the files
    print("   Waiting for file watcher to process files (simulated)...")
    time.sleep(3)
    
    # Show incoming tasks
    incoming_files = list(incoming_tasks_path.glob('*.md'))
    print(f"   Found {len(incoming_files)} task files in Incoming Tasks folder")
    
    if incoming_files:
        print("   Sample task files created:")
        for file in incoming_files[:3]:  # Show first 3
            print(f"     - {file.name}")
    
    # Simulate moving a task to in-progress
    if incoming_files:
        print("\n   Moving first task to In Progress...")
        task_to_move = incoming_files[0]
        
        # Update the task status in the file
        with open(task_to_move, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace the status in YAML frontmatter
        lines = content.split('\n')
        updated_lines = []
        in_yaml = False
        
        for line in lines:
            if line.strip() == '---' and not in_yaml:
                in_yaml = True
                updated_lines.append(line)
            elif line.strip() == '---' and in_yaml:
                in_yaml = False
                updated_lines.append(line)
            elif in_yaml and line.startswith('status:'):
                updated_lines.append('status: in_progress')
            else:
                updated_lines.append(line)
        
        # Write updated content back to file
        with open(task_to_move, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))
        
        print(f"   Updated status of {task_to_move.name} to 'in_progress'")
        
        # Move the file to in-progress folder
        in_progress_path = in_progress_tasks_path / task_to_move.name
        shutil.move(task_to_move, in_progress_path)
        print(f"   Moved {task_to_move.name} to In Progress folder")
    
    # Simulate completing a task
    in_progress_files = list(in_progress_tasks_path.glob('*.md'))
    if in_progress_files:
        print("\n   Completing a task...")
        task_to_complete = in_progress_files[0]
        
        # Update the task status in the file
        with open(task_to_complete, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace the status in YAML frontmatter
        lines = content.split('\n')
        updated_lines = []
        in_yaml = False
        
        for line in lines:
            if line.strip() == '---' and not in_yaml:
                in_yaml = True
                updated_lines.append(line)
            elif line.strip() == '---' and in_yaml:
                in_yaml = False
                updated_lines.append(line)
            elif in_yaml and line.startswith('status:'):
                updated_lines.append('status: completed')
            elif in_yaml and line.startswith('completed_date:'):
                # Update or add completed date
                updated_lines.append(f'completed_date: {datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}')
            else:
                if in_yaml and line.startswith('priority:'):
                    updated_lines.append(line)
                    # Add completed date after priority
                    updated_lines.append(f'completed_date: {datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}')
                else:
                    updated_lines.append(line)
        
        # Write updated content back to file
        with open(task_to_complete, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))
        
        print(f"   Updated status of {task_to_complete.name} to 'completed'")
        
        # Move the file to completed folder
        completed_path = completed_tasks_path / task_to_complete.name
        shutil.move(task_to_complete, completed_path)
        print(f"   Moved {task_to_complete.name} to Completed folder")

def show_system_status():
    """Show the current status of all folders"""
    print("\n[STATUS] Current System Status:")
    print("-" * 50)
    
    incoming_count = len(list(incoming_tasks_path.glob('*.md')))
    in_progress_count = len(list(in_progress_tasks_path.glob('*.md')))
    completed_count = len(list(completed_tasks_path.glob('*.md')))
    
    print(f"Incoming Tasks:   {incoming_count:>3} files")
    print(f"In Progress:      {in_progress_count:>3} files")
    print(f"Completed:        {completed_count:>3} files")
    
    # Show some examples
    if incoming_count > 0:
        print("\nSample Incoming Tasks:")
        for file in list(incoming_tasks_path.glob('*.md'))[:2]:
            print(f"  - {file.name}")
    
    if in_progress_count > 0:
        print("\nSample In Progress Tasks:")
        for file in list(in_progress_tasks_path.glob('*.md'))[:2]:
            print(f"  - {file.name}")
    
    if completed_count > 0:
        print("\nSample Completed Tasks:")
        for file in list(completed_tasks_path.glob('*.md'))[:2]:
            print(f"  - {file.name}")

def main():
    """Main function to run the test"""
    print("="*60)
    print("Testing Personal AI Employee System Workflow")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Create required directories
    inbox_path.mkdir(parents=True, exist_ok=True)
    incoming_tasks_path.mkdir(parents=True, exist_ok=True)
    in_progress_tasks_path.mkdir(parents=True, exist_ok=True)
    completed_tasks_path.mkdir(parents=True, exist_ok=True)
    
    # Create sample files in Inbox
    sample_files = create_sample_files()
    
    # Simulate the workflow
    simulate_task_processing()
    
    # Show final status
    show_system_status()
    
    print("\n[SUCCESS] Test completed successfully!")
    print("\n[SUMMARY] Summary:")
    print("   1. Created sample files in Inbox folder")
    print("   2. Simulated file watcher creating task files")
    print("   3. Moved a task to In Progress status")
    print("   4. Completed a task and moved to Completed folder")
    print("   5. Verified system status")
    
    print(f"\n[TIMESTAMP] Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()