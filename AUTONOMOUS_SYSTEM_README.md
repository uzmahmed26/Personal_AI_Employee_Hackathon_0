# Autonomous Personal AI Employee System

This is an upgraded version of the Personal AI Employee system that operates fully autonomously with advanced features:

## New Features

### 1. Auto Task Flow
- Tasks automatically flow from `01_Incoming_Tasks` → `02_In_Progress_Tasks` → `03_Completed_Tasks`
- Based on task type and predefined rules (no human editing required)

### 2. Ralph Loop (Retry Mechanism)
- Auto-retry tasks until status = completed
- Max 10 retries per task
- Logs each retry attempt for debugging

### 3. Human Approval Gate
- If task contains `approval: true` in YAML frontmatter
- Task moves to `04_Approval_Workflows` folder
- Waits for approval before continuing workflow
- To approve a task, update the YAML to include `approved: true`

### 4. Weekly CEO Reports
- Reads completed tasks and logs
- Generates markdown reports in `/Reports` folder
- Runs automatically every Sunday

### 5. Crash-Safe Operation
- Auto-restart failed components
- Clear error logging
- Enhanced monitoring

## How to Run

### Option 1: Run the Complete Autonomous System (Recommended)
```bash
python autonomous_system.py
```

### Option 2: Run Individual Components
```bash
# Start the enhanced orchestrator with crash recovery
python enhanced_orchestrator.py

# Or run individual components:
python ralph_loop.py              # The autonomous retry mechanism
python task_processor.py          # Handles task movement between folders
python weekly_ceo_report.py       # Generate reports (run manually or scheduled)
```

## Task YAML Frontmatter Examples

### Standard Task
```markdown
---
type: file_arrival
filename: report.pdf
size: 2.45 MB
created: 2026-01-29T00:30:00
status: pending_review
priority: normal
task_id: task_20260129_003000_123456
---

## New File Detected
...
```

### Task Requiring Approval
```markdown
---
type: email
from: boss@company.com
subject: Budget Approval Required
received: 2026-01-29T00:30:00
priority: high
status: pending_review
email_id: abc123def456
approval: true
---

## Email Received
...
```

### Approved Task (after approval)
```markdown
---
type: email
from: boss@company.com
subject: Budget Approval Required
received: 2026-01-29T00:30:00
priority: high
status: pending_review
email_id: abc123def456
approval: true
approved: true
---

## Email Received
...
```

## Folder Structure
- `Inbox` - Files placed here trigger the system
- `01_Incoming_Tasks` - New tasks created here
- `02_In_Progress_Tasks` - Tasks being processed
- `03_Completed_Tasks` - Finished tasks
- `04_Approval_Workflows` - Tasks awaiting approval
- `Logs` - System logs and retry logs
- `Reports` - Weekly CEO reports

## Local-First Architecture
- All data stored in markdown + YAML format
- No external dependencies required for core functionality
- Works offline
- Easy to backup and sync

## Error Handling
- Comprehensive logging in the `Logs` folder
- Automatic restart of failed components
- Graceful degradation when components fail