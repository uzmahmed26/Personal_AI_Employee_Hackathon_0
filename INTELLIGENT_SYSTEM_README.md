# Intelligent Personal AI Employee System

This is the upgraded version of the Personal AI Employee system with decision-making intelligence:

## New Intelligent Features

### 1. Task Intelligence Layer
- Reads task history from `03_Completed_Tasks`
- Auto-prioritizes new tasks based on:
  - Urgency
  - Past success patterns
  - Retries count
- Updates YAML with:
  - confidence_score
  - estimated_effort

### 2. Self-Correction Mode
- If same task fails 3 times:
  - Writes failure_analysis.md
  - Adjusts processing strategy automatically
  - Retries with new strategy

### 3. CEO Question Generator
- From weekly reports, generates:
  - CEO_Questions.md
  - Risks, blockers, and decisions needed
- Saved in /Reports

### 4. Learning Memory
- Creates /Memory/ folder
- Stores:
  - What worked
  - What failed
  - Approval patterns
- Uses memory in future task decisions

### 5. Silent Mode
- If system is stable for 7 days:
  - Reduces logs
  - Only log anomalies

## How to Run

### Option 1: Run the Complete Intelligent System (Recommended)
```bash
python intelligent_system.py
```

### Option 2: Run the Intelligent Orchestrator
```bash
python intelligent_orchestrator.py
```

### Option 3: Run Individual Intelligent Components
```bash
python task_intelligence.py          # Task intelligence layer
python self_correction.py            # Self-correction mode
python ceo_question_generator.py     # CEO question generator
python learning_memory.py            # Learning memory system
python silent_mode.py                # Silent mode manager
```

## Intelligent Task YAML Examples

### Standard Task with Intelligence
```markdown
---
type: file_arrival
filename: report.pdf
size: 2.45 MB
created: 2026-01-29T00:30:00
status: pending_review
priority: normal
task_id: task_20260129_003000_123456
confidence_score: 0.85
estimated_effort: medium
retry_count: 0
calculated_urgency: 0.4
---

## New File Detected
...
```

### Task with High Risk Factor
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
confidence_score: 0.3
estimated_effort: high
retry_count: 2
risk_factor: 0.7
requires_manual_review: true
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
- `05_Failed_Tasks` - Tasks that failed repeatedly
- `Logs` - System logs and retry logs
- `Memory` - Learning data and patterns
- `Reports` - Weekly CEO reports and questions

## Decision-Making Intelligence Flow
1. Task arrives in Incoming Tasks
2. Task Intelligence analyzes and prioritizes
3. Ralph Loop processes with learned strategies
4. System learns from successes/failures
5. Memory improves future decisions
6. Self-correction handles persistent failures
7. CEO questions identify strategic issues

## Local-First Architecture
- All data stored in markdown + YAML format
- No external dependencies required for core functionality
- Works offline
- Easy to backup and sync

## Error Handling
- Comprehensive logging in the `Logs` folder
- Automatic restart of failed components
- Intelligent failure analysis and correction
- Graceful degradation when components fail