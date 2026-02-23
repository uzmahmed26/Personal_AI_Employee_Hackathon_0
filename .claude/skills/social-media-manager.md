---
name: social-media-manager
description: Use this skill for any social media task across Facebook, Twitter/X, or Instagram. Trigger phrases: "post to Facebook", "tweet", "Instagram post", "social media post", "post on all platforms", "share on social media", "Facebook post", "Twitter post", "Instagram update", "social media update", "cross-post", "schedule social media".
version: 1.0.0
---

# Social Media Manager Skill

Manages content creation, drafting, approval, and posting across Facebook, Twitter/X, and Instagram using their respective MCP servers. All posts follow the HITL pattern: draft → approve → publish.

## Objective

Create engaging social media content from business data, schedule posts across platforms, track engagement metrics, and generate weekly social media summaries for the CEO Briefing.

## Procedure

### 1. Determine Target Platform(s)

| User Request | Platform(s) |
|-------------|-------------|
| "post everywhere" / "all platforms" | Facebook + Twitter + Instagram |
| "Facebook" / "FB" | Facebook only |
| "tweet" / "Twitter" / "X" | Twitter only |
| "Instagram" / "IG" / "Insta" | Instagram only |
| "social media update" | All three platforms |

### 2. Generate Platform-Specific Content

Each platform has different requirements:

| Platform | Max Length | Format | Special |
|----------|-----------|--------|---------|
| Facebook | 63,206 chars | Rich text, links OK | Best: 40-80 words |
| Twitter/X | 280 chars | Short, punchy | Hashtags #3 max |
| Instagram | 2,200 chars | Visual-first | Hashtags #20-30 |

**Adapting one post for all three:**
1. Write the full version for Facebook
2. Condense to 280 chars for Twitter (key message + 1-2 hashtags)
3. Rewrite for Instagram (visual description + 20 hashtags)

### 3. Draft on All Target Platforms

**Facebook:**
```
Use MCP tool: facebook → draft_facebook_post
  content: <facebook version>
  title: <brief description>
```

**Twitter:**
```
Use MCP tool: twitter → draft_tweet
  content: <twitter version (max 280 chars)>
  title: <brief description>
```

**Instagram:**
```
Use MCP tool: instagram → draft_instagram_post
  caption: <instagram version with hashtags>
  media_url: <image URL if available>
  title: <brief description>
```

### 4. Create Single Approval Task

```bash
python run_task_skill.py create -t approval_required \
  -d "Social media posts ready for review across [platforms]" \
  -p medium --approval \
  -m platforms="facebook,twitter,instagram"
```

### 5. After Human Approval — Post to All Platforms

**Facebook:**
```
Use MCP tool: facebook → post_to_facebook
  content: <approved content>
  force_execute: true
```

**Twitter:**
```
Use MCP tool: twitter → post_tweet
  content: <approved tweet>
  force_execute: true
```

**Instagram:**
```
Use MCP tool: instagram → post_to_instagram
  caption: <approved caption>
  image_url: <approved image URL>
  force_execute: true
```

### 6. Collect Metrics (for CEO Briefing)

```
Use MCP tool: facebook → get_page_insights
  period: week

Use MCP tool: twitter → get_timeline
  max_results: 10

Use MCP tool: instagram → get_instagram_insights
  type: account
  period: week
```

### 7. Log and Update

```bash
python run_task_skill.py create -t manual \
  -d "Social media posts published on [platforms]" \
  -p low
python dashboard_updater.py
```

---

## Content Templates

### Business Achievement Post

**Facebook version:**
```
Excited to share a milestone! [Achievement description]

Here's what made it possible:
✅ [Key factor 1]
✅ [Key factor 2]
✅ [Key factor 3]

[Call to action]

#[Industry] #[Business] #[Achievement]
```

**Twitter version (≤280 chars):**
```
Just hit [achievement]! 🎯

Key to success: [one-liner insight]

[1-2 hashtags]
```

**Instagram version:**
```
[Achievement headline] ✨

[2-3 lines about the achievement]

[Engaging question for comments]

#achievement #business #[industry] #milestone #growth #success #entrepreneurship #startup #[niche1] #[niche2] #[niche3] #motivation #entrepreneur #businessowner #[city] #[country] #digital #innovation #team #goals
```

### Weekly Update Post

**Facebook:**
```
Week [N] Recap 📊

This week we:
• [Achievement 1]
• [Achievement 2]
• [Progress on goal]

Looking ahead: [next week focus]

What's your biggest business win this week? Share below! 👇
```

**Twitter:**
```
Week [N] recap:
✅ [Achievement 1]
✅ [Achievement 2]
🔄 Working on [goal]

What did you accomplish? #[Hashtag]
```

### Tip / Value Post

**Facebook:**
```
[Bold tip or insight]

Here's what most business owners miss about [topic]:

[3-5 detailed points]

Save this post — you'll want to refer back to it!

What's your experience with [topic]? Comment below.

#[Topic] #BusinessTips #[Industry]
```

**Twitter:**
```
[Topic] tip that changed how I [do X]:

[Concise 1-2 line insight]

Thread 🧵 [if longer]

#[Topic]
```

---

## Queue Folder Structure

All drafts and posted content are tracked:
```
Business/
├── Facebook_Queue/
│   ├── DRAFT_*.md          ← Pending approval
│   └── Posted/POSTED_*.md  ← Published posts
├── Twitter_Queue/
│   ├── DRAFT_*.md
│   └── Posted/POSTED_*.md
├── Instagram_Queue/
│   ├── DRAFT_*.md
│   └── Posted/POSTED_*.md
└── LinkedIn_Queue/
    ├── DRAFT_*.md
    └── Posted/POSTED_*.md
```

---

## Weekly Social Media Summary (for CEO Briefing)

When generating the CEO Briefing, collect social media data:

```
Use MCP tool: facebook → get_page_posts (limit: 7)
Use MCP tool: facebook → get_page_insights (period: week)
Use MCP tool: twitter → get_timeline (max_results: 20)
Use MCP tool: instagram → get_instagram_posts (limit: 7)
Use MCP tool: instagram → get_instagram_insights (type: account, period: week)
Use MCP tool: linkedin → get_recent_posts (count: 7)
```

Include in CEO Briefing:
- Total posts published (by platform)
- Best performing post (highest engagement)
- Follower growth this week
- Top hashtags / keywords

---

## Security Rules

- NEVER post personal information, customer data, or financial details
- NEVER post without draft → approval → publish flow
- Max posts per day: Facebook 5, Twitter 10, Instagram 3, LinkedIn 5
- All credentials stay in `.env` — never hardcoded
- All posted content logged in `Business/*/Posted/` for audit trail
