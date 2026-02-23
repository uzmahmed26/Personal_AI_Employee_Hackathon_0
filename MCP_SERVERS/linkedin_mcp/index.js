#!/usr/bin/env node
/**
 * LinkedIn MCP Server — Personal AI Employee
 *
 * Implements MCP over stdio. Allows Claude Code to:
 *   - Post content to LinkedIn feed (with HITL approval)
 *   - Create post drafts saved to Business/LinkedIn_Queue/
 *   - Read recent posts / profile info
 *
 * Tools:
 *   - post_to_linkedin        Publish a post to LinkedIn feed
 *   - draft_linkedin_post     Save a draft to LinkedIn_Queue/ (awaits approval)
 *   - get_linkedin_profile    Get your LinkedIn profile info
 *   - get_recent_posts        Get your recent LinkedIn posts
 *
 * Setup:
 *   Set LINKEDIN_ACCESS_TOKEN in .env
 *   (Get token via: python linkedin_poster_improved.py)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const VAULT_PATH = path.resolve(__dirname, "..", "..");
const LINKEDIN_QUEUE = path.join(VAULT_PATH, "Business", "LinkedIn_Queue");

const LINKEDIN_API = "https://api.linkedin.com/v2";

function getHeaders() {
  const token = process.env.LINKEDIN_ACCESS_TOKEN;
  if (!token) throw new Error("LINKEDIN_ACCESS_TOKEN not set in environment");
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
  };
}

async function getPersonUrn() {
  const res = await axios.get(`${LINKEDIN_API}/me`, { headers: getHeaders() });
  return `urn:li:person:${res.data.id}`;
}

function saveDraftToQueue(content, title = "") {
  fs.mkdirSync(LINKEDIN_QUEUE, { recursive: true });
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const filename = `DRAFT_${timestamp}.md`;
  const filepath = path.join(LINKEDIN_QUEUE, filename);

  const md = `---\nstatus: pending_approval\ncreated: ${new Date().toISOString()}\ntitle: "${title}"\n---\n\n${content}\n`;
  fs.writeFileSync(filepath, md, "utf8");
  return filepath;
}

// ── MCP Server ────────────────────────────────────────────────────────────────

const server = new Server(
  { name: "linkedin-mcp", version: "2.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "post_to_linkedin",
      description:
        "Publish a text post to LinkedIn feed. REQUIRES human approval — prefer draft_linkedin_post first unless already approved.",
      inputSchema: {
        type: "object",
        properties: {
          content: {
            type: "string",
            description: "Post text content (max 3000 chars recommended)",
          },
          visibility: {
            type: "string",
            enum: ["PUBLIC", "CONNECTIONS"],
            description: "Post visibility (default: PUBLIC)",
            default: "PUBLIC",
          },
        },
        required: ["content"],
      },
    },
    {
      name: "draft_linkedin_post",
      description:
        "Save a LinkedIn post draft to Business/LinkedIn_Queue/ for human review and approval. Use this BEFORE posting.",
      inputSchema: {
        type: "object",
        properties: {
          content: {
            type: "string",
            description: "Post text content",
          },
          title: {
            type: "string",
            description: "Draft title for easy identification",
          },
        },
        required: ["content"],
      },
    },
    {
      name: "get_linkedin_profile",
      description: "Get your LinkedIn profile information.",
      inputSchema: { type: "object", properties: {} },
    },
    {
      name: "get_recent_posts",
      description: "Get your recent LinkedIn posts (last 10).",
      inputSchema: {
        type: "object",
        properties: {
          count: {
            type: "number",
            description: "Number of posts to retrieve (default: 10)",
            default: 10,
          },
        },
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === "draft_linkedin_post") {
      const filepath = saveDraftToQueue(args.content, args.title || "");
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: true,
              draft_saved_to: filepath,
              message:
                "Draft saved to LinkedIn_Queue/. Review and approve by moving to Approved/ or setting approved: true.",
            }),
          },
        ],
      };
    }

    if (name === "post_to_linkedin") {
      const personUrn = await getPersonUrn();
      const payload = {
        author: personUrn,
        lifecycleState: "PUBLISHED",
        specificContent: {
          "com.linkedin.ugc.ShareContent": {
            shareCommentary: { text: args.content },
            shareMediaCategory: "NONE",
          },
        },
        visibility: {
          "com.linkedin.ugc.MemberNetworkVisibility": args.visibility || "PUBLIC",
        },
      };

      const res = await axios.post(`${LINKEDIN_API}/ugcPosts`, payload, {
        headers: getHeaders(),
      });

      // Log the posted content to the Posted folder
      const postedDir = path.join(LINKEDIN_QUEUE, "Posted");
      fs.mkdirSync(postedDir, { recursive: true });
      const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
      fs.writeFileSync(
        path.join(postedDir, `POSTED_${ts}.md`),
        `---\nstatus: posted\npost_id: ${res.data.id}\nposted_at: ${new Date().toISOString()}\n---\n\n${args.content}\n`,
        "utf8"
      );

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: true,
              post_id: res.data.id,
              message: `Post published to LinkedIn. ID: ${res.data.id}`,
            }),
          },
        ],
      };
    }

    if (name === "get_linkedin_profile") {
      const res = await axios.get(
        `${LINKEDIN_API}/me?projection=(id,localizedFirstName,localizedLastName,profilePicture)`,
        { headers: getHeaders() }
      );
      return {
        content: [{ type: "text", text: JSON.stringify(res.data) }],
      };
    }

    if (name === "get_recent_posts") {
      const personUrn = await getPersonUrn();
      const encodedUrn = encodeURIComponent(personUrn);
      const res = await axios.get(
        `${LINKEDIN_API}/ugcPosts?q=authors&authors=List(${encodedUrn})&count=${args.count || 10}`,
        { headers: getHeaders() }
      );
      return {
        content: [{ type: "text", text: JSON.stringify(res.data) }],
      };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    const msg = error.response?.data
      ? JSON.stringify(error.response.data)
      : error.message;
    return {
      content: [{ type: "text", text: JSON.stringify({ error: msg }) }],
      isError: true,
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
