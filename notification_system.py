#!/usr/bin/env python3
"""
Notification System for Personal AI Employee

This script monitors task folders and sends notifications when new tasks arrive,
especially for high-priority tasks.
"""

import os
import time
from pathlib import Path
from datetime import datetime
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from plyer import notification  # pip install plyer
import platform

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
INCOMING_TASKS_FOLDER = "01_Incoming_Tasks"
NOTIFICATION_LOG_FILE = "Logs/notification_log.json"

# Convert to Path objects
incoming_tasks_path = Path(VAULT_PATH) / INCOMING_TASKS_FOLDER
logs_path = Path(VAULT_PATH) / "Logs"
notification_log_path = Path(VAULT_PATH) / NOTIFICATION_LOG_FILE

class NotificationSystem:
    def __init__(self):
        self.sent_notifications = self.load_notification_log()
        self.setup_logs_directory()
    
    def setup_logs_directory(self):
        """Create logs directory if it doesn't exist"""
        logs_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 [{datetime.now().strftime('%H:%M:%S')}] Created logs directory: {logs_path}")
    
    def load_notification_log(self):
        """Load previously sent notifications to avoid duplicates"""
        if notification_log_path.exists():
            try:
                with open(notification_log_path, 'r') as f:
                    return set(json.load(f))
            except Exception as e:
                print(f"Error loading notification log: {e}")
                return set()
        return set()
    
    def save_notification_log(self):
        """Save sent notifications to prevent duplicates"""
        try:
            with open(notification_log_path, 'w') as f:
                json.dump(list(self.sent_notifications), f)
        except Exception as e:
            print(f"Error saving notification log: {e}")
    
    def get_task_priority(self, file_path):
        """Extract priority from task file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for priority in YAML frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    for line in yaml_content.split('\n'):
                        if 'priority:' in line:
                            return line.split('priority:')[-1].strip()
            
            # Default priority
            return 'normal'
        except Exception as e:
            print(f"Error reading task priority from {file_path}: {e}")
            return 'unknown'
    
    def send_desktop_notification(self, title, message, priority="normal"):
        """Send a desktop notification"""
        try:
            # Determine icon based on priority
            icon = None
            if priority == "high" or priority == "critical":
                # For high priority, we might want to use a different icon
                pass
            
            # Send notification
            notification.notify(
                title=title,
                message=message,
                app_name="Personal AI Employee",
                timeout=10  # Duration in seconds
            )
            print(f"🔔 [{datetime.now().strftime('%H:%M:%S')}] Desktop notification sent: {title}")
        except Exception as e:
            print(f"Error sending desktop notification: {e}")
    
    def send_email_notification(self, subject, body, recipient_email=None):
        """Send an email notification (requires SMTP configuration)"""
        # This is a simplified version - in practice, you'd need proper SMTP setup
        print(f"📧 [{datetime.now().strftime('%H:%M:%S')}] Email notification ready: {subject}")
        print("   Note: Email notifications require SMTP configuration")
    
    def check_new_tasks(self):
        """Check for new tasks and send notifications"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking for new tasks...")
        
        # Get all task files in the incoming tasks folder
        task_files = list(incoming_tasks_path.glob('*.md'))
        
        new_tasks = []
        for task_file in task_files:
            # Check if we've already notified about this task
            if str(task_file) not in self.sent_notifications:
                new_tasks.append(task_file)
        
        if not new_tasks:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No new tasks found")
            return
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(new_tasks)} new task(s)")
        
        for task_file in new_tasks:
            # Get task priority
            priority = self.get_task_priority(task_file)
            
            # Create notification message
            task_name = task_file.stem
            message = f"New task in {INCOMING_TASKS_FOLDER}: {task_file.name}"
            
            # Title varies based on priority
            if priority in ["high", "critical"]:
                title = f"🚨 HIGH PRIORITY TASK: {task_name}"
            elif priority == "low":
                title = f"📋 Low Priority Task: {task_name}"
            else:
                title = f"🆕 New Task: {task_name}"
            
            # Send desktop notification
            self.send_desktop_notification(title, message, priority)
            
            # For high priority tasks, also consider sending email
            if priority in ["high", "critical"]:
                email_subject = f"🚨 High Priority Task Alert: {task_name}"
                email_body = f"A high priority task has been added to your queue:\n\n{message}\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self.send_email_notification(email_subject, email_body)
            
            # Add to sent notifications to prevent duplicate alerts
            self.sent_notifications.add(str(task_file))
    
    def run_monitoring(self, check_interval=30):
        """
        Run continuous monitoring for new tasks
        
        Args:
            check_interval (int): Seconds between checks
        """
        print("="*60)
        print("Notification System - Personal AI Employee")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Monitoring: {incoming_tasks_path}")
        print(f"Check Interval: {check_interval} seconds")
        print("="*60)
        
        try:
            while True:
                self.check_new_tasks()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Sleeping for {check_interval} seconds...")
                time.sleep(check_interval)
        except KeyboardInterrupt:
            print(f"\n🛑 [{datetime.now().strftime('%H:%M:%S')}] Notification system stopped by user")
            self.save_notification_log()
    
    def run_once(self):
        """Run notification check once"""
        self.check_new_tasks()
        self.save_notification_log()

def setup_directories():
    """Create required directories if they don't exist"""
    directories = [incoming_tasks_path, logs_path]

    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            print(f"📁 [{datetime.now().strftime('%H:%M:%S')}] Created directory: {directory}")

def main():
    """Main function to run the notification system"""
    # Setup required directories
    setup_directories()
    
    # Create and run the notification system
    notifier = NotificationSystem()
    
    # For now, run once to check for any existing new tasks
    notifier.run_once()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Notification check completed!")

if __name__ == "__main__":
    main()