#!/usr/bin/env python3
"""
Dashboard Updater — Personal AI Employee System

Dynamically regenerates Dashboard.md with real-time metrics by scanning
the task folders, memory, decision ledger, and plans.

Replaces the static template that was in Dashboard.md.

Usage:
  python dashboard_updater.py                  # One-shot update
  python dashboard_updater.py --watch          # Continuous mode (update every 60s)
  python dashboard_updater.py --watch --interval 30
"""

import argparse
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

try:
    import yaml
except ImportError:
    yaml = None

VAULT_PATH = Path(__file__).parent
DASHBOARD_FILE = VAULT_PATH / "Dashboard.md"


def count_md_files(folder: Path) -> int:
    if folder.exists():
        return len(list(folder.glob("*.md")))
    return 0


def parse_frontmatter(file_path: Path) -> Dict:
    """Parse YAML frontmatter from a markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                if yaml:
                    return yaml.safe_load(parts[1]) or {}
                # Fallback parser
                result = {}
                for line in parts[1].strip().splitlines():
                    if ":" in line:
                        k, _, v = line.partition(":")
                        result[k.strip()] = v.strip().strip('"')
                return result
    except Exception:
        pass
    return {}


def get_task_stats() -> Dict:
    """Collect task counts and details from all workflow folders."""
    folders = {
        "incoming": VAULT_PATH / "01_Incoming_Tasks",
        "in_progress": VAULT_PATH / "02_In_Progress_Tasks",
        "completed": VAULT_PATH / "03_Completed_Tasks",
        "approval": VAULT_PATH / "04_Approval_Workflows",
        "failed": VAULT_PATH / "05_Failed_Tasks",
        "needs_action": VAULT_PATH / "Needs_Action",
        "done": VAULT_PATH / "Done",
    }

    stats = {name: count_md_files(path) for name, path in folders.items()}

    # Get today's completed tasks
    today = datetime.now().date()
    completed_today = 0
    completed_this_week = 0
    recent_completed = []

    completed_dir = folders["completed"]
    if completed_dir.exists():
        for f in completed_dir.glob("*.md"):
            fm = parse_frontmatter(f)
            created_str = fm.get("created", "") or fm.get("last_updated", "")
            try:
                if "T" in str(created_str):
                    created = datetime.fromisoformat(str(created_str)).date()
                else:
                    created = datetime.strptime(str(created_str)[:10], "%Y-%m-%d").date()
                if created == today:
                    completed_today += 1
                if (today - created).days <= 7:
                    completed_this_week += 1
                    recent_completed.append({
                        "file": f.name,
                        "type": fm.get("type", "unknown"),
                        "priority": fm.get("priority", "medium"),
                        "created": str(created_str)[:16],
                    })
            except (ValueError, TypeError):
                pass

    stats["completed_today"] = completed_today
    stats["completed_this_week"] = completed_this_week
    stats["recent_completed"] = sorted(recent_completed, key=lambda x: x["created"], reverse=True)[:5]

    # Get approval items with details
    approval_items = []
    if folders["approval"].exists():
        for f in folders["approval"].glob("*.md"):
            fm = parse_frontmatter(f)
            approval_items.append({
                "file": f.name,
                "type": fm.get("type", "unknown"),
                "priority": fm.get("priority", "medium"),
                "created": fm.get("created", "")[:16] if fm.get("created") else "",
            })
    stats["approval_items"] = sorted(approval_items, key=lambda x: x["priority"])

    return stats


def get_plan_stats() -> Dict:
    """Collect stats from Plans/ folder."""
    plans_dir = VAULT_PATH / "Plans"
    stats = {"total": 0, "in_progress": 0, "completed": 0, "active_plans": []}

    if not plans_dir.exists():
        return stats

    for f in plans_dir.glob("PLAN_*.md"):
        fm = parse_frontmatter(f)
        stats["total"] += 1
        status = fm.get("status", "in_progress")
        if status == "completed":
            stats["completed"] += 1
        else:
            stats["in_progress"] += 1
            total_steps = int(fm.get("total_steps", 0) or 0)
            done_steps = int(fm.get("completed_steps", 0) or 0)
            pct = int(done_steps / total_steps * 100) if total_steps else 0
            stats["active_plans"].append({
                "file": f.name,
                "title": fm.get("title", f.stem),
                "progress": f"{done_steps}/{total_steps} ({pct}%)",
                "priority": fm.get("priority", "medium"),
            })

    return stats


def get_memory_stats() -> Dict:
    """Read learning memory for stats."""
    memory_dir = VAULT_PATH / "Memory"
    stats = {"success_count": 0, "failure_count": 0, "task_types_learned": []}

    success_file = memory_dir / "success_patterns.json"
    if success_file.exists():
        try:
            data = json.loads(success_file.read_text(encoding="utf-8"))
            stats["success_count"] = len(data)
            stats["task_types_learned"] = list(data.keys())[:5]
        except Exception:
            pass

    failure_file = memory_dir / "failure_patterns.json"
    if failure_file.exists():
        try:
            data = json.loads(failure_file.read_text(encoding="utf-8"))
            stats["failure_count"] = len(data)
        except Exception:
            pass

    return stats


def get_recent_decisions(limit: int = 5) -> List[Dict]:
    """Get the most recent decision ledger entries."""
    ledger_dir = VAULT_PATH / "Decision_Ledger"
    decisions = []

    if not ledger_dir.exists():
        return decisions

    # Get today's and yesterday's ledger files
    for days_back in range(3):
        date = datetime.now() - timedelta(days=days_back)
        ledger_file = ledger_dir / f"decision_ledger_{date.strftime('%Y%m%d')}.md"
        if ledger_file.exists():
            content = ledger_file.read_text(encoding="utf-8")
            # Find decision entries
            entries = content.split("## Decision Entry:")
            for entry in entries[1:]:  # Skip header
                lines = entry.strip().splitlines()
                timestamp = lines[0].strip() if lines else ""
                decision_type = ""
                for line in lines[1:6]:
                    if "**Type**:" in line:
                        decision_type = line.split("**Type**:")[-1].strip()
                        break
                decisions.append({"timestamp": timestamp[:19], "type": decision_type})
                if len(decisions) >= limit:
                    return decisions

    return decisions


def calculate_success_rate() -> str:
    """Calculate overall task success rate."""
    completed = count_md_files(VAULT_PATH / "03_Completed_Tasks")
    failed = count_md_files(VAULT_PATH / "05_Failed_Tasks")
    total = completed + failed
    if total == 0:
        return "N/A"
    rate = int(completed / total * 100)
    return f"{rate}%"


def get_system_status() -> str:
    """Determine overall system status."""
    # Check for log files to see if system is running
    log_file = VAULT_PATH / "Logs" / "autonomous_system.log"
    if log_file.exists():
        mtime = log_file.stat().st_mtime
        age_seconds = time.time() - mtime
        if age_seconds < 120:
            return "Active"
        elif age_seconds < 3600:
            return "Idle"
    return "Offline"


def generate_dashboard() -> str:
    """Generate the complete Dashboard.md content."""
    now = datetime.now()
    task_stats = get_task_stats()
    plan_stats = get_plan_stats()
    memory_stats = get_memory_stats()
    recent_decisions = get_recent_decisions(limit=5)
    success_rate = calculate_success_rate()
    system_status = get_system_status()

    # Status indicator
    status_icon = {"Active": "ACTIVE", "Idle": "IDLE", "Offline": "OFFLINE"}.get(system_status, "UNKNOWN")

    # Approval queue table
    if task_stats["approval_items"]:
        approval_rows = "\n".join(
            f"| {item['file'][:40]} | {item['type']} | {item['priority']} | {item['created']} |"
            for item in task_stats["approval_items"]
        )
        approval_table = f"""| File | Type | Priority | Created |
|------|------|----------|---------|
{approval_rows}"""
    else:
        approval_table = "*No pending approvals*"

    # Recent completed table
    if task_stats["recent_completed"]:
        recent_rows = "\n".join(
            f"| {item['file'][:40]} | {item['type']} | {item['priority']} | {item['created']} |"
            for item in task_stats["recent_completed"]
        )
        recent_table = f"""| File | Type | Priority | Created |
|------|------|----------|---------|
{recent_rows}"""
    else:
        recent_table = "*No completed tasks this week*"

    # Active plans
    if plan_stats["active_plans"]:
        plan_rows = "\n".join(
            f"| {p['title'][:35]} | {p['progress']} | {p['priority']} |"
            for p in plan_stats["active_plans"]
        )
        plans_table = f"""| Plan | Progress | Priority |
|------|----------|----------|
{plan_rows}"""
    else:
        plans_table = "*No active plans*"

    # Recent decisions
    if recent_decisions:
        decision_rows = "\n".join(
            f"| {d['timestamp']} | {d['type']} |"
            for d in recent_decisions
        )
        decisions_table = f"""| Timestamp | Decision Type |
|-----------|--------------|
{decision_rows}"""
    else:
        decisions_table = "*No recent decisions*"

    total_tasks = (task_stats["incoming"] + task_stats["in_progress"] +
                   task_stats["completed"] + task_stats["needs_action"])

    dashboard = f"""# Personal AI Employee — Dashboard

> **Status:** {status_icon} | **Last Updated:** {now.strftime('%Y-%m-%d %H:%M:%S')}

---

## System Overview

| Metric | Value |
|--------|-------|
| System Status | {system_status} |
| Total Tasks Tracked | {total_tasks} |
| Success Rate (all-time) | {success_rate} |
| Completed Today | {task_stats['completed_today']} |
| Completed This Week | {task_stats['completed_this_week']} |
| Patterns Learned | {memory_stats['success_count']} success / {memory_stats['failure_count']} failure |

---

## Task Pipeline

| Stage | Count |
|-------|-------|
| Needs Action | {task_stats['needs_action']} |
| Incoming Tasks | {task_stats['incoming']} |
| In Progress | {task_stats['in_progress']} |
| Completed | {task_stats['completed']} |
| Failed | {task_stats['failed']} |
| Done (archive) | {task_stats['done']} |

---

## Approval Queue ({task_stats['approval']} pending)

{approval_table}

> To approve: move file to `Approved/` folder, or set `approved: true` in frontmatter.

---

## Active Plans ({plan_stats['in_progress']} active)

{plans_table}

---

## Recently Completed (last 7 days)

{recent_table}

---

## Recent Decisions

{decisions_table}

> Full audit trail: `Decision_Ledger/`

---

## Quick Commands

```bash
# Create a task
python run_task_skill.py create -t email -d "Description" -p high

# Start Ralph Wiggum loop
python ralph_wiggum_hook.py --start --prompt "Process all pending tasks"

# Generate CEO briefing
python weekly_ceo_report.py

# Auto-generate plans for pending tasks
python plan_generator.py --auto

# Update this dashboard
python dashboard_updater.py
```

---

## System Links

- Home (Live Dataview): [[Home]]
- Kanban Board: [[Kanban]]
- Company Handbook: [[Company_Handbook]]
- Business Goals: [[Business_Goals]]
- Decision Ledger: `Decision_Ledger/`
- Plans: `Plans/`
- Memory: `Memory/`

---

*Auto-generated by Dashboard Updater — {now.isoformat()}*
"""
    return dashboard


def update_dashboard():
    """Write the generated dashboard to Dashboard.md."""
    content = generate_dashboard()
    DASHBOARD_FILE.write_text(content, encoding="utf-8")
    print(f"[Dashboard Updater] Updated {DASHBOARD_FILE.name} at {datetime.now().strftime('%H:%M:%S')}")


def main():
    parser = argparse.ArgumentParser(description="Update Dashboard.md with live metrics")
    parser.add_argument("--watch", action="store_true", help="Continuous update mode")
    parser.add_argument("--interval", type=int, default=60, help="Update interval in seconds (default: 60)")
    args = parser.parse_args()

    if args.watch:
        print(f"[Dashboard Updater] Watching — updating every {args.interval}s. Press Ctrl+C to stop.")
        while True:
            try:
                update_dashboard()
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\n[Dashboard Updater] Stopped.")
                break
    else:
        update_dashboard()


if __name__ == "__main__":
    main()
