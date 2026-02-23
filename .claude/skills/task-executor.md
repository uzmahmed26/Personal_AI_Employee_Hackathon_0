---
name: task-executor
description: Use this skill when the user wants to create, process, or manage tasks in the Personal AI Employee system. Trigger phrases: "create a task", "add to inbox", "process this file", "log email task", "create approval request", "execute task", "submit for approval", "handle this request", "process task".
version: 2.0.0
---

# Task Executor Skill

Manages the complete task lifecycle for the Personal AI Employee system — from creation through routing, approval, and completion — using the folder-based workflow pipeline.

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

```bash
python run_task_skill.py create -t <task_type> -d "<description>" -p <priority>

# With approval:
python run_task_skill.py create -t approval_required -d "<desc>" -p critical --approval

# With metadata:
python run_task_skill.py create -t email -d "<desc>" -p high -m sender=client@co.com subject="Invoice"
```

The task is automatically:
- Assigned a unique `task_id`
- Scored for business goal alignment (0–1)
- Risk-assessed (low / medium / high)
- Written to `01_Incoming_Tasks/` or `04_Approval_Workflows/`
- Logged to `Decision_Ledger/`

### 3. Generate a Plan for Complex Tasks

```bash
python plan_generator.py --task-id <task_id> --title "<title>" --steps "step1|step2|step3"

# Auto-generate for all pending tasks:
python plan_generator.py --auto
```

### 4. Route the Task

| Condition | Destination |
|-----------|-------------|
| `approval_required: false` | `01_Incoming_Tasks/` → Ralph Loop processes |
| `approval_required: true` | `04_Approval_Workflows/` → awaits human |
| `approved: true` | `02_In_Progress_Tasks/` → continues |
| After max 10 retries | `05_Failed_Tasks/` → manual intervention |

### 5. Handle Approvals

```bash
python approve.py list
python approve.py approve <filename>
python approve.py reject <filename>
```

### 6. Update Dashboard

```bash
python dashboard_updater.py
```

## Workflow State Machine

```
01_Incoming_Tasks/
    ↓ Ralph Loop (every 30s, max 10 retries)
    ├→ 02_In_Progress_Tasks/ → 03_Completed_Tasks/
    ↓
    04_Approval_Workflows/ → (approved) → 02_In_Progress_Tasks/
    ↓ (10 retries exceeded)
05_Failed_Tasks/
```

## Examples

```bash
# File dropped in Inbox
python run_task_skill.py create -t file_arrival -d "Process Q4 report PDF" -p high

# Important email
python run_task_skill.py create -t email -d "Client asking for invoice" -p high -m sender="client@co.com"

# Payment needing approval
python run_task_skill.py create -t approval_required -d "Pay vendor $500 invoice #1234" -p critical --approval -m amount=500

# LinkedIn post
python run_task_skill.py create -t linkedin -d "Post about Q1 milestone" -p medium

# WhatsApp action
python run_task_skill.py create -t whatsapp -d "Reply to client re: deadline" -p high --approval
```
