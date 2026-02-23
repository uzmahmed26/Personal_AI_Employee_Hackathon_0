#!/usr/bin/env node
/**
 * Instagram MCP Server — Personal AI Employee
 *
 * Integrates with Instagram Business / Creator accounts via Instagram Graph API.
 * Uses the same Facebook Page Access Token (Instagram must be linked to a Facebook Page).
 * All posts go through HITL approval.
 *
 * Tools:
 *   - draft_instagram_post    Save post draft to Business/Instagram_Queue/
 *   - post_to_instagram       Publish a photo/video post to Instagram
 *   - post_instagram_story    Publish a Story (image URL required)
 *   - get_instagram_posts     Get recent posts from your Instagram account
 *   - get_instagram_insights  Get account/post engagement metrics
 *   - get_post_comments       Get comments on a specific post
 *   - reply_to_comment        Reply to an Instagram comment (approval required)
 *
 * Setup (.env):
 *   IG_USER_ID              — Instagram Business Account ID
 *   FB_PAGE_ACCESS_TOKEN    — Facebook Page Access Token (linked to Instagram)
 *
 * Get IG User ID:
 *   https://graph.facebook.com/v18.0/me/accounts?access_token=<token>
 *   Then: https://graph.facebook.com/v18.0/<page-id>?fields=instagram_business_account&access_token=<token>
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const VAULT_PATH = path.resolve(__dirname, "..", "..");
const IG_QUEUE = path.join(VAULT_PATH, "Business", "Instagram_Queue");
const PENDING_APPROVAL = path.join(VAULT_PATH, "Pending_Approval");
const GRAPH_API = "https://graph.facebook.com/v18.0";

function getConfig() {
  const igUserId = process.env.IG_USER_ID;
  const token = process.env.FB_PAGE_ACCESS_TOKEN;
  if (!igUserId || !token)
    throw new Error("IG_USER_ID and FB_PAGE_ACCESS_TOKEN must be set in .env");
  return { igUserId, token };
}

function saveDraft(content, mediaUrl = "", title = "") {
  fs.mkdirSync(IG_QUEUE, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const file = path.join(IG_QUEUE, `DRAFT_${ts}.md`);
  fs.writeFileSync(file,
    `---\nstatus: pending_approval\ncreated: ${new Date().toISOString()}\ntitle: "${title}"\nplatform: instagram\nmedia_url: "${mediaUrl}"\n---\n\n${content}\n`, "utf8");
  return file;
}

function createApprovalFile(action, data) {
  fs.mkdirSync(PENDING_APPROVAL, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const file = path.join(PENDING_APPROVAL, `IG_${action.toUpperCase()}_${ts}.md`);
  fs.writeFileSync(file,
    `---\ntype: instagram_action\naction: ${action}\ncreated: ${new Date().toISOString()}\nstatus: pending_approval\napproved: false\n---\n\n## Instagram Action Pending Approval\n\n**Action:** ${action}\n\n\`\`\`json\n${JSON.stringify(data, null, 2)}\n\`\`\`\n\n---\nMove to \`Approved/\` or set \`approved: true\` to execute.\n`,
    "utf8");
  return path.basename(file);
}

// ── Two-step Instagram publish: create container → publish ────────────────────

async function createMediaContainer(cfg, imageUrl, caption, isStory = false) {
  const params = {
    access_token: cfg.token,
    caption,
    image_url: imageUrl,
  };
  if (isStory) params.media_type = "IMAGE";

  const res = await axios.post(`${GRAPH_API}/${cfg.igUserId}/media`, null, { params });
  return res.data.id; // creation_id
}

async function publishContainer(cfg, creationId) {
  const res = await axios.post(`${GRAPH_API}/${cfg.igUserId}/media_publish`, null, {
    params: { access_token: cfg.token, creation_id: creationId },
  });
  return res.data.id; // post_id
}

// ── MCP Server ────────────────────────────────────────────────────────────────

const server = new Server(
  { name: "instagram-mcp", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "draft_instagram_post",
      description: "Save an Instagram post draft to Business/Instagram_Queue/ for human review. ALWAYS use before post_to_instagram.",
      inputSchema: {
        type: "object",
        properties: {
          caption: { type: "string", description: "Post caption with hashtags (max 2200 chars)" },
          media_url: { type: "string", description: "Publicly accessible URL of the image or video" },
          title: { type: "string", description: "Draft title" },
        },
        required: ["caption"],
      },
    },
    {
      name: "post_to_instagram",
      description: "Publish a photo post to Instagram. Requires a public image URL. Approval required unless force_execute=true.",
      inputSchema: {
        type: "object",
        properties: {
          caption: { type: "string", description: "Post caption with hashtags" },
          image_url: { type: "string", description: "Publicly accessible image URL (JPEG/PNG)" },
          force_execute: { type: "boolean", default: false },
        },
        required: ["caption", "image_url"],
      },
    },
    {
      name: "post_instagram_story",
      description: "Publish an image Story to Instagram. Approval required unless force_execute=true.",
      inputSchema: {
        type: "object",
        properties: {
          image_url: { type: "string", description: "Publicly accessible image URL for the Story" },
          force_execute: { type: "boolean", default: false },
        },
        required: ["image_url"],
      },
    },
    {
      name: "get_instagram_posts",
      description: "Get recent Instagram posts from your account. Read-only.",
      inputSchema: {
        type: "object",
        properties: {
          limit: { type: "number", default: 10, description: "Number of posts (max 25)" },
        },
      },
    },
    {
      name: "get_instagram_insights",
      description: "Get Instagram account or post engagement metrics. Read-only.",
      inputSchema: {
        type: "object",
        properties: {
          type: { type: "string", enum: ["account", "post"], default: "account" },
          post_id: { type: "string", description: "Required if type=post" },
          period: { type: "string", enum: ["day", "week", "month"], default: "week" },
        },
      },
    },
    {
      name: "get_post_comments",
      description: "Get comments on a specific Instagram post. Read-only.",
      inputSchema: {
        type: "object",
        properties: {
          post_id: { type: "string", description: "Instagram post ID" },
          limit: { type: "number", default: 20 },
        },
        required: ["post_id"],
      },
    },
    {
      name: "reply_to_comment",
      description: "Reply to an Instagram comment. Creates approval request first.",
      inputSchema: {
        type: "object",
        properties: {
          comment_id: { type: "string" },
          message: { type: "string" },
          force_execute: { type: "boolean", default: false },
        },
        required: ["comment_id", "message"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  try {
    const cfg = getConfig();

    if (name === "draft_instagram_post") {
      const file = saveDraft(args.caption, args.media_url || "", args.title || "");
      return { content: [{ type: "text", text: JSON.stringify({ success: true, draft_file: file, message: "Draft saved to Business/Instagram_Queue/. Approve before posting." }) }] };
    }

    if (name === "post_to_instagram") {
      if (!args.force_execute) {
        const approval = createApprovalFile("post", { caption: args.caption, image_url: args.image_url });
        return { content: [{ type: "text", text: JSON.stringify({ approval_required: true, approval_file: approval, message: "Post NOT published. Approval request created." }) }] };
      }
      const creationId = await createMediaContainer(cfg, args.image_url, args.caption);
      // Wait for container to be ready (Instagram requires brief delay)
      await new Promise(r => setTimeout(r, 3000));
      const postId = await publishContainer(cfg, creationId);

      const postedDir = path.join(IG_QUEUE, "Posted");
      fs.mkdirSync(postedDir, { recursive: true });
      const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
      fs.writeFileSync(path.join(postedDir, `POSTED_${ts}.md`),
        `---\nstatus: posted\npost_id: ${postId}\nposted_at: ${new Date().toISOString()}\nimage_url: ${args.image_url}\nplatform: instagram\n---\n\n${args.caption}\n`, "utf8");

      return { content: [{ type: "text", text: JSON.stringify({ success: true, post_id: postId, message: `Published to Instagram. Post ID: ${postId}` }) }] };
    }

    if (name === "post_instagram_story") {
      if (!args.force_execute) {
        const approval = createApprovalFile("story", { image_url: args.image_url });
        return { content: [{ type: "text", text: JSON.stringify({ approval_required: true, approval_file: approval, message: "Story NOT published. Approval request created." }) }] };
      }
      const creationId = await createMediaContainer(cfg, args.image_url, "", true);
      await new Promise(r => setTimeout(r, 3000));
      const postId = await publishContainer(cfg, creationId);
      return { content: [{ type: "text", text: JSON.stringify({ success: true, post_id: postId, message: `Story published to Instagram. ID: ${postId}` }) }] };
    }

    if (name === "get_instagram_posts") {
      const res = await axios.get(`${GRAPH_API}/${cfg.igUserId}/media`, {
        params: {
          access_token: cfg.token,
          fields: "id,caption,media_type,media_url,thumbnail_url,timestamp,like_count,comments_count",
          limit: Math.min(args.limit || 10, 25),
        },
      });
      return { content: [{ type: "text", text: JSON.stringify(res.data) }] };
    }

    if (name === "get_instagram_insights") {
      if (args.type === "post" && args.post_id) {
        const res = await axios.get(`${GRAPH_API}/${args.post_id}/insights`, {
          params: { access_token: cfg.token, metric: "impressions,reach,likes,comments,shares,saved" },
        });
        return { content: [{ type: "text", text: JSON.stringify(res.data) }] };
      }
      // Account-level insights
      const res = await axios.get(`${GRAPH_API}/${cfg.igUserId}/insights`, {
        params: {
          access_token: cfg.token,
          metric: "impressions,reach,follower_count,profile_views",
          period: args.period || "week",
        },
      });
      return { content: [{ type: "text", text: JSON.stringify(res.data) }] };
    }

    if (name === "get_post_comments") {
      const res = await axios.get(`${GRAPH_API}/${args.post_id}/comments`, {
        params: {
          access_token: cfg.token,
          fields: "id,text,username,timestamp",
          limit: args.limit || 20,
        },
      });
      return { content: [{ type: "text", text: JSON.stringify(res.data) }] };
    }

    if (name === "reply_to_comment") {
      if (!args.force_execute) {
        const approval = createApprovalFile("reply_comment", { comment_id: args.comment_id, message: args.message });
        return { content: [{ type: "text", text: JSON.stringify({ approval_required: true, approval_file: approval, message: "Reply request created in Pending_Approval/." }) }] };
      }
      const res = await axios.post(`${GRAPH_API}/${args.comment_id}/replies`, null, {
        params: { access_token: cfg.token, message: args.message },
      });
      return { content: [{ type: "text", text: JSON.stringify({ success: true, reply_id: res.data.id }) }] };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    const msg = error.response?.data ? JSON.stringify(error.response.data) : error.message;
    return { content: [{ type: "text", text: JSON.stringify({ error: msg }) }], isError: true };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
