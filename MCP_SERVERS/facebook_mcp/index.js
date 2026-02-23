#!/usr/bin/env node
/**
 * Facebook MCP Server — Personal AI Employee
 *
 * Integrates with Facebook Pages via Graph API v18.
 * All posts go through HITL approval (draft first).
 *
 * Tools:
 *   - draft_facebook_post      Save draft to Business/Facebook_Queue/ (HITL)
 *   - post_to_facebook         Publish a post to Facebook Page
 *   - get_page_posts           Get recent posts from the Page
 *   - get_page_insights        Get Page engagement metrics
 *   - delete_facebook_post     Delete a post by ID (approval required)
 *   - get_post_comments        Get comments on a post
 *
 * Setup (.env):
 *   FB_PAGE_ID         — Your Facebook Page ID
 *   FB_PAGE_ACCESS_TOKEN — Long-lived Page Access Token (from Graph API Explorer)
 *   FB_APP_ID          — Facebook App ID
 *   FB_APP_SECRET      — Facebook App Secret
 *
 * Get tokens: https://developers.facebook.com/tools/explorer/
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
const FB_QUEUE = path.join(VAULT_PATH, "Business", "Facebook_Queue");
const PENDING_APPROVAL = path.join(VAULT_PATH, "Pending_Approval");
const GRAPH_API = "https://graph.facebook.com/v18.0";

function getConfig() {
  const pageId = process.env.FB_PAGE_ID;
  const token = process.env.FB_PAGE_ACCESS_TOKEN;
  if (!pageId || !token)
    throw new Error("FB_PAGE_ID and FB_PAGE_ACCESS_TOKEN must be set in .env");
  return { pageId, token };
}

function saveDraft(content, title = "") {
  fs.mkdirSync(FB_QUEUE, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const file = path.join(FB_QUEUE, `DRAFT_${ts}.md`);
  fs.writeFileSync(
    file,
    `---\nstatus: pending_approval\ncreated: ${new Date().toISOString()}\ntitle: "${title}"\nplatform: facebook\n---\n\n${content}\n`,
    "utf8"
  );
  return file;
}

function createApprovalFile(action, data) {
  fs.mkdirSync(PENDING_APPROVAL, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const file = path.join(PENDING_APPROVAL, `FB_${action.toUpperCase()}_${ts}.md`);
  fs.writeFileSync(
    file,
    `---\ntype: facebook_action\naction: ${action}\ncreated: ${new Date().toISOString()}\nstatus: pending_approval\napproved: false\n---\n\n## Facebook Action Pending Approval\n\n**Action:** ${action}\n\n\`\`\`json\n${JSON.stringify(data, null, 2)}\n\`\`\`\n\n---\nMove to \`Approved/\` or set \`approved: true\` to execute.\n`,
    "utf8"
  );
  return path.basename(file);
}

// ── MCP Server ────────────────────────────────────────────────────────────────

const server = new Server(
  { name: "facebook-mcp", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "draft_facebook_post",
      description: "Save a Facebook post draft to Business/Facebook_Queue/ for human review. ALWAYS use this before post_to_facebook.",
      inputSchema: {
        type: "object",
        properties: {
          content: { type: "string", description: "Post text (max 63,206 chars)" },
          title: { type: "string", description: "Draft title for easy identification" },
          link: { type: "string", description: "Optional URL to attach" },
        },
        required: ["content"],
      },
    },
    {
      name: "post_to_facebook",
      description: "Publish a post to your Facebook Page. Requires approval unless force_execute=true.",
      inputSchema: {
        type: "object",
        properties: {
          content: { type: "string", description: "Post text content" },
          link: { type: "string", description: "Optional URL to attach to the post" },
          force_execute: { type: "boolean", default: false, description: "Set true only after human approval" },
        },
        required: ["content"],
      },
    },
    {
      name: "get_page_posts",
      description: "Get recent posts from your Facebook Page. Read-only.",
      inputSchema: {
        type: "object",
        properties: {
          limit: { type: "number", default: 10, description: "Number of posts (max 25)" },
        },
      },
    },
    {
      name: "get_page_insights",
      description: "Get Facebook Page engagement metrics (impressions, reach, likes). Read-only.",
      inputSchema: {
        type: "object",
        properties: {
          period: { type: "string", enum: ["day", "week", "days_28"], default: "week" },
        },
      },
    },
    {
      name: "get_post_comments",
      description: "Get comments on a specific Facebook post. Read-only.",
      inputSchema: {
        type: "object",
        properties: {
          post_id: { type: "string", description: "Facebook post ID" },
          limit: { type: "number", default: 20 },
        },
        required: ["post_id"],
      },
    },
    {
      name: "delete_facebook_post",
      description: "Delete a Facebook post. Creates approval request first.",
      inputSchema: {
        type: "object",
        properties: {
          post_id: { type: "string", description: "Facebook post ID to delete" },
          force_execute: { type: "boolean", default: false },
        },
        required: ["post_id"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  try {
    const cfg = getConfig();

    if (name === "draft_facebook_post") {
      const file = saveDraft(args.content, args.title || "");
      return {
        content: [{ type: "text", text: JSON.stringify({ success: true, draft_file: file, message: "Draft saved. Review in Business/Facebook_Queue/ and approve before posting." }) }],
      };
    }

    if (name === "post_to_facebook") {
      if (!args.force_execute) {
        const approval = createApprovalFile("post", { content: args.content, link: args.link });
        return {
          content: [{ type: "text", text: JSON.stringify({ approval_required: true, approval_file: approval, message: "Post NOT published. Approval request created in Pending_Approval/." }) }],
        };
      }
      const payload = { message: args.content, access_token: cfg.token };
      if (args.link) payload.link = args.link;
      const res = await axios.post(`${GRAPH_API}/${cfg.pageId}/feed`, payload);

      // Log to Posted folder
      const postedDir = path.join(FB_QUEUE, "Posted");
      fs.mkdirSync(postedDir, { recursive: true });
      const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
      fs.writeFileSync(path.join(postedDir, `POSTED_${ts}.md`),
        `---\nstatus: posted\npost_id: ${res.data.id}\nposted_at: ${new Date().toISOString()}\nplatform: facebook\n---\n\n${args.content}\n`, "utf8");

      return {
        content: [{ type: "text", text: JSON.stringify({ success: true, post_id: res.data.id, message: `Posted to Facebook Page. ID: ${res.data.id}` }) }],
      };
    }

    if (name === "get_page_posts") {
      const res = await axios.get(`${GRAPH_API}/${cfg.pageId}/posts`, {
        params: { access_token: cfg.token, fields: "id,message,created_time,likes.summary(true),comments.summary(true)", limit: Math.min(args.limit || 10, 25) },
      });
      return { content: [{ type: "text", text: JSON.stringify(res.data) }] };
    }

    if (name === "get_page_insights") {
      const metrics = ["page_impressions", "page_reach", "page_fans", "page_post_engagements"];
      const res = await axios.get(`${GRAPH_API}/${cfg.pageId}/insights`, {
        params: { access_token: cfg.token, metric: metrics.join(","), period: args.period || "week" },
      });
      return { content: [{ type: "text", text: JSON.stringify(res.data) }] };
    }

    if (name === "get_post_comments") {
      const res = await axios.get(`${GRAPH_API}/${args.post_id}/comments`, {
        params: { access_token: cfg.token, fields: "id,message,from,created_time", limit: args.limit || 20 },
      });
      return { content: [{ type: "text", text: JSON.stringify(res.data) }] };
    }

    if (name === "delete_facebook_post") {
      if (!args.force_execute) {
        const approval = createApprovalFile("delete_post", { post_id: args.post_id });
        return {
          content: [{ type: "text", text: JSON.stringify({ approval_required: true, approval_file: approval, message: "Delete request created in Pending_Approval/." }) }],
        };
      }
      await axios.delete(`${GRAPH_API}/${args.post_id}`, { params: { access_token: cfg.token } });
      return { content: [{ type: "text", text: JSON.stringify({ success: true, message: `Post ${args.post_id} deleted.` }) }] };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    const msg = error.response?.data ? JSON.stringify(error.response.data) : error.message;
    return { content: [{ type: "text", text: JSON.stringify({ error: msg }) }], isError: true };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
