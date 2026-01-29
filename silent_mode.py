#!/usr/bin/env python3
"""
Silent Mode for Personal AI Employee System

This module implements silent mode that reduces logging when the system
is stable for 7 consecutive days.
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
LOGS_FOLDER = "Logs"
MEMORY_FOLDER = "Memory"

# Convert to Path objects
logs_path = Path(VAULT_PATH) / LOGS_FOLDER
memory_path = Path(VAULT_PATH) / MEMORY_FOLDER

class SilentMode:
    def __init__(self):
        self.setup_logs_directory()
        self.setup_memory_directory()
        self.silent_mode_active = False
        self.stability_check_days = 7
        self.log_level = logging.INFO
        self.load_silent_mode_state()

    def setup_logs_directory(self):
        """Create logs directory if it doesn't exist"""
        logs_path.mkdir(parents=True, exist_ok=True)

    def setup_memory_directory(self):
        """Create memory directory if it doesn't exist"""
        memory_path.mkdir(parents=True, exist_ok=True)

    def load_silent_mode_state(self):
        """Load silent mode state from memory"""
        state_file = memory_path / "silent_mode_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    self.silent_mode_active = state.get('active', False)
                    self.last_stability_check = datetime.fromisoformat(state.get('last_check', datetime.now().isoformat()))
            except:
                self.silent_mode_active = False
                self.last_stability_check = datetime.now()
        else:
            self.silent_mode_active = False
            self.last_stability_check = datetime.now()

    def save_silent_mode_state(self):
        """Save silent mode state to memory"""
        state_file = memory_path / "silent_mode_state.json"
        state = {
            'active': self.silent_mode_active,
            'last_check': self.last_stability_check.isoformat()
        }
        with open(state_file, 'w') as f:
            json.dump(state, f)

    def check_system_stability(self):
        """Check if the system has been stable for the required number of days"""
        # Look for error or warning logs in the past N days
        stability_period = datetime.now() - timedelta(days=self.stability_check_days)
        
        for log_file in logs_path.glob("*.log"):
            try:
                # Check if this is a recent log file
                file_date_str = log_file.name.split('.')[0]  # Remove extension
                # Try to parse date from filename if it follows date format
                if '_' in file_date_str:
                    date_part = file_date_str.split('_')[-1]  # Take the last part
                    try:
                        file_date = datetime.strptime(date_part, '%Y%m%d')
                        if file_date < stability_period:
                            continue  # Skip old log files
                    except ValueError:
                        # If we can't parse the date, just check the file modification time
                        mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if mod_time < stability_period:
                            continue  # Skip old log files
                else:
                    # If no date in filename, check modification time
                    mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if mod_time < stability_period:
                        continue  # Skip old log files
                
                # Read the log file to check for errors/warnings
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Look for error/warning indicators
                    error_indicators = ['ERROR', 'CRITICAL', 'WARNING', 'exception', 'traceback', 'failed']
                    for indicator in error_indicators:
                        if indicator.lower() in content.lower():
                            # Found an error/warning, system is not stable
                            return False
            except Exception as e:
                print(f"Error checking log file {log_file}: {e}")
                return False  # If we can't read the log, assume instability
        
        # Also check retry logs for excessive retries
        for retry_log in logs_path.glob("retry_log_*.json"):
            try:
                mod_time = datetime.fromtimestamp(retry_log.stat().st_mtime)
                if mod_time < stability_period:
                    continue  # Skip old retry logs
                
                with open(retry_log, 'r') as f:
                    retry_data = json.load(f)
                
                # If there are many retry attempts, system might not be stable
                if len(retry_data) > 50:  # Arbitrary threshold
                    return False
            except Exception as e:
                print(f"Error checking retry log {retry_log}: {e}")
                return False
        
        # If we got here, no significant errors were found in the stability period
        return True

    def activate_silent_mode(self):
        """Activate silent mode to reduce logging"""
        if not self.silent_mode_active:
            self.silent_mode_active = True
            self.log_level = logging.WARNING  # Only log warnings and errors
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Silent mode activated - reducing log verbosity")
            
            # Update logging configuration if possible
            for handler in logging.root.handlers[:]:
                handler.setLevel(logging.WARNING)

    def deactivate_silent_mode(self):
        """Deactivate silent mode to resume normal logging"""
        if self.silent_mode_active:
            self.silent_mode_active = False
            self.log_level = logging.INFO  # Resume normal logging
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Silent mode deactivated - restoring normal log verbosity")
            
            # Update logging configuration if possible
            for handler in logging.root.handlers[:]:
                handler.setLevel(logging.INFO)

    def should_log(self, message_level):
        """Determine if a message should be logged based on current mode"""
        if self.silent_mode_active:
            # In silent mode, only log warnings and errors
            return message_level >= logging.WARNING
        else:
            # In normal mode, log everything
            return True

    def run_silent_mode_check(self):
        """Run a check to determine if silent mode should be activated or deactivated"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running silent mode check")
        
        is_stable = self.check_system_stability()
        
        if is_stable and not self.silent_mode_active:
            # System has been stable, activate silent mode
            self.activate_silent_mode()
        elif not is_stable and self.silent_mode_active:
            # System is unstable, deactivate silent mode
            self.deactivate_silent_mode()
        
        # Update the last check time
        self.last_stability_check = datetime.now()
        self.save_silent_mode_state()
        
        status = "ACTIVE" if self.silent_mode_active else "INACTIVE"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Silent mode is {status}")
        
        return self.silent_mode_active

    def log_if_appropriate(self, level, message):
        """Log a message only if it should be logged in current mode"""
        if self.should_log(level):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def main():
    """Main function to run the silent mode checker"""
    print("="*60)
    print("SILENT MODE CHECKER")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    silent_mode = SilentMode()
    silent_mode.run_silent_mode_check()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Silent mode check completed")

if __name__ == "__main__":
    main()