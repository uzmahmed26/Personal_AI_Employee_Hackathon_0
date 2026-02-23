#!/usr/bin/env python3
"""
Plan Generator — Personal AI Employee System

Creates Plan.md files in Plans/ for complex multi-step tasks.
Claude reads these plans and ticks off checkboxes as it completes each step.

The Plans/ folder is monitored by the task processor; when all steps
are checked off the plan is moved to Done/.

Usage:
  python plan_generator.py --task-id <id> --title "Invoice Client A" --steps "step1|step2|step3"
  python plan_generator.py --task-id <id> --task-file 01_Incoming_Tasks/task_xyz.md
  python plan_generator.py --auto   # Auto-generate plans for all unplanned tasks in Incoming
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict

try:
    import yaml
except ImportError:
    yaml = None

VAULT_PATH = Path(__file__).parent
PLANS_DIR = VAULT_PATH / "Plans"
INCOMING_DIR = VAULT_PATH / "01_Incoming_Tasks"
NEEDS_ACTION_DIR = VAULT_PATH / "Needs_Action"
MEMORY_DIR = VAULT_PATH / "Memory"


# Default step templates by task type
TASK_TYPE_TEMPLATES: Dict[str, List[str]] = {
    "email": [
        "Read and analyse the email content",
        "Identify required actions and urgency",
        "Draft response or action plan",
        "Review draft (human approval if new contact)",
        "Send reply via Email MCP",
        "Log outcome to Decision Ledger",
        "Move task to Completed",
    ],
    "whatsapp": [
        "Read WhatsApp message content",
        "Identify request type (invoice / query / urgent / other)",
        "Draft reply or action",
        "Create approval file in 04_Approval_Workflows/ for human review",
        "After approval: send reply via WhatsApp MCP",
        "Log outcome",
        "Move task to Completed",
    ],
    "file_arrival": [
        "Identify file type and source",
        "Extract relevant information from file",
        "Categorise and tag content",
        "Create task or update relevant records",
        "Archive original file to appropriate folder",
        "Update Dashboard",
    ],
    "linkedin": [
        "Read post content or brief",
        "Check Business/LinkedIn_Queue/ for scheduled posts",
        "Review post for tone and compliance with Company Handbook",
        "Create approval file in 04_Approval_Workflows/",
        "After approval: post via LinkedIn MCP",
        "Log post URL and engagement tracking",
        "Move to Completed",
    ],
    "approval_required": [
        "Review the approval request details",
        "Check Company_Handbook.md for relevant policy",
        "Verify all required information is present",
        "Create APPROVAL_REQUIRED file in 04_Approval_Workflows/",
        "Notify human (CEO Brief or notification)",
        "Wait for approval: monitor 04_Approval_Workflows/ for approved: true",
        "After approval: execute the approved action",
        "Log decision to Decision Ledger",
        "Move to Completed",
    ],
    "manual": [
        "Understand the task objective",
        "Break down into sub-steps",
        "Execute each sub-step in order",
        "Verify output quality",
        "Update Dashboard",
        "Move to Completed",
    ],
}


def parse_task_frontmatter(task_file: Path) -> Dict:
    """Parse YAML frontmatter from a task file."""
    try:
        content = task_file.read_text(encoding="utf-8")
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                if yaml:
                    return yaml.safe_load(parts[1]) or {}
                else:
                    # Simple fallback parser
                    result = {}
                    for line in parts[1].strip().splitlines():
                        if ":" in line:
                            k, _, v = line.partition(":")
                            result[k.strip()] = v.strip()
                    return result
    except Exception:
        pass
    return {}


def get_default_steps(task_type: str, description: str = "") -> List[str]:
    """Get default steps for a task type, with optional description-based augmentation."""
    base_steps = TASK_TYPE_TEMPLATES.get(task_type, TASK_TYPE_TEMPLATES["manual"])

    # Augment steps based on description keywords
    extra_steps = []
    desc_lower = description.lower()
    if any(w in desc_lower for w in ["invoice", "billing", "$"]):
        extra_steps.append("Update Accounting records in Odoo or accounting log")
    if any(w in desc_lower for w in ["schedule", "calendar", "meeting"]):
        extra_steps.append("Create or update calendar event")
    if any(w in desc_lower for w in ["follow up", "follow-up", "reminder"]):
        extra_steps.append("Set follow-up reminder in 3 days")

    return base_steps + extra_steps


def create_plan(
    task_id: str,
    title: str,
    steps: List[str],
    task_type: str = "manual",
    priority: str = "medium",
    description: str = "",
    source_task_file: Optional[str] = None,
) -> Path:
    """
    Create a Plan.md file in Plans/.

    Args:
        task_id: Unique task identifier.
        title: Human-readable plan title.
        steps: List of step descriptions (will become checkboxes).
        task_type: Task type for metadata.
        priority: Task priority.
        description: Optional task description.
        source_task_file: Optional path to the originating task file.

    Returns:
        Path to the created plan file.
    """
    PLANS_DIR.mkdir(parents=True, exist_ok=True)

    plan_file = PLANS_DIR / f"PLAN_{task_id}.md"

    now = datetime.now()

    # Build YAML frontmatter
    frontmatter_lines = [
        "---",
        f"plan_id: PLAN_{task_id}",
        f"task_id: {task_id}",
        f"title: \"{title}\"",
        f"task_type: {task_type}",
        f"priority: {priority}",
        f"created: {now.isoformat()}",
        f"status: in_progress",
        f"total_steps: {len(steps)}",
        f"completed_steps: 0",
    ]
    if source_task_file:
        frontmatter_lines.append(f"source_task: \"{source_task_file}\"")
    frontmatter_lines.append("---")

    # Build step checkboxes
    steps_md = "\n".join(f"- [ ] {step}" for step in steps)

    # Build progress indicator
    progress_bar = "░" * len(steps)

    content = "\n".join(frontmatter_lines) + f"""

# Plan: {title}

**Created:** {now.strftime('%Y-%m-%d %H:%M:%S')}
**Task ID:** `{task_id}`
**Type:** {task_type.replace('_', ' ').title()}
**Priority:** {priority.title()}

---

## Objective

{description or title}

---

## Steps

{steps_md}

---

## Progress

`[{progress_bar}]` 0 / {len(steps)} steps complete

---

## Notes

*(Add notes here as you work through the plan)*

---

## Completion

When all steps are checked, update frontmatter: `status: completed`
Then move this file to `Done/` or `03_Completed_Tasks/`.

---
*Generated by Plan Generator — {now.isoformat()}*
"""

    plan_file.write_text(content, encoding="utf-8")
    print(f"[Plan Generator] Created: {plan_file.name}")
    return plan_file


def update_plan_progress(plan_file: Path) -> Dict:
    """
    Re-count checked steps and update the frontmatter + progress bar.

    Returns dict with total, completed, percentage.
    """
    content = plan_file.read_text(encoding="utf-8")
    total = content.count("- [ ]") + content.count("- [x]") + content.count("- [X]")
    completed = content.count("- [x]") + content.count("- [X]")
    pct = int((completed / total * 100)) if total else 0

    # Update progress bar
    filled = int(completed / total * 20) if total else 0
    bar = "█" * filled + "░" * (20 - filled)
    new_progress = f"`[{bar}]` {completed} / {total} steps complete ({pct}%)"

    # Replace old progress line
    content = re.sub(
        r"`\[.*?\]`.*steps complete.*",
        new_progress,
        content
    )

    # Update frontmatter fields
    if yaml:
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
            fm["completed_steps"] = completed
            fm["total_steps"] = total
            if completed == total and total > 0:
                fm["status"] = "completed"
                fm["completed_at"] = datetime.now().isoformat()
            new_fm = yaml.dump(fm, default_flow_style=False)
            content = f"---\n{new_fm}---{parts[2]}"

    plan_file.write_text(content, encoding="utf-8")
    return {"total": total, "completed": completed, "percentage": pct}


def auto_generate_plans():
    """Scan Incoming and Needs_Action for tasks that don't have a plan yet."""
    generated = 0
    existing_plan_ids = {p.stem.replace("PLAN_", "") for p in PLANS_DIR.glob("PLAN_*.md")} if PLANS_DIR.exists() else set()

    for folder in [INCOMING_DIR, NEEDS_ACTION_DIR]:
        if not folder.exists():
            continue
        for task_file in folder.glob("*.md"):
            fm = parse_task_frontmatter(task_file)
            task_id = fm.get("task_id", task_file.stem)

            if task_id in existing_plan_ids:
                continue  # Plan already exists

            task_type = fm.get("type", "manual")
            priority = fm.get("priority", "medium")
            description = fm.get("description", "")
            title = fm.get("subject", fm.get("filename", task_file.stem))

            steps = get_default_steps(task_type, description)
            create_plan(
                task_id=task_id,
                title=f"Plan for {title}",
                steps=steps,
                task_type=task_type,
                priority=priority,
                description=description,
                source_task_file=str(task_file.name),
            )
            generated += 1

    print(f"[Plan Generator] Auto-generated {generated} plan(s).")
    return generated


def main():
    parser = argparse.ArgumentParser(
        description="Generate Plan.md files for AI Employee tasks"
    )
    parser.add_argument("--task-id", help="Task ID to create a plan for")
    parser.add_argument("--title", help="Plan title")
    parser.add_argument("--steps", help="Pipe-separated step descriptions: 'step1|step2|step3'")
    parser.add_argument("--task-type", default="manual", help="Task type (email, file_arrival, etc.)")
    parser.add_argument("--priority", default="medium", help="Priority level")
    parser.add_argument("--description", default="", help="Task description")
    parser.add_argument("--task-file", help="Path to existing task file to generate plan from")
    parser.add_argument("--auto", action="store_true", help="Auto-generate plans for all unplanned tasks")
    parser.add_argument("--update", help="Update progress for a plan file (provide plan filename)")

    args = parser.parse_args()

    if args.update:
        plan_file = PLANS_DIR / args.update
        if not plan_file.exists():
            plan_file = Path(args.update)
        progress = update_plan_progress(plan_file)
        print(f"Progress: {progress['completed']}/{progress['total']} ({progress['percentage']}%)")

    elif args.auto:
        auto_generate_plans()

    elif args.task_file:
        task_path = Path(args.task_file)
        if not task_path.is_absolute():
            task_path = VAULT_PATH / args.task_file
        fm = parse_task_frontmatter(task_path)
        task_id = args.task_id or fm.get("task_id", task_path.stem)
        task_type = args.task_type or fm.get("type", "manual")
        priority = args.priority or fm.get("priority", "medium")
        description = args.description or fm.get("description", "")
        title = args.title or fm.get("subject", task_path.stem)
        steps_input = args.steps or ""
        steps = [s.strip() for s in steps_input.split("|") if s.strip()] if steps_input else get_default_steps(task_type, description)
        create_plan(task_id, title, steps, task_type, priority, description, str(task_path.name))

    elif args.task_id:
        if not args.title:
            parser.error("--title is required when using --task-id")
        steps_input = args.steps or ""
        steps = [s.strip() for s in steps_input.split("|") if s.strip()] if steps_input else get_default_steps(args.task_type, args.description)
        create_plan(args.task_id, args.title, steps, args.task_type, args.priority, args.description)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
