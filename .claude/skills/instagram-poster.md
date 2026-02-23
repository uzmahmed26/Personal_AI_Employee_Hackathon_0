---
name: instagram-poster
description: Use this skill for any Instagram task. Trigger phrases: "Instagram post", "post on Instagram", "IG post", "Insta post", "Instagram update", "post to Instagram", "Instagram story", "Instagram insights", "IG metrics", "Instagram caption".
version: 1.0.0
---

# Instagram Poster Skill

Manages drafting, approval, and publishing of Instagram posts and stories using the Instagram Graph API MCP server. All posts follow the HITL pattern: draft → approve → publish.

## Procedure

### 1. Draft the Post

```
Use MCP tool: instagram → draft_instagram_post
  caption: <caption with hashtags (see format below)>
  media_url: <public image URL — required for actual publishing>
  title: <short description for file tracking>
```

This saves a draft to `Business/Instagram_Queue/DRAFT_*.md` and creates an approval file in `Pending_Approval/`.

> **Note:** Instagram requires an image/video URL when actually publishing. If no media URL is available, draft the caption now and add the URL at approval time.

### 2. Notify for Approval

Tell the user:
> "Instagram post drafted and waiting for your approval. Run `python approve.py list` to review. Make sure a media URL is included before approving."

### 3. After Human Approval — Publish

```
Use MCP tool: instagram → post_to_instagram
  caption: <approved caption>
  image_url: <approved image URL>
  force_execute: true
```

Instagram uses a two-step publish (container create → publish). The MCP server handles this automatically. Post is logged to `Business/Instagram_Queue/Posted/POSTED_*.md`.

### 4. Post a Story

```
Use MCP tool: instagram → post_instagram_story
  media_url: <public image or video URL>
  force_execute: true
```

Stories don't need captions but do need a media URL.

### 5. Read-Only Operations (no approval needed)

**Get recent posts:**
```
Use MCP tool: instagram → get_instagram_posts
  limit: 10
```

**Get account insights:**
```
Use MCP tool: instagram → get_instagram_insights
  type: account
  period: week
```

**Get post insights:**
```
Use MCP tool: instagram → get_instagram_insights
  type: post
  media_id: <post_id>
```

**Get comments:**
```
Use MCP tool: instagram → get_post_comments
  media_id: <post_id>
```

**Reply to a comment:**
```
Use MCP tool: instagram → reply_to_comment
  comment_id: <comment_id>
  message: <reply text>
  force_execute: true
```

### 6. Log the Action

```bash
python run_task_skill.py create -t manual \
  -d "Instagram post published: <title>" \
  -p low
python dashboard_updater.py
```

---

## Caption Format Guidelines

| Element | Recommendation |
|---------|---------------|
| Length | 125–150 chars for above-fold; max 2,200 |
| Hashtags | 20–30 hashtags at end or in first comment |
| Tone | Visual-first, storytelling, engaging |
| Line breaks | Use blank lines for readability |
| Call to action | Ask a question or invite saves/shares |
| Emojis | Liberally — break up text visually |

## Content Templates

### Achievement Post
```
[Achievement headline] ✨

[2–3 lines about the achievement or story behind it]

[Engaging question to invite comments]

#achievement #business #[industry] #milestone #growth #success #entrepreneurship #startup #[niche1] #[niche2] #[niche3] #motivation #entrepreneur #businessowner #[city] #[country] #digital #innovation #team #goals #[custom1]
```

### Product/Service Highlight
```
Introducing [product/service] 🚀

[What it does and why it matters]

[How to get it / link in bio]

#[product] #[industry] #newlaunch #[niche] #business #entrepreneur #innovation #[city] #startup #[custom1] #[custom2] #marketing #brand #growth #digital #success #quality #[custom3] #announcement #linkinbio
```

### Behind the Scenes
```
Behind the scenes of [what you're showing] 👀

[Short story or insight about the process]

What do you want to see next? Drop it in the comments 👇

#behindthescenes #[industry] #entrepreneur #business #process #team #work #[niche1] #[niche2] #motivation #hustle #startup #[city] #day #[custom1] #workflow #bts #businesslife #growth #entrepreneurship
```

---

## Hashtag Strategy

Group hashtags by size for maximum reach:

| Size | Followers | Examples |
|------|-----------|---------|
| Large (1M+) | Mass reach | #business #entrepreneur |
| Medium (100K–1M) | Targeted | #[industry] #startup |
| Small (10K–100K) | Niche | #[city]business #[niche] |
| Brand | Your own | #[YourBrandName] |

Use 5–10 from each tier for best results.

---

## Security Rules

- NEVER post without draft → approve → publish flow
- Max 3 feed posts per day; stories unlimited
- Always include a valid public image URL before publishing
- Never post personal data, financial info, or customer details
- All credentials stay in `.env` — `IG_USER_ID` + `FB_PAGE_ACCESS_TOKEN`
- All posted content logged in `Business/Instagram_Queue/Posted/`
