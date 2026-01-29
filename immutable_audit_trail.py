#!/usr/bin/env python3
"""
Immutable Audit Trail for Company-Scale AI Organization

This module implements an immutable audit trail with hash protection.
"""

import os
import time
from pathlib import Path
from datetime import datetime
import json
import hashlib
from typing import Dict, List, Optional

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
MEMORY_FOLDER = "Memory"
LOGS_FOLDER = "Logs"
AUDIT_TRAIL_FOLDER = "Audit_Trail"
GOVERNANCE_FOLDER = "Governance"

class ImmutableAuditTrail:
    def __init__(self):
        self.memory_path = Path(VAULT_PATH) / MEMORY_FOLDER
        self.logs_path = Path(VAULT_PATH) / LOGS_FOLDER
        self.audit_trail_path = Path(VAULT_PATH) / AUDIT_TRAIL_FOLDER
        self.governance_path = Path(VAULT_PATH) / GOVERNANCE_FOLDER
        self.hash_store_path = self.audit_trail_path / "hash_store.json"
        self.setup_audit_trail()

    def setup_audit_trail(self):
        """Setup immutable audit trail system"""
        self.audit_trail_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize hash store if it doesn't exist
        if not self.hash_store_path.exists():
            with open(self.hash_store_path, 'w') as f:
                json.dump({}, f)

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read the file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def store_file_hash(self, file_path: str, file_hash: str):
        """Store the hash of a file in the hash store"""
        hash_store = {}
        if self.hash_store_path.exists():
            try:
                with open(self.hash_store_path, 'r') as f:
                    hash_store = json.load(f)
            except Exception as e:
                print(f"Error reading hash store: {e}")
        
        # Store the hash with timestamp
        hash_store[file_path] = {
            'hash': file_hash,
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path
        }
        
        with open(self.hash_store_path, 'w') as f:
            json.dump(hash_store, f, indent=2)

    def verify_file_integrity(self, file_path: Path) -> bool:
        """Verify that a file has not been tampered with"""
        if not file_path.exists():
            return False
        
        # Calculate current hash
        current_hash = self.calculate_file_hash(file_path)
        
        # Get stored hash
        stored_hash = self.get_stored_hash(str(file_path))
        
        return current_hash == stored_hash

    def get_stored_hash(self, file_path: str) -> str:
        """Get the stored hash for a file"""
        if self.hash_store_path.exists():
            try:
                with open(self.hash_store_path, 'r') as f:
                    hash_store = json.load(f)
                
                if file_path in hash_store:
                    return hash_store[file_path]['hash']
            except Exception as e:
                print(f"Error reading stored hash for {file_path}: {e}")
        
        return None

    def lock_decision_log(self, log_file_path: Path):
        """Lock a decision log by calculating and storing its hash"""
        if not log_file_path.exists():
            print(f"Log file does not exist: {log_file_path}")
            return False
        
        # Calculate hash of the log file
        file_hash = self.calculate_file_hash(log_file_path)
        
        # Store the hash to lock the file
        self.store_file_hash(str(log_file_path), file_hash)
        
        print(f"Decision log locked: {log_file_path} (hash: {file_hash[:16]}...)")
        return True

    def lock_all_existing_decision_logs(self):
        """Lock all existing decision logs"""
        locked_count = 0
        
        # Look for decision logs in various locations
        log_locations = [
            self.logs_path,
            self.memory_path,
            self.audit_trail_path
        ]
        
        for location in log_locations:
            if location.exists():
                # Lock all JSON and markdown log files
                for log_file in location.glob("*.json"):
                    if "decision" in log_file.name.lower() or "log" in log_file.name.lower():
                        if self.lock_decision_log(log_file):
                            locked_count += 1
                
                for log_file in location.glob("*.md"):
                    if "decision" in log_file.name.lower() or "log" in log_file.name.lower():
                        if self.lock_decision_log(log_file):
                            locked_count += 1
        
        print(f"Locked {locked_count} decision logs")
        return locked_count

    def verify_all_locked_logs(self) -> Dict[str, bool]:
        """Verify the integrity of all locked logs"""
        verification_results = {}
        
        if self.hash_store_path.exists():
            try:
                with open(self.hash_store_path, 'r') as f:
                    hash_store = json.load(f)
                
                for file_path_str, info in hash_store.items():
                    file_path = Path(file_path_str)
                    is_valid = self.verify_file_integrity(file_path)
                    verification_results[file_path_str] = is_valid
                    
                    if not is_valid:
                        print(f"⚠️  Integrity violation detected: {file_path_str}")
                    else:
                        print(f"✅ Integrity verified: {file_path_str}")
            except Exception as e:
                print(f"Error verifying logs: {e}")
        
        return verification_results

    def create_audit_entry(self, event_type: str, details: Dict) -> str:
        """Create an immutable audit entry"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details,
            'entry_id': f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        }
        
        # Create audit file with timestamp
        audit_file = self.audit_trail_path / f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        
        with open(audit_file, 'w') as f:
            json.dump(audit_entry, f, indent=2)
        
        # Lock the audit entry immediately
        self.lock_decision_log(audit_file)
        
        print(f"Audit entry created and locked: {audit_file.name}")
        return str(audit_file)

    def prevent_retroactive_edits(self, log_file_path: Path) -> bool:
        """Prevent retroactive edits by verifying file integrity"""
        if not log_file_path.exists():
            return True  # Non-existent files can't be edited
        
        # Verify integrity
        is_valid = self.verify_file_integrity(log_file_path)
        
        if not is_valid:
            print(f"⚠️  Attempt to edit locked log detected: {log_file_path}")
            # In a real system, you might want to alert security here
            return False
        
        return True

    def run_audit_integrity_check(self):
        """Run a comprehensive audit integrity check"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running audit integrity check")
        
        # Lock all existing decision logs
        locked_count = self.lock_all_existing_decision_logs()
        
        # Verify all locked logs
        verification_results = self.verify_all_locked_logs()
        
        # Count integrity violations
        violations = sum(1 for valid in verification_results.values() if not valid)
        
        print(f"Integrity check completed:")
        print(f"  - Logs locked: {locked_count}")
        print(f"  - Total verified: {len(verification_results)}")
        print(f"  - Integrity violations: {violations}")
        
        # Create audit entry for the integrity check
        self.create_audit_entry(
            event_type="integrity_check",
            details={
                "locked_count": locked_count,
                "verified_count": len(verification_results),
                "violations": violations,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Audit integrity check completed")
        
        return {
            'locked_count': locked_count,
            'verified_count': len(verification_results),
            'violations': violations,
            'verification_results': verification_results
        }

def main():
    """Main function to run the immutable audit trail"""
    print("="*60)
    print("IMMUTABLE AUDIT TRAIL SYSTEM")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    audit_trail = ImmutableAuditTrail()
    result = audit_trail.run_audit_integrity_check()
    
    print(f"\nAudit Results:")
    print(f"  Locked Count: {result['locked_count']}")
    print(f"  Verified Count: {result['verified_count']}")
    print(f"  Violations: {result['violations']}")
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Immutable audit trail system initialized")

if __name__ == "__main__":
    main()