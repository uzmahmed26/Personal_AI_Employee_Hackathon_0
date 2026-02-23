#!/usr/bin/env node
/**
 * Gmail MCP Server — Personal AI Employee
 *
 * Implements the Model Context Protocol (MCP) over stdio.
 * Claude Code connects to this server and can call the tools below.
 *
 * Tools:
 *   - send_email          Send an email via Gmail API
 *   - draft_email         Create a draft (HITL — does NOT send)
 *   - read_emails         Read inbox emails (filtered by query)
 *   - search_emails       Search emails with Gmail query syntax
 *   - mark_as_read        Mark a message as read
 *   - get_email_details   Get full details of a specific email
 *
 * Setup:
 *   1. Add Gmail OAuth credentials to credentials.json (Google Cloud Console)
 *   2. Set GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN in .env
 *   3. Run: node MCP_SERVERS/gmail_mcp/index.js
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { google } from "googleapis";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const VAULT_PATH = path.resolve(__dirname, "..", "..");

// ── Auth helpers ──────────────────────────────────────────────────────────────

function getOAuth2Client() {
  const clientId = process.env.GMAIL_CLIENT_ID;
  const clientSecret = process.env.GMAIL_CLIENT_SECRET;
  const refreshToken = process.env.GMAIL_REFRESH_TOKEN;
  const accessToken = process.env.GMAIL_ACCESS_TOKEN;

  if (!clientId || !clientSecret) {
    throw new Error(
      "GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET must be set in environment variables"
    );
  }

  const oAuth2Client = new google.auth.OAuth2(
    clientId,
    clientSecret,
    "http://localhost:3001/oauth/callback"
  );

  if (refreshToken) {
    oAuth2Client.setCredentials({
      refresh_token: refreshToken,
      access_token: accessToken,
    });
  } else {
    // Try loading from token.json in vault root
    const tokenPath = path.join(VAULT_PATH, "gmail_token.json");
    if (fs.existsSync(tokenPath)) {
      const token = JSON.parse(fs.readFileSync(tokenPath, "utf8"));
      oAuth2Client.setCredentials(token);
    } else {
      throw new Error(
        "No Gmail auth found. Set GMAIL_REFRESH_TOKEN or run gmail_watcher.py first to authenticate."
      );
    }
  }

  return oAuth2Client;
}

function getGmailClient() {
  const auth = getOAuth2Client();
  return google.gmail({ version: "v1", auth });
}

function decodeBase64(encoded) {
  return Buffer.from(encoded.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf8");
}

function extractEmailBody(payload) {
  if (!payload) return "";
  if (payload.body?.data) return decodeBase64(payload.body.data);
  if (payload.parts) {
    for (const part of payload.parts) {
      if (part.mimeType === "text/plain" && part.body?.data) {
        return decodeBase64(part.body.data);
      }
    }
    for (const part of payload.parts) {
      const body = extractEmailBody(part);
      if (body) return body;
    }
  }
  return "";
}

function makeRawEmail(to, subject, body, from = "", cc = "") {
  const lines = [
    `To: ${to}`,
    from ? `From: ${from}` : "",
    cc ? `Cc: ${cc}` : "",
    `Subject: ${subject}`,
    "Content-Type: text/plain; charset=utf-8",
    "MIME-Version: 1.0",
    "",
    body,
  ].filter(Boolean);
  return Buffer.from(lines.join("\r\n"))
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

// ── MCP Server ────────────────────────────────────────────────────────────────

const server = new Server(
  { name: "gmail-mcp", version: "2.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "send_email",
      description:
        "Send an email via Gmail. REQUIRES human approval for new contacts or bulk sends.",
      inputSchema: {
        type: "object",
        properties: {
          to: { type: "string", description: "Recipient email address" },
          subject: { type: "string", description: "Email subject" },
          body: { type: "string", description: "Email body (plain text)" },
          cc: { type: "string", description: "CC email addresses (optional)" },
        },
        required: ["to", "subject", "body"],
      },
    },
    {
      name: "draft_email",
      description:
        "Create a Gmail draft (does NOT send — use for HITL approval). Returns the draft ID.",
      inputSchema: {
        type: "object",
        properties: {
          to: { type: "string", description: "Recipient email address" },
          subject: { type: "string", description: "Email subject" },
          body: { type: "string", description: "Email body (plain text)" },
        },
        required: ["to", "subject", "body"],
      },
    },
    {
      name: "read_emails",
      description: "Read recent emails from Gmail inbox.",
      inputSchema: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "Gmail search query (e.g. 'is:unread is:important')",
            default: "is:unread",
          },
          max_results: {
            type: "number",
            description: "Maximum number of emails to return (default: 10)",
            default: 10,
          },
        },
      },
    },
    {
      name: "search_emails",
      description: "Search emails using Gmail query syntax.",
      inputSchema: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "Gmail search query (e.g. 'from:client@co.com invoice')",
          },
          max_results: { type: "number", default: 20 },
        },
        required: ["query"],
      },
    },
    {
      name: "get_email_details",
      description: "Get the full content of a specific email by message ID.",
      inputSchema: {
        type: "object",
        properties: {
          message_id: { type: "string", description: "Gmail message ID" },
        },
        required: ["message_id"],
      },
    },
    {
      name: "mark_as_read",
      description: "Mark an email as read.",
      inputSchema: {
        type: "object",
        properties: {
          message_id: { type: "string", description: "Gmail message ID" },
        },
        required: ["message_id"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    const gmail = getGmailClient();

    if (name === "send_email") {
      const raw = makeRawEmail(args.to, args.subject, args.body, "", args.cc || "");
      const res = await gmail.users.messages.send({
        userId: "me",
        requestBody: { raw },
      });
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: true,
              message_id: res.data.id,
              thread_id: res.data.threadId,
              message: `Email sent to ${args.to} — Subject: "${args.subject}"`,
            }),
          },
        ],
      };
    }

    if (name === "draft_email") {
      const raw = makeRawEmail(args.to, args.subject, args.body);
      const res = await gmail.users.drafts.create({
        userId: "me",
        requestBody: { message: { raw } },
      });
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: true,
              draft_id: res.data.id,
              message: `Draft created for ${args.to}. Review at Gmail drafts before sending.`,
            }),
          },
        ],
      };
    }

    if (name === "read_emails" || name === "search_emails") {
      const query = args.query || "is:unread";
      const maxResults = args.max_results || 10;

      const listRes = await gmail.users.messages.list({
        userId: "me",
        q: query,
        maxResults,
      });

      const messages = listRes.data.messages || [];
      const emails = [];

      for (const msg of messages.slice(0, maxResults)) {
        const msgRes = await gmail.users.messages.get({
          userId: "me",
          id: msg.id,
          format: "metadata",
          metadataHeaders: ["From", "To", "Subject", "Date"],
        });

        const headers = {};
        for (const h of msgRes.data.payload?.headers || []) {
          headers[h.name] = h.value;
        }

        emails.push({
          id: msg.id,
          from: headers.From || "",
          subject: headers.Subject || "(no subject)",
          date: headers.Date || "",
          snippet: msgRes.data.snippet || "",
        });
      }

      return {
        content: [{ type: "text", text: JSON.stringify({ emails, count: emails.length }) }],
      };
    }

    if (name === "get_email_details") {
      const msgRes = await gmail.users.messages.get({
        userId: "me",
        id: args.message_id,
        format: "full",
      });

      const headers = {};
      for (const h of msgRes.data.payload?.headers || []) {
        headers[h.name] = h.value;
      }

      const body = extractEmailBody(msgRes.data.payload);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              id: args.message_id,
              from: headers.From,
              to: headers.To,
              subject: headers.Subject,
              date: headers.Date,
              body: body.slice(0, 5000),
            }),
          },
        ],
      };
    }

    if (name === "mark_as_read") {
      await gmail.users.messages.modify({
        userId: "me",
        id: args.message_id,
        requestBody: { removeLabelIds: ["UNREAD"] },
      });
      return {
        content: [{ type: "text", text: JSON.stringify({ success: true, message_id: args.message_id }) }],
      };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    return {
      content: [{ type: "text", text: JSON.stringify({ error: error.message }) }],
      isError: true,
    };
  }
});

// ── Start ─────────────────────────────────────────────────────────────────────

const transport = new StdioServerTransport();
await server.connect(transport);
