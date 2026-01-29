import time
from pathlib import Path
import os

# Simple test to see if the script is working
print("Testing basic functionality...")

# Check if directories exist
inbox_path = Path(".") / "Inbox"
incoming_tasks_path = Path(".") / "01_Incoming_Tasks"
completed_tasks_path = Path(".") / "03_Completed_Tasks"

print(f"Inbox exists: {inbox_path.exists()}")
print(f"Incoming Tasks exists: {incoming_tasks_path.exists()}")
print(f"Completed Tasks exists: {completed_tasks_path.exists()}")

# List files in inbox
if inbox_path.exists():
    inbox_files = list(inbox_path.glob('*'))
    print(f"Files in inbox: {[f.name for f in inbox_files]}")