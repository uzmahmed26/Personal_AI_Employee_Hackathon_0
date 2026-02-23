---
name: linkedin-poster
description: Use this skill when the user wants to post content to LinkedIn, schedule a LinkedIn post, draft a LinkedIn update, share business news on LinkedIn, or generate a LinkedIn post from business data. Trigger phrases: "post to LinkedIn", "LinkedIn post", "share on LinkedIn", "draft LinkedIn", "LinkedIn update", "publish LinkedIn", "post about our business".
version: 1.0.0
---

# LinkedIn Poster Skill

Autonomously creates, drafts, and publishes LinkedIn posts to generate business sales and visibility. All posts go through a HITL approval step before publishing.

## Objective

Generate engaging LinkedIn content from business data (completed tasks, business goals, CEO briefing) and post to LinkedIn using the LinkedIn MCP server.

## Procedure

### 1. Gather Content Context

Read business context:
```bash
# Read business goals and recent activity
cat Business_Goals.md
cat Dashboard.md
# Check any existing LinkedIn drafts
ls Business/LinkedIn_Queue/
```

### 2. Generate Post Content

Create a LinkedIn post that:
- Highlights a business achievement, insight, or value proposition
- Is professional and engaging (150-500 words ideal)
- Includes relevant hashtags (3-5 max)
- Has a clear call-to-action if appropriate
- Aligns with Company_Handbook.md tone guidelines

**Post types by trigger:**
| Trigger | Post Type |
|---------|-----------|
| Business milestone | Achievement post with metrics |
| New week/Monday | Goal-setting or insight post |
| Completed project | Case study / results post |
| Industry news | Thought leadership post |
| General | Value-adding tip or insight |

### 3. Create Draft First (ALWAYS)

ALWAYS save a draft before posting:
```
Use MCP tool: linkedin → draft_linkedin_post
  content: <generated post text>
  title: <brief description>
```

The draft is saved to `Business/LinkedIn_Queue/DRAFT_<timestamp>.md`.

### 4. Create Task for Approval

```bash
python run_task_skill.py create -t linkedin \
  -d "LinkedIn post draft ready for review and approval" \
  -p medium --approval \
  -m draft_file="Business/LinkedIn_Queue/DRAFT_<timestamp>.md"
```

### 5. After Human Approval

When user approves (moves file to Approved/ or sets `approved: true`):

```
Use MCP tool: linkedin → post_to_linkedin
  content: <approved post content>
  visibility: PUBLIC
```

### 6. Log and Update Dashboard

```bash
python run_task_skill.py create -t linkedin \
  -d "LinkedIn post published successfully" \
  -p low
python dashboard_updater.py
```

## Content Templates

### Achievement Post
```
[Achievement] We just [accomplished X] and here's what we learned...

Key takeaways:
• [Insight 1]
• [Insight 2]
• [Insight 3]

[Call to action / question for engagement]

#[Hashtag1] #[Hashtag2] #[Hashtag3]
```

### Weekly Update Post
```
Week [N] update from [Company/Role]:

This week we focused on [focus area]:
✅ [Achievement 1]
✅ [Achievement 2]
🔄 [In progress]

What's your biggest win this week?

#[Hashtag1] #[Hashtag2]
```

### Value/Tip Post
```
[Bold statement or question]

Here's what most people don't know about [topic]:

[3-5 bullet points with value]

Save this post if you found it useful.

#[Hashtag1] #[Hashtag2] #[Hashtag3]
```

## Security Rules

- NEVER post directly without going through `draft_linkedin_post` first
- NEVER post personal information, financial details, or client names without approval
- Maximum 5 posts per day (rate limit in LinkedIn MCP config)
- Always log posted content to `Business/LinkedIn_Queue/Posted/`
