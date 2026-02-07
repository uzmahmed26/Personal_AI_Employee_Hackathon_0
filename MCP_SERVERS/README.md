# MCP Servers for Personal AI Employee

This directory contains the Model Context Protocol (MCP) server configurations for your Personal AI Employee. Each server enables Claude Code to interact with external systems.

## Server Overview

### 1. File System MCP
- Handles file operations within your Obsidian vault
- Manages reading, writing, moving, and deleting files
- Enforces security boundaries to prevent unauthorized access
- Built into Claude Code runtime (no separate server required)

### 2. Gmail MCP
- Enables email sending, reading, and searching
- Integrates with Gmail API for secure email operations
- Implements approval workflows for sensitive emails
- Requires OAuth 2.0 authentication

### 3. WhatsApp MCP
- Facilitates WhatsApp messaging through Meta Business API
- Enables sending messages, media, and checking status
- Requires Meta Business API credentials
- Includes webhook support for receiving messages

### 4. LinkedIn MCP
- Allows posting updates and managing connections
- Handles social media engagement for business purposes
- Implements rate limiting and approval requirements
- Requires LinkedIn OAuth authentication

### 5. Context 7 MCP
- Provides advanced context analysis and data retrieval
- Processes information from external knowledge bases
- Ensures secure data handling and encryption
- Currently ACTIVE and running on port 8080

## Current Status

- ✅ Context7 MCP Server: ACTIVE (Port 8080) - Already running
- ✅ FileSystem MCP: ACTIVE - Built into Claude Code runtime
- ✅ Gmail MCP Server: ACTIVE (Port 8081) - **Successfully activated!**
- 🟡 LinkedIn MCP Server: BLOCKED - Requires OAuth setup
- 🟡 WhatsApp MCP Server: BLOCKED - Requires Meta Business API setup

## Setup Instructions

### Prerequisites
1. Install Node.js (v14 or higher)
2. Install required dependencies for each server:
   ```bash
   # For each server directory (gmail_mcp, linkedin_mcp, whatsapp_mcp):
   cd MCP_SERVERS/[server_name]_mcp
   npm install
   ```

### Environment Variables Setup
1. Copy the `.env` file and add your actual credentials:
   ```bash
   # Edit the .env file in the root directory with your actual credentials
   ```

2. Set environment variables based on your operating system:
   - See SETUP_INSTRUCTIONS.md for detailed steps

### Starting Servers
1. Individual servers:
   ```bash
   cd MCP_SERVERS/[server_name]_mcp
   node server.js
   ```

2. All servers at once:
   ```bash
   node start_all_mcp_servers.js
   ```

## Security Notes

- Never commit credential files to version control
- Use environment variables for sensitive information
- Regularly rotate API keys and access tokens
- Monitor logs for unauthorized access attempts
- The .env file is already added to .gitignore to prevent accidental commits

## Activation

To activate all MCP servers:

1. Set up the required environment variables in the `.env` file
2. Start each server individually or use the orchestration script:
   ```bash
   node start_all_mcp_servers.js
   ```
3. Verify all servers are running using the validation script:
   ```bash
   node validate_mcp_servers.js
   ```