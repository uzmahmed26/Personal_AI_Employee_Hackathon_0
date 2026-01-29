#!/usr/bin/env python3
"""
Kill Switch and Safe Mode for Company-Scale AI Organization

This module implements the global SAFE_MODE functionality.
"""

import os
import time
from pathlib import Path
from datetime import datetime
import json
import yaml

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
MEMORY_FOLDER = "Memory"
LOGS_FOLDER = "Logs"
GOVERNANCE_FOLDER = "Governance"

class KillSwitchSafeMode:
    def __init__(self):
        self.memory_path = Path(VAULT_PATH) / MEMORY_FOLDER
        self.logs_path = Path(VAULT_PATH) / LOGS_FOLDER
        self.governance_path = Path(VAULT_PATH) / GOVERNANCE_FOLDER
        self.safe_mode_file = self.memory_path / "safe_mode_config.json"
        self.setup_safe_mode()

    def setup_safe_mode(self):
        """Setup safe mode configuration"""
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize safe mode config if it doesn't exist
        if not self.safe_mode_file.exists():
            config = {
                'safe_mode_enabled': False,
                'activation_reason': 'Initial setup',
                'activated_by': 'system',
                'activation_timestamp': datetime.now().isoformat(),
                'last_status_check': datetime.now().isoformat()
            }
            with open(self.safe_mode_file, 'w') as f:
                json.dump(config, f, indent=2)

    def is_safe_mode_enabled(self) -> bool:
        """Check if safe mode is currently enabled"""
        if self.safe_mode_file.exists():
            try:
                with open(self.safe_mode_file, 'r') as f:
                    config = json.load(f)
                    return config.get('safe_mode_enabled', False)
            except Exception as e:
                print(f"Error reading safe mode config: {e}")
                return False
        return False

    def enable_safe_mode(self, reason: str, activated_by: str = "human_operator"):
        """Enable safe mode"""
        config = {
            'safe_mode_enabled': True,
            'activation_reason': reason,
            'activated_by': activated_by,
            'activation_timestamp': datetime.now().isoformat(),
            'last_status_check': datetime.now().isoformat()
        }
        
        with open(self.safe_mode_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Log the activation
        self.log_safe_mode_activation(reason, activated_by)
        
        print(f"SAFE MODE ACTIVATED: {reason}")

    def disable_safe_mode(self, deactivated_by: str = "human_operator"):
        """Disable safe mode"""
        if self.safe_mode_file.exists():
            try:
                with open(self.safe_mode_file, 'r') as f:
                    config = json.load(f)
                
                config['safe_mode_enabled'] = False
                config['deactivation_timestamp'] = datetime.now().isoformat()
                config['deactivated_by'] = deactivated_by
                
                with open(self.safe_mode_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print("SAFE MODE DISABLED")
                return True
            except Exception as e:
                print(f"Error disabling safe mode: {e}")
                return False
        
        return False

    def log_safe_mode_activation(self, reason: str, activated_by: str):
        """Log safe mode activation to governance log"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'safe_mode_activation',
            'reason': reason,
            'activated_by': activated_by,
            'system_state': 'frozen_execution'
        }
        
        # Create governance log file
        log_file = self.logs_path / f"governance_log_{datetime.now().strftime('%Y%m')}.json"
        
        # Load existing logs if file exists
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        # Append new log entry
        logs.append(log_entry)
        
        # Write logs back to file
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def freeze_execution(self):
        """Freeze all AI execution while allowing read-only analysis"""
        if self.is_safe_mode_enabled():
            print("Execution frozen - system in safe mode")
            # In a real implementation, this would stop all active processes
            # For this implementation, we just return True to indicate frozen state
            return True
        return False

    def allow_read_only_analysis(self):
        """Allow read-only analysis in safe mode"""
        # This would allow reading logs, reports, and other data
        # but not modifying anything
        print("Read-only analysis permitted in safe mode")
        return True

    def require_human_approval_to_resume(self):
        """Require human approval to resume normal operations"""
        if not self.is_safe_mode_enabled():
            print("System not in safe mode - normal operations resumed")
            return True
        
        print("Human approval required to resume operations from safe mode")
        return False

    def get_safe_mode_status(self) -> dict:
        """Get current safe mode status"""
        if self.safe_mode_file.exists():
            try:
                with open(self.safe_mode_file, 'r') as f:
                    config = json.load(f)
                    return config
            except Exception as e:
                print(f"Error reading safe mode status: {e}")
                return {'safe_mode_enabled': False, 'error': str(e)}
        
        return {'safe_mode_enabled': False, 'not_configured': True}

    def run_safe_mode_check(self):
        """Run a check of safe mode status"""
        status = self.get_safe_mode_status()
        
        if status.get('safe_mode_enabled', False):
            print(f"⚠️  SAFE MODE ACTIVE")
            print(f"   Reason: {status.get('activation_reason', 'Unknown')}")
            print(f"   Activated by: {status.get('activated_by', 'Unknown')}")
            print(f"   Since: {status.get('activation_timestamp', 'Unknown')}")
            return True
        else:
            print("✅ SAFE MODE INACTIVE - Normal operations")
            return False

def main():
    """Main function to demonstrate kill switch and safe mode"""
    print("="*60)
    print("KILL SWITCH AND SAFE MODE CONTROLLER")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    controller = KillSwitchSafeMode()
    
    # Check current status
    controller.run_safe_mode_check()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Kill switch and safe mode controller initialized")

if __name__ == "__main__":
    main()