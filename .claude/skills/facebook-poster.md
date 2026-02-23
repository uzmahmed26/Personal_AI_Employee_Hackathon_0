---
name: facebook-poster
description: Use this skill for any Facebook task. Trigger phrases: "post to Facebook", "Facebook post", "FB post", "share on Facebook", "post on Facebook", "Facebook update", "Facebook page", "get Facebook insights", "Facebook metrics", "delete Facebook post".
version: 1.0.0
---

# Facebook Poster Skill

Manages drafting, approval, and publishing of posts to a Facebook Page using the Facebook Graph API MCP server. All posts follow the HITL pattern: draft → approve → publish.

## Procedure

### 1. Draft the Post

```
Use MCP tool: facebook → draft_facebook_post
  content: <post content (40-80 words recommended, max 63,206 chars)>
  title: <short description for file tracking>
```

This saves a draft to `Business/Facebook_Queue/DRAFT_*.md` and creates an approval file in `Pending_Approval/`.

### 2. Notify for Approval

Tell the user:
> "Facebook post drafted and waiting for your approval. Run `python approve.py list` to review, or check `Pending_Approval/`."

### 3. After Human Approval — Publish

```
Use MCP tool: facebook → post_to_facebook
  content: <approved content>
  force_execute: true
```

Post is published and logged to `Business/Facebook_Queue/Posted/POSTED_*.md`.

### 4. Read-Only Operations (no approval needed)

**Get recent posts:**
```
Use MCP tool: facebook → get_page_posts
  limit: 10
```

**Get page insights (reach, impressions, engagement):**
```
Use MCP tool: facebook → get_page_insights
  period: week
```

**Get comments on a post:**
```
Use MCP tool: facebook → get_post_comments
  post_id: <post_id>
```

**Delete a post:**
```
Use MCP tool: facebook → delete_facebook_post
  post_id: <post_id>
  force_execute: true
```

### 5. Log the Action

```bash
python run_task_skill.py create -t manual \
  -d "Facebook post published: <title>" \
  -p low
python dashboard_updater.py
```

---

## Post Format Guidelines

| Element | Recommendation |
|---------|---------------|
| Length | 40–80 words for best engagement |
| Tone | Conversational, professional |
| Hashtags | 2–5 relevant hashtags at end |
| Links | OK to include |
| Emojis | 1–3 to increase visibility |

## Content Templates

### Business Achievement
```
Excited to share a milestone! [Achievement description]

Here's what made it possible:
✅ [Key factor 1]
✅ [Key factor 2]
✅ [Key factor 3]

[Call to action]

#[Industry] #[Business] #[Achievement]
```

### Weekly Recap
```
Week [N] Recap 📊

This week we:
• [Achievement 1]
• [Achievement 2]
• [Progress on goal]

Looking ahead: [next week focus]

What's your biggest business win this week? Share below! 👇
```

### Tip / Value Post
```
[Bold tip or insight]

Here's what most business owners miss about [topic]:

[3–5 detailed points]

Save this post — you'll want to refer back to it!

What's your experience with [topic]? Comment below.

#[Topic] #BusinessTips #[Industry]
```

---

## Security Rules

- NEVER post without draft → approval → publish flow
- Max 5 posts per day on this Page
- Never post customer data or financial details
- All credentials stay in `.env` — never hardcoded
- All posted content logged in `Business/Facebook_Queue/Posted/`
