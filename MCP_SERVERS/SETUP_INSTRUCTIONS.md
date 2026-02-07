# AI Employee MCP Servers Setup Guide

This document explains how to set up and run all MCP servers for your AI Employee system.

## Current Status
- ✅ Context7 MCP Server: ACTIVE (Port 8080) - Already running
- ✅ FileSystem MCP: ACTIVE - Built into Claude Code runtime
- 🟡 Gmail MCP Server: BLOCKED - Requires OAuth setup
- 🟡 LinkedIn MCP Server: BLOCKED - Requires OAuth setup  
- 🟡 WhatsApp MCP Server: BLOCKED - Requires Meta Business API setup

## Environment Variables Setup

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your actual credentials:
   - For Gmail: Visit https://console.cloud.google.com/
   - For LinkedIn: Visit https://www.linkedin.com/developers/
   - For WhatsApp: Visit https://developers.facebook.com/

3. Source the environment variables:
   ```bash
   # On Windows (Command Prompt)
   set /p=GMAIL_CLIENT_ID < .env
   # Or use a tool like dotenv to load variables
   
   # On Windows (PowerShell)
   Get-Content .env | ForEach-Object {
       $name, $value = $_.split('=')
       [Environment]::SetEnvironmentVariable($name, $value)
   }
   ```

## Setting Environment Variables on Windows

### Option 1: Using Command Prompt
```cmd
set GMAIL_CLIENT_ID=your_actual_client_id
set GMAIL_CLIENT_SECRET=your_actual_client_secret
set LINKEDIN_CLIENT_ID=your_actual_client_id
set LINKEDIN_CLIENT_SECRET=your_actual_client_secret
set LINKEDIN_ACCESS_TOKEN=your_actual_access_token
set WHATSAPP_ACCESS_TOKEN=your_actual_access_token
set WHATSAPP_PHONE_NUMBER_ID=your_actual_phone_number_id
```

### Option 2: Using PowerShell
```powershell
$env:GMAIL_CLIENT_ID="your_actual_client_id"
$env:GMAIL_CLIENT_SECRET="your_actual_client_secret"
$env:LINKEDIN_CLIENT_ID="your_actual_client_id"
$env:LINKEDIN_CLIENT_SECRET="your_actual_client_secret"
$env:LINKEDIN_ACCESS_TOKEN="your_actual_access_token"
$env:WHATSAPP_ACCESS_TOKEN="your_actual_access_token"
$env:WHATSAPP_PHONE_NUMBER_ID="your_actual_phone_number_id"
```

## Starting MCP Servers

After setting environment variables, start each server:

### Individual Servers:
```bash
# Start Gmail MCP Server
cd MCP_SERVERS/gmail_mcp
node server.js

# Start LinkedIn MCP Server  
cd MCP_SERVERS/linkedin_mcp
node server.js

# Start WhatsApp MCP Server
cd MCP_SERVERS/whatsapp_mcp
node server.js
```

### All Servers at Once:
```bash
node start_all_mcp_servers.js
```

## Verification

After starting servers, verify they're running:

1. Check if ports are listening:
   ```bash
   netstat -ano | findstr :808
   ```

2. Test endpoints:
   - Context7: http://localhost:8080/ and http://localhost:8080/.well-known/mcp-info
   - Gmail: http://localhost:8081/ and http://localhost:8081/.well-known/mcp-info
   - LinkedIn: http://localhost:8082/ and http://localhost:8082/.well-known/mcp-info
   - WhatsApp: http://localhost:8083/ and http://localhost:8083/.well-known/mcp-info

## OAuth Setup Instructions

### Gmail OAuth Setup:
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials
5. Add `http://localhost:8081/oauth/callback` to authorized redirect URIs
6. Copy Client ID and Client Secret to your environment variables

### LinkedIn OAuth Setup:
1. Go to LinkedIn Developer Portal: https://www.linkedin.com/developers/
2. Create a new application
3. Set the redirect URL to `http://localhost:8082/oauth/callback`
4. Copy Client ID, Client Secret, and generate an Access Token
5. Add to your environment variables

### WhatsApp Business API Setup:
1. Go to Facebook Developers: https://developers.facebook.com/
2. Set up a WhatsApp Business Account
3. Get your Access Token and Phone Number ID
4. Add to your environment variables

## Troubleshooting

If servers are not starting:
1. Verify all required environment variables are set
2. Check that ports 8080-8083 are not in use by other applications
3. Review server logs for specific error messages
4. Ensure all dependencies are installed (`npm install` in each server directory)

## Security Notes

- Never commit the `.env` file to version control
- Store credentials securely and rotate them regularly
- Use different credentials for development and production environments
- The .env file is already added to .gitignore to prevent accidental commits