---
name: email-handler
description: Use this skill when the user needs to read emails, reply to emails, draft email responses, process email tasks from Needs_Action/ or 01_Incoming_Tasks/, send emails, or handle any Gmail-related task. Trigger phrases: "check emails", "reply to email", "read email", "send email", "draft email response", "process email task", "email from client".
version: 1.0.0
---

# Email Handler Skill

Reads, processes, and responds to emails using the Gmail MCP server. All email sends require HITL approval unless the recipient is a known contact.

## Objective

Process email-type tasks from the workflow folders, draft appropriate responses, route them through the approval workflow, and send via Gmail MCP.

## Procedure

### 1. Find Email Tasks

Check for pending email tasks:
```bash
ls Needs_Action/
ls 01_Incoming_Tasks/
```

Look for files with `type: email` in their YAML frontmatter.

### 2. Read the Email Content

For each email task file, read it to understand:
- Sender (`from:` field)
- Subject
- Message snippet / body
- Required action

To get full email details if a message_id is available:
```
Use MCP tool: gmail → get_email_details
  message_id: <id from task frontmatter>
```

To read recent unread emails:
```
Use MCP tool: gmail → read_emails
  query: "is:unread is:important"
  max_results: 10
```

### 3. Analyse and Determine Action

For each email, determine:
- **Reply needed?** → Draft a response
- **Invoice/payment request?** → Create approval task + Odoo invoice draft
- **New contact?** → Flag for approval, do NOT auto-reply
- **Spam/low priority?** → Mark as read and log
- **Urgent (keywords: asap, urgent, deadline)?** → Elevate priority

Check Company_Handbook.md for tone guidelines before drafting.

### 4. Draft the Response (HITL)

```
Use MCP tool: gmail → draft_email
  to: <sender email>
  subject: Re: <original subject>
  body: <drafted response>
```

Then create a task for approval:
```bash
python run_task_skill.py create -t approval_required \
  -d "Email reply draft ready for review — To: <sender>" \
  -p high --approval \
  -m to="<sender>" subject="Re: <subject>" draft_id="<draft_id>"
```

### 5. After Approval — Send

When approval file is moved to Approved/ (or `approved: true` set):

```
Use MCP tool: gmail → send_email
  to: <recipient>
  subject: <subject>
  body: <approved body>
```

### 6. Mark Original as Read + Complete Task

```
Use MCP tool: gmail → mark_as_read
  message_id: <original message id>
```

Move task file to 03_Completed_Tasks/:
```bash
python approve.py approve <task_filename>
```

Update dashboard:
```bash
python dashboard_updater.py
```

## Reply Templates

### Invoice Request
```
Hello [Name],

Thank you for reaching out. Please find your invoice for [period] attached.

Invoice Details:
- Amount: $[amount]
- Due Date: [date]
- Reference: [invoice #]

Please don't hesitate to contact us if you have any questions.

Best regards,
[Your Name]
```

### General Acknowledgment
```
Hello [Name],

Thank you for your email. I've received your message regarding [topic] and will
get back to you within [timeframe].

Best regards,
[Your Name]
```

### Follow-up
```
Hello [Name],

I wanted to follow up on my previous email regarding [topic] sent on [date].

[Brief context]

Could you please let me know your thoughts when you get a chance?

Best regards,
[Your Name]
```

## Security Rules

- NEVER send to new/unknown contacts without human approval
- NEVER include financial account details in email body
- Rate limit: max 10 emails per hour (enforced by Gmail MCP config)
- Always create a draft first with `draft_email` before using `send_email`
- Log all sent emails in Decision_Ledger/
