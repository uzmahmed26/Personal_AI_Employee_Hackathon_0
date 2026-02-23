---
name: ralph-loop
description: Use this skill to start an autonomous processing loop, process all pending tasks autonomously, run the Ralph Wiggum loop, or keep working until all tasks are done. Trigger phrases: "process all tasks", "start autonomous loop", "work until done", "Ralph loop", "run autonomously", "process everything in inbox", "clear the queue".
version: 1.0.0
---

# Ralph Loop Skill

Starts the Ralph Wiggum autonomous loop — Claude keeps working on all pending tasks until every task in 01_Incoming_Tasks/ and Needs_Action/ is either completed, moved to approval, or failed. Uses the Stop hook in `.claude/settings.json` to prevent early exit.

## Objective

Process ALL pending tasks end-to-end without stopping, using the full skill set:
- Task Executor for task creation and routing
- Email Handler for email tasks
- WhatsApp Handler for WhatsApp tasks
- LinkedIn Poster for social media tasks
- Odoo Accounting for financial tasks
- Plan Generator for complex multi-step tasks
- Dashboard Updater to keep metrics current

## Procedure

### 1. Start the Ralph Session

```bash
python ralph_wiggum_hook.py --start \
  --prompt "Process all pending tasks in 01_Incoming_Tasks/ and Needs_Action/" \
  --task-id ""
```

### 2. Inventory All Pending Work

```bash
ls 01_Incoming_Tasks/
ls Needs_Action/
ls 04_Approval_Workflows/
python dashboard_updater.py
```

### 3. Process Each Task by Type

For each task file found, determine its type from YAML frontmatter and invoke the appropriate skill:

| task_type | Skill to Use |
|-----------|-------------|
| `email` | Email Handler Skill |
| `whatsapp` | WhatsApp Handler Skill |
| `linkedin` | LinkedIn Poster Skill |
| `file_arrival` | Task Executor (route and plan) |
| `approval_required` | Create approval file, notify |
| `manual` | Plan and execute step by step |

### 4. After Each Task

- Move to 02_In_Progress_Tasks/ or 03_Completed_Tasks/
- Log decision to Decision_Ledger/
- Update Dashboard

### 5. Signal Completion

When ALL tasks are processed:
```bash
python dashboard_updater.py
```

Output: `<task_complete>RALPH_DONE</task_complete>`

The Ralph Wiggum Stop hook detects this and allows Claude to exit cleanly.

### 6. If Stuck or Max Iterations Reached

```bash
python ralph_wiggum_hook.py --stop
python ralph_wiggum_hook.py --status
```

Review `05_Failed_Tasks/` for items needing manual attention.

## Max Iterations

The loop runs for a maximum of **10 iterations** before stopping automatically, preventing infinite loops. Each iteration = one Claude response cycle.

## Check Status

```bash
python ralph_wiggum_hook.py --status
```

Returns:
```json
{
  "active": true,
  "iteration": 3,
  "task_id": "",
  "started_at": "2026-02-23T..."
}
```
