# Personal AI Employee System

An autonomous task management and orchestration platform. Monitors Gmail, WhatsApp, and local files — creates structured tasks, routes them through a folder-based workflow, posts to social media, and generates business reports with minimal human intervention.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
cd MCP_SERVERS/gmail_mcp && npm install && cd ../..
cd MCP_SERVERS/linkedin_mcp && npm install && cd ../..
cd MCP_SERVERS/whatsapp_mcp && npm install && cd ../..
cd MCP_SERVERS/facebook_mcp && npm install && cd ../..
cd MCP_SERVERS/twitter_mcp && npm install && cd ../..
cd MCP_SERVERS/instagram_mcp && npm install && cd ../..

# 2. Configure credentials
cp .env.example .env
# Fill in API keys in .env

# 3. Run the system
python autonomous_system.py
```

---

## System Components

| Component | Description |
|-----------|-------------|
| `file_watcher.py` | Monitors `Inbox/` for new files, creates tasks |
| `gmail_watcher.py` | Monitors Gmail for important emails, creates tasks |
| `whatsapp_watcher.py` | Monitors `Inbox/whatsapp_queue/` for messages |
| `ralph_loop.py` | Retry engine — processes tasks up to 10 times |
| `task_processor.py` | Moves tasks through workflow folders every 30s |
| `notification_system.py` | Desktop notifications for high-priority tasks |
| `dashboard_updater.py` | Regenerates `Dashboard.md` every 60s |
| `plan_generator.py` | Auto-generates step-by-step plans for tasks |
| `weekly_ceo_report.py` | Monday morning CEO briefing report |

All components are started and crash-monitored automatically by `autonomous_system.py`.

---

## Workflow Pipeline

Tasks move through these folders based on their YAML `status` field:

```
Inbox/  →  01_Incoming_Tasks/  →  02_In_Progress_Tasks/  →  03_Completed_Tasks/
                              ↘  04_Approval_Workflows/  ↗
                              ↘  05_Failed_Tasks/   (after 10 retries)
```

**Human approval:** Tasks with `approval: true` go to `Pending_Approval/`. Move to `Approved/` or set `approved: true` in frontmatter to continue.

---

## MCP Integrations

| Service | Tools Available |
|---------|----------------|
| Gmail | send, draft, read, search, mark as read |
| LinkedIn | post, draft, get profile, get posts |
| WhatsApp | send message, send template, check queue |
| Facebook | post, draft, get insights, get comments |
| Twitter/X | tweet, draft, get timeline, search, metrics |
| Instagram | post, story, get insights, reply to comments |
| Odoo ERP | invoices, customers, financial summary |

All MCP servers run via `.claude/settings.json` and are accessible as tools inside Claude Code.

---

## Agent Skills

Trigger these by typing the keyword in Claude Code:

| Keyword | Skill |
|---------|-------|
| "create task", "add to inbox" | Create structured task file |
| "check emails", "reply to email" | Gmail MCP |
| "WhatsApp message" | WhatsApp MCP |
| "post to LinkedIn" | LinkedIn MCP |
| "post to Facebook" | Facebook MCP |
| "tweet", "post on Twitter" | Twitter MCP |
| "Instagram post" | Instagram MCP |
| "post everywhere", "cross-post" | All social platforms |
| "create invoice", "Odoo" | Odoo ERP |
| "CEO briefing", "weekly report" | Weekly report + all MCPs |
| "refresh dashboard", "vault note" | Obsidian vault |
| "process all tasks" | Ralph loop (autonomous mode) |

---

## Testing the System

### 1. Test File Watcher
Drop any file into the `Inbox/` folder:
```bash
# Drop a PDF, text file, or anything into Inbox/
# Within 30 seconds a task file will appear in 01_Incoming_Tasks/
```

### 2. Test Task Creation via CLI
```bash
python run_task_skill.py create -t email -d "Client asked for invoice" -p high
python run_task_skill.py create -t file_arrival -d "New contract received" -p critical --approval
python run_task_skill.py demo   # Creates 2 example tasks
```

### 3. Test Approval Workflow
```bash
python approve.py list                          # See pending approvals
python approve.py show <filename>               # Read the approval request
python approve.py approve <filename>            # Approve it
python approve.py reject <filename>             # Reject with reason
```

### 4. Test Gmail Watcher
Send an email marked as **Important** in Gmail. Within 60 seconds a task file will appear in `01_Incoming_Tasks/`.

### 5. Test WhatsApp
Drop a JSON file into `Inbox/whatsapp_queue/`:
```json
{"from": "923001234567", "body": "Please send me the invoice", "timestamp": "2026-02-24T10:00:00"}
```

### 6. Test Social Media (via Claude Code)
Type in Claude Code chat:
- `post to LinkedIn: "Excited to launch our new AI product!"`
- `tweet: "Big news coming soon! #AI #Startup"`
- `post to Facebook: "Check out our latest update"`

All write operations create approval requests in `Pending_Approval/` first (HITL pattern).

### 7. Test Dashboard
```bash
python dashboard_updater.py       # Regenerate Dashboard.md once
python dashboard_updater.py --watch  # Live update every 60s
```
Then open `Dashboard.md` in Obsidian to see the live view.

### 8. Test Plan Generator
```bash
python plan_generator.py --auto   # Generate plans for all pending tasks
```
Plans appear in `Plans/` folder.

### 9. Test CEO Report
```bash
python weekly_ceo_report.py       # Generate a briefing report
```
Report saved to `Briefings/` folder.

### 10. Test Ralph Loop (Autonomous Mode)
```bash
python ralph_wiggum_hook.py --start --prompt "Process all pending tasks"
python ralph_wiggum_hook.py --status
python ralph_wiggum_hook.py --stop
```

---

## Obsidian Vault

Open this folder as an Obsidian vault. Installed plugins:
- **Dataview** — live task queries in `Home.md`
- **Kanban** — visual pipeline board in `Kanban.md`
- **Templater** — task/plan/briefing templates in `Templates/`

Key views:
- `Home.md` — live dashboard with Dataview queries
- `Kanban.md` — drag-and-drop task board
- `Dashboard.md` — auto-generated system status

---

## Environment Variables

All secrets live in `.env` (never committed). Required keys:

```
GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN
LINKEDIN_ACCESS_TOKEN, LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET
WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID
FB_APP_ID, FB_APP_SECRET, FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN
TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, TWITTER_BEARER_TOKEN
IG_USER_ID
```

See `.env.example` for the full template.

---

## Troubleshooting

See `TROUBLESHOOTING.md` for common issues. Quick checks:
- `.env` has valid credentials
- `01_Incoming_Tasks/` through `05_Failed_Tasks/` folders exist (auto-created on startup)
- Gmail OAuth token valid — re-check `GMAIL_REFRESH_TOKEN` in `.env` if auth fails
- WhatsApp/Facebook tokens expire — regenerate from developer consoles if API calls fail
