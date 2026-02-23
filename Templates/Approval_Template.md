---
task_id: approval_{{date:YYYYMMDD}}_{{time:HHmmss}}_000000
type: approval_required
priority: high
status: pending_approval
created: {{date:YYYY-MM-DD}}T{{time:HH:mm:ss}}
approved: false
risk_level: medium
action_type:
platform:
---

## Approval Request: {{title}}

**Created:** {{date:YYYY-MM-DD}} {{time:HH:mm}}
**Action Type:**
**Platform:**
**Risk Level:** Medium

---

### What will happen if approved:


### Content / Details:


### To Approve:
1. Set `approved: true` in the frontmatter above, **OR**
2. Move this file to the `Approved/` folder, **OR**
3. Run: `python approve.py approve <filename>`

### To Reject:
Run: `python approve.py reject <filename>`

---

*Waiting for human approval — AI will not proceed until approved.*
*Created via Obsidian Template*
