---
name: twitter-poster
description: Use this skill for any Twitter/X task. Trigger phrases: "tweet", "post a tweet", "Twitter post", "post on Twitter", "post on X", "Twitter update", "X post", "search tweets", "get timeline", "Twitter metrics", "delete tweet".
version: 1.0.0
---

# Twitter Poster Skill

Manages drafting, approval, and publishing of tweets using the Twitter API v2 MCP server. All posts follow the HITL pattern: draft → approve → publish.

## Procedure

### 1. Draft the Tweet

```
Use MCP tool: twitter → draft_tweet
  content: <tweet text (max 280 characters — STRICTLY enforced)>
  title: <short description for file tracking>
```

This saves a draft to `Business/Twitter_Queue/DRAFT_*.md` and creates an approval file in `Pending_Approval/`.

**Important:** Always count characters before drafting. If content exceeds 280 chars, condense it.

### 2. Notify for Approval

Tell the user:
> "Tweet drafted ([N] chars) and waiting for your approval. Run `python approve.py list` to review."

### 3. After Human Approval — Post

```
Use MCP tool: twitter → post_tweet
  content: <approved tweet text>
  force_execute: true
```

Tweet is published and logged to `Business/Twitter_Queue/Posted/POSTED_*.md`.

### 4. Read-Only Operations (no approval needed)

**Get your timeline:**
```
Use MCP tool: twitter → get_timeline
  max_results: 10
```

**Search tweets:**
```
Use MCP tool: twitter → search_tweets
  query: <search query>
  max_results: 20
```

**Get a specific tweet:**
```
Use MCP tool: twitter → get_tweet
  tweet_id: <tweet_id>
```

**Get tweet engagement metrics:**
```
Use MCP tool: twitter → get_tweet_metrics
  tweet_id: <tweet_id>
```

**Delete a tweet:**
```
Use MCP tool: twitter → delete_tweet
  tweet_id: <tweet_id>
  force_execute: true
```

### 5. Log the Action

```bash
python run_task_skill.py create -t manual \
  -d "Tweet published: <title>" \
  -p low
python dashboard_updater.py
```

---

## Tweet Format Guidelines

| Element | Rule |
|---------|------|
| Length | **Max 280 characters** (hard limit) |
| Hashtags | Max 2–3 (more reduces engagement) |
| Tone | Short, punchy, direct |
| Links | Count as ~23 chars (Twitter shortens URLs) |
| Emojis | 1–2 max, use purposefully |

## Content Templates

### Announcement (short)
```
Just [achieved/launched/completed] [thing]! 🎯

Key insight: [one-liner]

#[Hashtag1] #[Hashtag2]
```
*(Keep under 200 chars to leave room for replies/retweets)*

### Weekly Recap
```
Week [N] recap:
✅ [Achievement 1]
✅ [Achievement 2]
🔄 Working on [goal]

What did you accomplish? #[Hashtag]
```

### Tip Post
```
[Topic] tip that changed how I [do X]:

[Concise 1–2 line insight]

#[Topic]
```

### Thread Starter
```
[Hook statement that makes people want to read more]

Thread 🧵👇
```
*(Follow with numbered replies: "1/ ...", "2/ ...")*

---

## Character Count Helper

When drafting, estimate length:
- Plain text: count characters directly
- A URL: ~23 chars (regardless of actual URL length)
- An @mention: counts as written
- Emoji: usually 2 chars each

---

## Security Rules

- NEVER post without draft → approval → publish flow
- Max 10 tweets per day
- 280 character limit strictly enforced at draft stage
- Never post sensitive business or customer data
- All credentials (API key, secret, tokens) stay in `.env`
- All posted content logged in `Business/Twitter_Queue/Posted/`
