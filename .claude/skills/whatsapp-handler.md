---
name: whatsapp-handler
description: Use this skill to handle WhatsApp messages, reply to WhatsApp conversations, process WhatsApp tasks from Needs_Action/ or 01_Incoming_Tasks/, or send WhatsApp messages. Trigger phrases: "WhatsApp message", "reply on WhatsApp", "send WhatsApp", "WhatsApp from client", "check WhatsApp", "process WhatsApp task".
version: 1.0.0
---

# WhatsApp Handler Skill

Processes incoming WhatsApp messages and sends replies via the WhatsApp MCP server. All outgoing messages MUST go through human approval.

## Objective

Read WhatsApp tasks from the workflow folders, analyse the message, draft an appropriate response, route for human approval, and send via WhatsApp MCP after approval.

## Procedure

### 1. Find WhatsApp Tasks

```bash
ls Needs_Action/
ls 01_Incoming_Tasks/
```

Look for files with `type: whatsapp` in YAML frontmatter. Also check:
```
Use MCP tool: whatsapp → check_whatsapp_queue
```

### 2. Analyse the Message

For each WhatsApp task, read the file and determine:

| Message Content | Required Action |
|----------------|-----------------|
| Invoice / payment request | Create invoice in Odoo, draft payment details reply |
| Pricing / quote request | Draft quote reply |
| Urgent / ASAP | Elevate to high priority, escalate |
| General question | Draft informative reply |
| Appointment request | Check calendar, draft availability reply |
| Complaint | Escalate, flag for immediate human review |

### 3. Check Business Rules

Read Company_Handbook.md for:
- Tone guidelines ("Always be polite on WhatsApp")
- Which contacts require human-only responses
- Auto-reply thresholds

### 4. Draft Reply (HITL — ALWAYS)

```
Use MCP tool: whatsapp → queue_whatsapp_reply
  phone_number: <sender phone from task>
  message: <drafted reply text>
  draft_id: <task_id>
```

This creates a file in `Pending_Approval/WHATSAPP_REPLY_<timestamp>.md`.

**Never use `send_whatsapp_message` directly without approval.**

### 5. Create Approval Task

```bash
python run_task_skill.py create -t approval_required \
  -d "WhatsApp reply ready for approval — to: <phone>" \
  -p high --approval \
  -m phone="<phone>" message_preview="<first 100 chars>"
```

### 6. After Approval — Send

When human approves (file moved to Approved/ or `approved: true`):

```
Use MCP tool: whatsapp → send_whatsapp_message
  phone_number: <phone>
  message: <approved message>
  force_send: true
```

### 7. Complete the Task

Move original task to completed:
```bash
python dashboard_updater.py
```

## Reply Templates

### Invoice/Payment Reply
```
Hello! Thank you for your message.

I've prepared your invoice for [month]:
• Amount: $[amount]
• Reference: [INV-XXX]
• Due date: [date]

I'll send the full invoice to your email at [email].

Please let me know if you have any questions!
```

### Pricing Reply
```
Hello! Thanks for your interest.

Here's a quick overview:
• [Service/Product 1]: $[price]
• [Service/Product 2]: $[price]

For a detailed quote tailored to your needs, I'll follow up via email.

Feel free to ask any questions!
```

### Urgent Acknowledgment
```
Hello! I received your urgent message and I'm looking into it right now.

I'll get back to you within [timeframe] with a full update.

Thank you for your patience!
```

## Security Rules

- NEVER send messages with financial account numbers (bank details, card numbers)
- NEVER auto-reply to unknown numbers without human approval
- NEVER send bulk messages (each send goes through individual approval)
- All WhatsApp sessions and credentials stay LOCAL — never sync to cloud
- Rate limit: WhatsApp Business API enforces per-hour/per-day message limits
