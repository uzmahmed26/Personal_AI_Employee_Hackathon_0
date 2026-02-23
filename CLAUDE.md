# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Personal AI Employee System** — an autonomous task management and orchestration platform that monitors inputs (files, emails), creates structured tasks, routes them through a folder-based workflow pipeline, and generates business insights with minimal human intervention.

## Running the System

```bash
# Full autonomous system (recommended — starts all components)
python autonomous_system.py

# Intelligent system (adds learning/AI modules)
python intelligent_system.py

# Individual components
python file_watcher.py              # Monitor Inbox/ folder for new files
python gmail_watcher.py             # Monitor Gmail (OAuth required on first run)
python whatsapp_watcher.py          # Monitor WhatsApp queue (Inbox/whatsapp_queue/)
python ralph_loop.py                # Task retry/processing engine (max 10 retries)
python task_processor.py            # Move tasks through workflow folders
python dashboard_updater.py         # Regenerate Dashboard.md from live data
python dashboard_updater.py --watch # Continuously update Dashboard.md every 60s
python plan_generator.py --auto     # Auto-generate Plan.md for all pending tasks
python weekly_ceo_report.py         # Generate Monday morning CEO briefing

# Ralph Wiggum loop management
python ralph_wiggum_hook.py --start --prompt "Process all pending tasks"
python ralph_wiggum_hook.py --status
python ralph_wiggum_hook.py --stop

# Manual task creation via CLI (SKILL)
python run_task_skill.py create -t file_arrival -d "Description" -p high
python run_task_skill.py create -t email -d "Client invoice request" -p high --approval
python run_task_skill.py demo

# Human approval workflow
python approve.py list              # List all pending approvals
python approve.py show <filename>   # Read approval request details
python approve.py approve <filename> # Approve and move to Approved/
python approve.py reject <filename>  # Reject with reason

# Plan management
python plan_generator.py --task-id <id> --title "My Plan" --steps "step1|step2|step3"
python plan_generator.py --update PLAN_<task_id>.md

# Testing
python test_workflow.py
python requirements_checker.py
python check_mcp_status.py
```

## Installation

```bash
pip install -r requirements.txt   # Python deps (Google API, plyer, etc.)
npm install                        # Node.js deps for MCP microservices
cp .env.example .env              # Then fill in real API credentials
```

Gmail requires OAuth setup on first run — see `GMAIL_SETUP_GUIDE.md`.

## MCP Servers (Connected via `.claude/settings.json`)

| Server | Tools | Setup Required |
|--------|-------|----------------|
| `gmail` | `send_email`, `draft_email`, `read_emails`, `search_emails`, `mark_as_read`, `get_email_details` | `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN` in `.env` |
| `linkedin` | `post_to_linkedin`, `draft_linkedin_post`, `get_linkedin_profile`, `get_recent_posts` | `LINKEDIN_ACCESS_TOKEN` in `.env` |
| `whatsapp` | `send_whatsapp_message`, `send_whatsapp_template`, `check_whatsapp_queue`, `queue_whatsapp_reply` | `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID` in `.env` |
| `facebook` | `post_to_facebook`, `draft_facebook_post`, `get_page_posts`, `get_page_insights`, `get_post_comments`, `delete_facebook_post` | `FB_PAGE_ID`, `FB_PAGE_ACCESS_TOKEN` in `.env` |
| `twitter` | `post_tweet`, `draft_tweet`, `get_timeline`, `search_tweets`, `get_tweet_metrics`, `delete_tweet` | `TWITTER_API_KEY`, `TWITTER_ACCESS_TOKEN`, `TWITTER_BEARER_TOKEN` in `.env` |
| `instagram` | `post_to_instagram`, `draft_instagram_post`, `post_instagram_story`, `get_instagram_posts`, `get_instagram_insights`, `get_post_comments`, `reply_to_comment` | `IG_USER_ID`, `FB_PAGE_ACCESS_TOKEN` in `.env` |
| `odoo` | `get_financial_summary`, `list_customers`, `create_customer`, `list_invoices`, `create_invoice_draft`, `get_overdue_invoices` | `ODOO_URL`, `ODOO_DB`, `ODOO_PASSWORD` in `.env` |
| `context7` | Library docs lookup | Runs via `npx @upstash/context7-mcp@latest` — no setup |

Each MCP server in `MCP_SERVERS/*/index.js` implements the MCP protocol over stdio using `@modelcontextprotocol/sdk`. The old `server.js` files are HTTP fallback APIs.

**Install MCP dependencies** (one-time per server):
```bash
cd MCP_SERVERS/gmail_mcp && npm install
cd MCP_SERVERS/linkedin_mcp && npm install
cd MCP_SERVERS/whatsapp_mcp && npm install
cd MCP_SERVERS/odoo_mcp && npm install
```

## Agent Skills (`.claude/skills/`)

| Skill | Trigger | Uses |
|-------|---------|------|
| `task-executor` | "create task", "add to inbox" | `run_task_skill.py` |
| `email-handler` | "check emails", "reply to email" | Gmail MCP |
| `whatsapp-handler` | "WhatsApp message", "reply on WhatsApp" | WhatsApp MCP |
| `linkedin-poster` | "post to LinkedIn", "LinkedIn post" | LinkedIn MCP |
| `odoo-accounting` | "create invoice", "Odoo", "financials" | Odoo MCP |
| `facebook-poster` | "post to Facebook", "FB post", "Facebook update" | Facebook MCP |
| `twitter-poster` | "tweet", "post on Twitter/X", "Twitter update" | Twitter MCP |
| `instagram-poster` | "Instagram post", "IG post", "Insta post" | Instagram MCP |
| `social-media-manager` | "post everywhere", "all platforms", "cross-post", "social media update" | Facebook + Twitter + Instagram MCPs |
| `ceo-briefing` | "CEO briefing", "weekly report" | All MCPs + `weekly_ceo_report.py` |
| `obsidian-manager` | "create note in Obsidian", "update Kanban", "vault note", "refresh dashboard" | Obsidian vault files |
| `ralph-loop` | "process all tasks", "run autonomously" | Stop hook + all skills |

All skills follow the **HITL pattern**: write operations generate approval requests in `Pending_Approval/` and never execute directly. Read operations are immediate.

## Architecture

### Workflow Pipeline (Folder-Based FSM)

Tasks move through these folders as their state changes:

```
01_Incoming_Tasks/ → 02_In_Progress_Tasks/ → 03_Completed_Tasks/
                  ↘ 04_Approval_Workflows/ ↗
                  ↘ 05_Failed_Tasks/  (after >10 retries)
```

`task_processor.py` reads task YAML frontmatter to determine where to move each file. `ralph_loop.py` is the retry engine (max 10 attempts) that learns from failures.

### Core Orchestration

- **`autonomous_system.py`** — Main entry point. Starts all components as threads/processes, monitors health, auto-restarts failed components (up to 5 attempts).
- **`intelligent_system.py`** — Enhanced version that also loads AI/learning modules.
- **`task_executor_skill.py`** — Core task creation engine: generates YAML frontmatter, calculates business goal alignment scores (0–1), and performs risk assessment.

### Intelligence Layer

- **`learning_memory.py`** — Persists success/failure patterns to `Memory/` JSON files.
- **`self_correction.py`** — Analyzes failed tasks and adjusts strategies automatically.
- **`business_goal_alignment.py`** — Scores tasks against `Business/business_goals.md`.
- **`risk_radar.py`** — Continuously scans for high-risk tasks and triggers escalation.
- **`decision_ledger.py`** — Writes immutable decision records to `Decision_Ledger/`.

### MCP Microservices (`MCP_SERVERS/`)

Independent Node.js/Python services for external integrations: Gmail, LinkedIn, WhatsApp, file system operations, and context management. Run via `npm start` or individually.

### Watcher Layer

All watchers inherit from `base_watcher.py` (`BaseWatcher` ABC). To add a new watcher:
1. Subclass `BaseWatcher`
2. Implement `check_for_updates() -> list` and `create_action_file(item) -> Path`
3. Add to `autonomous_system.py` components dict

WhatsApp messages are fed via JSON files dropped into `Inbox/whatsapp_queue/` or via the shared `Inbox/whatsapp_incoming.json` queue file written by `whatsapp_mcp_server.py`.

### Ralph Wiggum Stop Hook

`.claude/settings.json` configures the `Stop` hook to run `ralph_wiggum_hook.py`. State is persisted in `.claude/ralph_state.json`. Start a loop with:
```bash
python ralph_wiggum_hook.py --start --prompt "Process all tasks in 01_Incoming_Tasks/"
```
Then run `claude` — it will keep working until tasks are done or 10 iterations are reached.

### Key Data Directories

| Directory | Contents |
|-----------|----------|
| `Needs_Action/` | Tasks created by Watchers (hackathon spec primary input) |
| `Done/` | Archive for Watcher-created tasks after processing |
| `Pending_Approval/` | Items awaiting human approval (hackathon spec) |
| `Approved/` | Human-approved items ready for execution |
| `Plans/` | `PLAN_<task_id>.md` files with step-by-step execution plans |
| `Memory/` | JSON files: success/failure/approval patterns, task type performance |
| `Decision_Ledger/` | Daily markdown decision logs (immutable audit trail) |
| `Logs/` | Component-level logs (`autonomous_system.log`, `ralph_loop.log`, etc.) |
| `Reports/` | Generated dashboards and CEO reports |
| `Business/` | Business goals, company handbook, LinkedIn queue |

## Task File Format

Tasks are markdown files with YAML frontmatter:

```yaml
---
task_id: uuid
task_type: file_arrival | email | manual
priority: critical | high | medium | low
status: pending | in_progress | completed | failed | needs_approval
business_alignment: 0.0–1.0
risk_level: low | medium | high | critical
retry_count: 0
---
Task description here...
```

## Environment Variables

All secrets live in `.env` (never committed). See `.env.example` for required keys:
- Google OAuth credentials (Gmail API)
- WhatsApp Business API token
- LinkedIn access token
- General `API_KEY`, `DATABASE_URL`

## Troubleshooting

See `TROUBLESHOOTING.md` for common issues. Key things to check:
- `.env` has valid credentials before starting
- `01_Incoming_Tasks/` through `05_Failed_Tasks/` folders exist
- Gmail OAuth token is valid (re-run `gmail_watcher.py` to refresh)
