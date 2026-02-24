# Complete MCP Server Activation Guide

This guide will help you activate all MCP servers for your AI Employee system.

## Current Status
- ✅ Context7 MCP Server: ACTIVE (Port 8080)
- ✅ FileSystem MCP: ACTIVE (Built into Claude Code runtime)
- ✅ Gmail MCP Server: ACTIVE (Port 8081) - **Congratulations on your successful setup!**
- 🟡 LinkedIn MCP Server: BLOCKED (Requires OAuth setup)
- 🟡 WhatsApp MCP Server: BLOCKED (Requires Meta Business API setup)

## Next Steps to Full Activation

### 1. LinkedIn MCP Server Setup (Port 8082)

#### Step 1: Create LinkedIn Application
1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Sign in with your LinkedIn account
3. Click "Create App" or "My Apps"
4. Fill in the application details:
   - Application name: "AI Employee LinkedIn Integration"
   - Description: "Integration for AI Employee system"
   - Logo: Upload a logo or use a placeholder

#### Step 2: Configure OAuth Settings
1. Go to the "Auth" tab of your application
2. Under "Authorized Redirect URLs", add:
   ```
   http://localhost:8082/oauth/callback
   ```
3. Under "Default Application Permissions", request the following scopes:
   - `r_liteprofile` (Basic profile read)
   - `r_emailaddress` (Email address)
   - `w_member_social` (Share with your network)
   - `rw_organization_social` (Share company updates)

#### Step 3: Get Your Credentials
1. Go to the "Products" tab
2. Enable the "Marketing Developer Platform" or "Share on LinkedIn"
3. Go back to "Settings" tab
4. Copy your:
   - Client ID (store as LINKEDIN_CLIENT_ID)
   - Client Secret (store as LINKEDIN_CLIENT_SECRET)

#### Step 4: Generate Access Token
1. Go to the "OAuth 2.0 playground" in your app settings
2. Generate an access token with the required permissions
3. Store this as LINKEDIN_ACCESS_TOKEN

#### Step 5: Update .env File
Update your `.env` file with the actual values:
```
LINKEDIN_CLIENT_ID=your_actual_client_id
LINKEDIN_CLIENT_SECRET=your_actual_client_secret
LINKEDIN_ACCESS_TOKEN=your_actual_access_token
```

#### Step 6: Start LinkedIn MCP Server
```bash
cd MCP_SERVERS/linkedin_mcp
node server.js
```

### 2. WhatsApp MCP Server Setup (Port 8083)

#### Step 1: Create Meta Developer Account
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Sign in with your Facebook/Meta account
3. Create a new app or select an existing one

#### Step 2: Set Up WhatsApp Business Account
1. In your app dashboard, click "Add Product"
2. Select "WhatsApp Business Platform"
3. Follow the setup wizard to create a WhatsApp Business Account

#### Step 3: Configure WhatsApp Business Account
1. Set up your phone number in the WhatsApp Business Account
2. Configure your webhooks if needed
3. Get your WhatsApp Business Account access token

#### Step 4: Get Your Credentials
1. Go to "WhatsApp" section in your app dashboard
2. Find your:
   - Access Token (under "Configuration" or "Tokens")
   - Phone Number ID (associated with your WhatsApp number)

#### Step 5: Update .env File
Update your `.env` file with the actual values:
```
WHATSAPP_ACCESS_TOKEN=your_actual_access_token
WHATSAPP_PHONE_NUMBER_ID=your_actual_phone_number_id
```

#### Step 6: Start WhatsApp MCP Server
```bash
cd MCP_SERVERS/whatsapp_mcp
node server.js
```

### 3. Starting All MCP Servers Together

Once you have all credentials set up, you can start all servers together:

```bash
node start_all_mcp_servers.js
```

### 4. Verification

After starting each server, verify they're running:

1. Check if ports are listening:
   ```bash
   netstat -ano | findstr :808
   ```

2. Test endpoints:
   - Context7: http://localhost:8080/ and http://localhost:8080/.well-known/mcp-info
   - Gmail: http://localhost:8081/ and http://localhost:8081/.well-known/mcp-info
   - LinkedIn: http://localhost:8082/ and http://localhost:8082/.well-known/mcp-info
   - WhatsApp: http://localhost:8083/ and http://localhost:8083/.well-known/mcp-info

3. Run the validation script:
   ```bash
   node validate_mcp_servers.js
   ```

## Troubleshooting

### Common Issues:
1. **Port already in use**: Make sure no other applications are using ports 8080-8083
2. **Invalid credentials**: Double-check that you copied the credentials correctly
3. **OAuth errors**: Ensure redirect URLs match exactly what you registered

### If Servers Won't Start:
1. Verify all required environment variables are set
2. Check server logs for specific error messages
3. Ensure all dependencies are installed (`npm install` in each server directory)

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- Rotate your API keys and tokens regularly
- Monitor your API usage to stay within rate limits
- Revoke access tokens if they're compromised

## Success Criteria

Your AI Employee system will be **FULLY OPERATIONAL** when:
- All 5 MCP servers are ACTIVE (Context7, FileSystem, Gmail, LinkedIn, WhatsApp)
- All servers respond to their health and MCP info endpoints
- All capabilities are accessible and functional
- Claude Code can interact with all MCP servers seamlessly

---

**Congratulations!** You've already successfully activated the Gmail MCP server. Just two more to go for complete functionality!