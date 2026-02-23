#!/usr/bin/env node
/**
 * Twitter/X MCP Server — Personal AI Employee
 *
 * Integrates with Twitter API v2 (OAuth 1.0a for posting, Bearer Token for reading).
 * All posts require HITL approval.
 *
 * Tools:
 *   - draft_tweet          Save tweet draft to Business/Twitter_Queue/
 *   - post_tweet           Post a tweet (approval required)
 *   - get_timeline         Get your recent tweets
 *   - search_tweets        Search recent tweets by keyword
 *   - get_tweet            Get a specific tweet by ID
 *   - delete_tweet         Delete a tweet (approval required)
 *   - get_tweet_metrics    Get engagement metrics for a tweet
 *
 * Setup (.env):
 *   TWITTER_API_KEY             — API Key (Consumer Key)
 *   TWITTER_API_SECRET          — API Secret (Consumer Secret)
 *   TWITTER_ACCESS_TOKEN        — Access Token (your account)
 *   TWITTER_ACCESS_TOKEN_SECRET — Access Token Secret
 *   TWITTER_BEARER_TOKEN        — Bearer Token (for read-only endpoints)
 *   TWITTER_USER_ID             — Your Twitter user ID (for timeline)
 *
 * Get tokens: https://developer.twitter.com/en/portal/dashboard
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";
import crypto from "crypto";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const VAULT_PATH = path.resolve(__dirname, "..", "..");
const TW_QUEUE = path.join(VAULT_PATH, "Business", "Twitter_Queue");
const PENDING_APPROVAL = path.join(VAULT_PATH, "Pending_Approval");

// ── OAuth 1.0a helpers ────────────────────────────────────────────────────────

function getOAuthConfig() {
  const apiKey = process.env.TWITTER_API_KEY;
  const apiSecret = process.env.TWITTER_API_SECRET;
  const accessToken = process.env.TWITTER_ACCESS_TOKEN;
  const accessSecret = process.env.TWITTER_ACCESS_TOKEN_SECRET;
  const bearerToken = process.env.TWITTER_BEARER_TOKEN;
  if (!apiKey || !apiSecret || !accessToken || !accessSecret)
    throw new Error("TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET must be set in .env");
  return { apiKey, apiSecret, accessToken, accessSecret, bearerToken };
}

function buildOAuthHeader(method, url, params, cfg) {
  const oauthParams = {
    oauth_consumer_key: cfg.apiKey,
    oauth_nonce: crypto.randomBytes(16).toString("hex"),
    oauth_signature_method: "HMAC-SHA1",
    oauth_timestamp: Math.floor(Date.now() / 1000).toString(),
    oauth_token: cfg.accessToken,
    oauth_version: "1.0",
  };

  const allParams = { ...params, ...oauthParams };
  const sortedParams = Object.keys(allParams).sort().map(k =>
    `${encodeURIComponent(k)}=${encodeURIComponent(allParams[k])}`
  ).join("&");

  const signatureBase = `${method.toUpperCase()}&${encodeURIComponent(url)}&${encodeURIComponent(sortedParams)}`;
  const signingKey = `${encodeURIComponent(cfg.apiSecret)}&${encodeURIComponent(cfg.accessSecret)}`;
  const signature = crypto.createHmac("sha1", signingKey).update(signatureBase).digest("base64");
  oauthParams.oauth_signature = signature;

  const authHeader = "OAuth " + Object.keys(oauthParams).sort().map(k =>
    `${encodeURIComponent(k)}="${encodeURIComponent(oauthParams[k])}"`
  ).join(", ");

  return authHeader;
}

async function twitterPost(endpoint, body) {
  const cfg = getOAuthConfig();
  const url = `https://api.twitter.com/2${endpoint}`;
  const authHeader = buildOAuthHeader("POST", url, {}, cfg);
  const res = await axios.post(url, body, {
    headers: { Authorization: authHeader, "Content-Type": "application/json" },
  });
  return res.data;
}

async function twitterGet(endpoint, params = {}) {
  const cfg = getOAuthConfig();
  const bearerToken = cfg.bearerToken;
  const url = `https://api.twitter.com/2${endpoint}`;

  if (bearerToken) {
    // Use Bearer Token for read-only endpoints (simpler)
    const res = await axios.get(url, {
      params,
      headers: { Authorization: `Bearer ${bearerToken}` },
    });
    return res.data;
  }

  // Fallback to OAuth 1.0a
  const authHeader = buildOAuthHeader("GET", url, params, cfg);
  const res = await axios.get(url, {
    params,
    headers: { Authorization: authHeader },
  });
  return res.data;
}

async function twitterDelete(endpoint) {
  const cfg = getOAuthConfig();
  const url = `https://api.twitter.com/2${endpoint}`;
  const authHeader = buildOAuthHeader("DELETE", url, {}, cfg);
  const res = await axios.delete(url, { headers: { Authorization: authHeader } });
  return res.data;
}

function saveDraft(content, title = "") {
  fs.mkdirSync(TW_QUEUE, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const file = path.join(TW_QUEUE, `DRAFT_${ts}.md`);
  fs.writeFileSync(file,
    `---\nstatus: pending_approval\ncreated: ${new Date().toISOString()}\ntitle: "${title}"\nplatform: twitter\nchar_count: ${content.length}\n---\n\n${content}\n`, "utf8");
  return file;
}

function createApprovalFile(action, data) {
  fs.mkdirSync(PENDING_APPROVAL, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const file = path.join(PENDING_APPROVAL, `TWITTER_${action.toUpperCase()}_${ts}.md`);
  fs.writeFileSync(file,
    `---\ntype: twitter_action\naction: ${action}\ncreated: ${new Date().toISOString()}\nstatus: pending_approval\napproved: false\n---\n\n## Twitter Action Pending Approval\n\n**Action:** ${action}\n\n\`\`\`json\n${JSON.stringify(data, null, 2)}\n\`\`\`\n\n---\nMove to \`Approved/\` or set \`approved: true\` to execute.\n`,
    "utf8");
  return path.basename(file);
}

// ── MCP Server ────────────────────────────────────────────────────────────────

const server = new Server(
  { name: "twitter-mcp", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "draft_tweet",
      description: "Save a tweet draft to Business/Twitter_Queue/ for human review. ALWAYS use before post_tweet.",
      inputSchema: {
        type: "object",
        properties: {
          content: { type: "string", description: "Tweet text (max 280 chars)" },
          title: { type: "string", description: "Draft title" },
          reply_to_id: { type: "string", description: "Tweet ID to reply to (optional)" },
        },
        required: ["content"],
      },
    },
    {
      name: "post_tweet",
      description: "Post a tweet to Twitter/X. Requires approval unless force_execute=true.",
      inputSchema: {
        type: "object",
        properties: {
          content: { type: "string", description: "Tweet text (max 280 chars)" },
          reply_to_id: { type: "string", description: "Tweet ID to reply to (for threads)" },
          force_execute: { type: "boolean", default: false },
        },
        required: ["content"],
      },
    },
    {
      name: "get_timeline",
      description: "Get your recent tweets. Read-only.",
      inputSchema: {
        type: "object",
        properties: {
          max_results: { type: "number", default: 10, description: "Number of tweets (5-100)" },
        },
      },
    },
    {
      name: "search_tweets",
      description: "Search recent tweets by keyword or hashtag. Read-only.",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string", description: "Search query (e.g. '#AI -is:retweet')" },
          max_results: { type: "number", default: 10 },
        },
        required: ["query"],
      },
    },
    {
      name: "get_tweet",
      description: "Get details of a specific tweet by ID. Read-only.",
      inputSchema: {
        type: "object",
        properties: {
          tweet_id: { type: "string" },
        },
        required: ["tweet_id"],
      },
    },
    {
      name: "get_tweet_metrics",
      description: "Get engagement metrics (likes, retweets, replies, impressions) for a tweet. Read-only.",
      inputSchema: {
        type: "object",
        properties: {
          tweet_id: { type: "string" },
        },
        required: ["tweet_id"],
      },
    },
    {
      name: "delete_tweet",
      description: "Delete a tweet. Creates approval request first.",
      inputSchema: {
        type: "object",
        properties: {
          tweet_id: { type: "string" },
          force_execute: { type: "boolean", default: false },
        },
        required: ["tweet_id"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  try {
    if (name === "draft_tweet") {
      if (args.content && args.content.length > 280)
        return { content: [{ type: "text", text: JSON.stringify({ error: `Tweet too long: ${args.content.length}/280 chars. Please shorten.` }) }], isError: true };
      const file = saveDraft(args.content, args.title || "");
      return { content: [{ type: "text", text: JSON.stringify({ success: true, draft_file: file, char_count: args.content.length, message: "Draft saved. Review in Business/Twitter_Queue/ then approve." }) }] };
    }

    if (name === "post_tweet") {
      if (args.content && args.content.length > 280)
        return { content: [{ type: "text", text: JSON.stringify({ error: `Tweet too long: ${args.content.length}/280 chars.` }) }], isError: true };

      if (!args.force_execute) {
        const approval = createApprovalFile("tweet", { content: args.content, reply_to_id: args.reply_to_id });
        return { content: [{ type: "text", text: JSON.stringify({ approval_required: true, approval_file: approval, message: "Tweet NOT posted. Approval request created." }) }] };
      }

      const body = { text: args.content };
      if (args.reply_to_id) body.reply = { in_reply_to_tweet_id: args.reply_to_id };
      const data = await twitterPost("/tweets", body);

      // Log to Posted folder
      const postedDir = path.join(TW_QUEUE, "Posted");
      fs.mkdirSync(postedDir, { recursive: true });
      const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
      fs.writeFileSync(path.join(postedDir, `POSTED_${ts}.md`),
        `---\nstatus: posted\ntweet_id: ${data.data?.id}\nposted_at: ${new Date().toISOString()}\nplatform: twitter\n---\n\n${args.content}\n`, "utf8");

      return { content: [{ type: "text", text: JSON.stringify({ success: true, tweet_id: data.data?.id, message: `Tweet posted. ID: ${data.data?.id}` }) }] };
    }

    if (name === "get_timeline") {
      const userId = process.env.TWITTER_USER_ID;
      if (!userId) throw new Error("TWITTER_USER_ID must be set in .env");
      const data = await twitterGet(`/users/${userId}/tweets`, {
        max_results: Math.min(Math.max(args.max_results || 10, 5), 100),
        "tweet.fields": "created_at,public_metrics,text",
      });
      return { content: [{ type: "text", text: JSON.stringify(data) }] };
    }

    if (name === "search_tweets") {
      const data = await twitterGet("/tweets/search/recent", {
        query: args.query,
        max_results: Math.min(Math.max(args.max_results || 10, 10), 100),
        "tweet.fields": "created_at,public_metrics,author_id,text",
      });
      return { content: [{ type: "text", text: JSON.stringify(data) }] };
    }

    if (name === "get_tweet") {
      const data = await twitterGet(`/tweets/${args.tweet_id}`, {
        "tweet.fields": "created_at,public_metrics,author_id,text,conversation_id",
      });
      return { content: [{ type: "text", text: JSON.stringify(data) }] };
    }

    if (name === "get_tweet_metrics") {
      const data = await twitterGet(`/tweets/${args.tweet_id}`, {
        "tweet.fields": "public_metrics,non_public_metrics,organic_metrics",
      });
      return { content: [{ type: "text", text: JSON.stringify(data) }] };
    }

    if (name === "delete_tweet") {
      if (!args.force_execute) {
        const approval = createApprovalFile("delete_tweet", { tweet_id: args.tweet_id });
        return { content: [{ type: "text", text: JSON.stringify({ approval_required: true, approval_file: approval, message: "Delete request created in Pending_Approval/." }) }] };
      }
      const data = await twitterDelete(`/tweets/${args.tweet_id}`);
      return { content: [{ type: "text", text: JSON.stringify({ success: true, deleted: data.data?.deleted }) }] };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    const msg = error.response?.data ? JSON.stringify(error.response.data) : error.message;
    return { content: [{ type: "text", text: JSON.stringify({ error: msg }) }], isError: true };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
