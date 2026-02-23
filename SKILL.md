---
name: task-executor
description: Use this skill when the user wants to create, process, or manage tasks in the Personal AI Employee system. Trigger phrases include "create a task", "add to inbox", "process this file", "log email task", "create approval request", "execute task", "submit for approval", "post to LinkedIn", "handle WhatsApp message", or any task lifecycle management action.
version: 2.0.0
---

# Task Executor Skill

This skill manages the complete task lifecycle for the Personal AI Employee system — from creation through routing, approval, and completion — using the folder-based workflow pipeline.

## Objective

Create structured task files with YAML frontmatter, route them through the 5-stage workflow pipeline, generate Plan.md files for complex tasks, log all decisions to the Decision Ledger, and update the Dashboard.

## Procedure

### 1. Identify Task Parameters

Extract from the user's request:
- **task_type**: `file_arrival` | `email` | `approval_required` | `linkedin` | `whatsapp` | `manual`
- **priority**: `critical` | `high` | `medium` | `low`
- **approval_required**: true if any of these apply:
  - Financial transaction > $100
  - New external contact
  - Legal/contract action
  - Bulk send (email or social media)
  - Irreversible deletion or action
- **metadata**: filename, sender, subject, amount, deadline, etc.

### 2. Create the Task

Run the Task Executor CLI:

```bash
python run_task_skill.py create -t <task_type> -d "<description>" -p <priority>
# With approval flag:
python run_task_skill.py create -t approval_required -d "<description>" -p critical --approval
# With extra metadata:
python run_task_skill.py create -t email -d "<description>" -p high -m sender=client@example.com subject="Invoice"
```

The task is automatically:
- Assigned a unique `task_id`
- Scored for business goal alignment (0–1)
- Risk-assessed (low / medium / high)
- Written to `01_Incoming_Tasks/` or `04_Approval_Workflows/`
- Logged to `Decision_Ledger/`

### 3. Generate a Plan for Complex Tasks

For multi-step tasks (3+ steps), generate a `Plan.md`:

```bash
python plan_generator.py --task-id <task_id> --title "<plan title>" --steps "step1|step2|step3"
```

Plans are saved to `Plans/PLAN_<task_id>.md` with checkboxes and progress tracking.

### 4. Route the Task

| Condition | Destination |
|-----------|-------------|
| `approval_required: false` | `01_Incoming_Tasks/` → Ralph Loop processes |
| `approval_required: true` | `04_Approval_Workflows/` → awaits human |
| `approved: true` set by human | `02_In_Progress_Tasks/` → continues |
| After max 10 retries | `05_Failed_Tasks/` → manual intervention |

### 5. Handle Approval Workflow

When a task needs approval, the system creates a file in `04_Approval_Workflows/`. To approve:

```bash
# Option A: Move the file to Approved/ folder
# Option B: Use approve.py script
python approve.py <task_filename>
# Option C: Edit the task file and set approved: true in YAML frontmatter
```

### 6. Update Dashboard

After task creation or status change:

```bash
python dashboard_updater.py
```

## Task File Format

Every task is a Markdown file with this YAML frontmatter:

```yaml
---
task_id: task_20260223_143022_a1b2c3
type: email
priority: high
status: pending_review
approval: false
goal_alignment_score: 0.72
business_value: 1.0
risk_level: medium
risk_factors:
  - high_priority
created: 2026-02-23T14:30:22
---

## Task: Email
[Task content here]
```

## Workflow State Machine

```
01_Incoming_Tasks/
    ↓ Ralph Loop (auto, every 30s)
    ├→ 02_In_Progress_Tasks/
    │       ↓ (success)
    │   03_Completed_Tasks/
    ↓
    04_Approval_Workflows/
        ↓ (human sets approved: true)
    02_In_Progress_Tasks/
    ↓ (max 10 retries exceeded)
05_Failed_Tasks/
```

## Common Usage Examples

```bash
# File dropped in Inbox
python run_task_skill.py create -t file_arrival -d "Process Q4 report PDF" -p high

# Important email
python run_task_skill.py create -t email -d "Client asking for invoice Jan 2026" -p high -m sender="client@co.com"

# Payment approval needed
python run_task_skill.py create -t approval_required -d "Pay vendor $500 invoice #1234" -p critical --approval -m amount=500 recipient="Vendor Co"

# LinkedIn post
python run_task_skill.py create -t linkedin -d "Post about Q1 milestone achievement" -p medium

# WhatsApp action
python run_task_skill.py create -t whatsapp -d "Reply to client about project deadline" -p high --approval
```

## Output Artifacts

| Artifact | Location | Description |
|----------|----------|-------------|
| Task file | `01_Incoming_Tasks/` or `04_Approval_Workflows/` | Main task document |
| Plan file | `Plans/PLAN_<task_id>.md` | Step-by-step execution plan |
| Decision log | `Decision_Ledger/decision_ledger_YYYYMMDD.md` | Immutable audit entry |
| Dashboard | `Dashboard.md` | Updated system status |
