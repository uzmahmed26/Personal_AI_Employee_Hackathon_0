#!/usr/bin/env python3
"""
Ralph Wiggum Stop Hook

This script is invoked by Claude Code's Stop hook mechanism every time Claude
tries to exit. It checks whether the current autonomous task is complete.

- If complete (task file is in 03_Completed_Tasks/ or Done/) → exit 0 (allow stop)
- If incomplete and iterations < max → print re-injection prompt → Claude continues
- If max iterations reached → exit 0 (allow stop, prevents infinite loop)

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

Usage (automatic via .claude/settings.json Stop hook):
  python ralph_wiggum_hook.py

Manual usage:
  python ralph_wiggum_hook.py --task-id task_20260223_143022_a1b2c3
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Paths
VAULT_PATH = Path(__file__).parent
STATE_FILE = VAULT_PATH / ".claude" / "ralph_state.json"
COMPLETED_FOLDER = VAULT_PATH / "03_Completed_Tasks"
DONE_FOLDER = VAULT_PATH / "Done"
INCOMING_FOLDER = VAULT_PATH / "01_Incoming_Tasks"
IN_PROGRESS_FOLDER = VAULT_PATH / "02_In_Progress_Tasks"
FAILED_FOLDER = VAULT_PATH / "05_Failed_Tasks"

MAX_ITERATIONS = 10


def load_state() -> dict:
    """Load the current Ralph Loop state from file."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_state(state: dict):
    """Persist the Ralph Loop state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def is_task_complete(task_id: str) -> bool:
    """
    Check if a task has reached a terminal state (completed or done folder).
    Returns True if the task is finished.
    """
    if not task_id:
        # No specific task tracked — check if any tasks remain in incoming/in_progress
        incoming = list(INCOMING_FOLDER.glob("*.md")) if INCOMING_FOLDER.exists() else []
        in_progress = list(IN_PROGRESS_FOLDER.glob("*.md")) if IN_PROGRESS_FOLDER.exists() else []
        return len(incoming) == 0 and len(in_progress) == 0

    # Check if task file exists in completion folders
    for folder in [COMPLETED_FOLDER, DONE_FOLDER]:
        if folder.exists():
            # Match by task_id prefix
            matches = list(folder.glob(f"{task_id}*.md")) + list(folder.glob(f"*{task_id}*.md"))
            if matches:
                return True

    return False


def build_continuation_prompt(state: dict) -> str:
    """Build the re-injection prompt to feed back to Claude."""
    original_prompt = state.get("prompt", "Continue processing tasks in 01_Incoming_Tasks/")
    task_id = state.get("task_id", "")
    iteration = state.get("iteration", 1)

    # Count current tasks
    incoming_count = len(list(INCOMING_FOLDER.glob("*.md"))) if INCOMING_FOLDER.exists() else 0
    in_progress_count = len(list(IN_PROGRESS_FOLDER.glob("*.md"))) if IN_PROGRESS_FOLDER.exists() else 0

    prompt = f"""[RALPH WIGGUM LOOP - Iteration {iteration}/{MAX_ITERATIONS}]

The task is not yet complete. Continue working autonomously.

Original objective: {original_prompt}

Current system state:
- Incoming tasks pending: {incoming_count}
- Tasks in progress: {in_progress_count}
- Task ID being tracked: {task_id or "all pending tasks"}

Instructions:
1. Check 01_Incoming_Tasks/ for any unprocessed tasks
2. Process each task according to its type and priority
3. Move completed tasks to 03_Completed_Tasks/
4. Move tasks requiring approval to 04_Approval_Workflows/
5. Update Dashboard.md with current status
6. When ALL tasks are processed, output: <task_complete>RALPH_DONE</task_complete>

Continue now — do not stop until all tasks are handled or you output RALPH_DONE.
"""
    return prompt


def main():
    """
    Main Ralph Wiggum hook logic.

    Exit codes:
      0 = allow Claude to stop (task done or max iterations reached)
      non-zero = block stop (Claude receives stdout as new prompt)

    Note: Claude Code Stop hooks block exit when the hook outputs text to stdout.
    The output text is injected back as a new user message.
    """
    state = load_state()

    # If no active Ralph session, allow normal exit
    if not state.get("active", False):
        sys.exit(0)

    task_id = state.get("task_id", "")
    iteration = state.get("iteration", 0)

    # Check completion via explicit RALPH_DONE signal in state
    if state.get("completed", False):
        state["active"] = False
        save_state(state)
        sys.exit(0)

    # Check if task is complete by file presence
    if is_task_complete(task_id):
        state["active"] = False
        state["completed"] = True
        state["completed_at"] = datetime.now().isoformat()
        save_state(state)
        # Allow Claude to exit cleanly
        sys.exit(0)

    # Check max iterations guard
    if iteration >= MAX_ITERATIONS:
        state["active"] = False
        state["stopped_reason"] = "max_iterations_reached"
        save_state(state)
        print(f"[Ralph Wiggum] Max iterations ({MAX_ITERATIONS}) reached. Stopping loop.", file=sys.stderr)
        sys.exit(0)

    # Task is NOT complete — increment iteration and re-inject prompt
    iteration += 1
    state["iteration"] = iteration
    save_state(state)

    # Output the continuation prompt to stdout (Claude Code will re-inject this)
    continuation = build_continuation_prompt(state)
    print(continuation)

    # Exit with 0 — Claude Code treats non-empty stdout as the re-injection signal
    sys.exit(0)


# ── Helper: start a Ralph session (called by orchestrator) ──────────────────

def start_ralph_session(prompt: str, task_id: str = ""):
    """
    Initialize a new Ralph Wiggum loop session.

    Call this before invoking Claude Code to set up the loop state.
    The Stop hook will then keep Claude working until the task is done.

    Args:
        prompt: The initial instruction for Claude
        task_id: Optional specific task_id to track for completion
    """
    state = {
        "active": True,
        "prompt": prompt,
        "task_id": task_id,
        "iteration": 0,
        "completed": False,
        "started_at": datetime.now().isoformat(),
    }
    save_state(state)
    print(f"[Ralph Wiggum] Session started. Tracking task: {task_id or 'all pending'}")


def stop_ralph_session():
    """Manually stop an active Ralph session."""
    state = load_state()
    state["active"] = False
    state["completed"] = True
    state["stopped_at"] = datetime.now().isoformat()
    save_state(state)
    print("[Ralph Wiggum] Session stopped.")


if __name__ == "__main__":
    # CLI for manual session management
    import argparse
    parser = argparse.ArgumentParser(description="Ralph Wiggum Hook / Session Manager")
    parser.add_argument("--start", action="store_true", help="Start a new Ralph session")
    parser.add_argument("--stop", action="store_true", help="Stop the active Ralph session")
    parser.add_argument("--status", action="store_true", help="Show current session status")
    parser.add_argument("--prompt", default="Process all pending tasks in 01_Incoming_Tasks/")
    parser.add_argument("--task-id", default="", help="Task ID to track for completion")
    args = parser.parse_args()

    if args.start:
        start_ralph_session(args.prompt, args.task_id)
    elif args.stop:
        stop_ralph_session()
    elif args.status:
        state = load_state()
        print(json.dumps(state, indent=2))
    else:
        # Called as Stop hook by Claude Code
        main()
