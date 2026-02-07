// Gmail MCP Server Implementation
// MCP Protocol compliant server for Gmail API integration with OAuth

const express = require('express');
const { google } = require('googleapis');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 8081;

app.use(express.json());
app.use(cors());

// Environment variables for OAuth
const CLIENT_ID = process.env.GMAIL_CLIENT_ID;
const CLIENT_SECRET = process.env.GMAIL_CLIENT_SECRET;
const REDIRECT_URI = process.env.GMAIL_REDIRECT_URI || 'http://localhost:8081/oauth/callback';
const CREDENTIALS_PATH = process.env.GMAIL_CREDENTIALS_PATH || './gmail_credentials.json';

let oauth2Client = null;

// Initialize OAuth2 client if credentials are available
if (CLIENT_ID && CLIENT_SECRET) {
  oauth2Client = new google.auth.OAuth2(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI);
}

// MCP Protocol Info Endpoint - Required by MCP specification
app.get('/.well-known/mcp-info', (req, res) => {
  res.json({
    "name": "gmail-mcp",
    "description": "Gmail integration for AI Employee with OAuth",
    "version": "1.0.0",
    "capabilities": [
      {
        "name": "send_email",
        "description": "Send email via Gmail API",
        "input_schema": {
          "type": "object",
          "properties": {
            "to": {"type": "string", "description": "Recipient email address"},
            "subject": {"type": "string", "description": "Email subject"},
            "body": {"type": "string", "description": "Email body content"}
          },
          "required": ["to", "subject", "body"]
        }
      },
      {
        "name": "read_emails",
        "description": "Read emails from Gmail inbox",
        "input_schema": {
          "type": "object",
          "properties": {
            "query": {"type": "string", "description": "Search query for emails"},
            "max_results": {"type": "number", "description": "Maximum number of results to return"}
          }
        }
      },
      {
        "name": "search_emails",
        "description": "Search emails in Gmail",
        "input_schema": {
          "type": "object",
          "properties": {
            "query": {"type": "string", "description": "Search query"},
            "labels": {"type": "array", "items": {"type": "string"}}
          },
          "required": ["query"]
        }
      },
      {
        "name": "mark_read",
        "description": "Mark emails as read",
        "input_schema": {
          "type": "object",
          "properties": {
            "message_ids": {"type": "array", "items": {"type": "string"}, "description": "Array of message IDs to mark as read"}
          },
          "required": ["message_ids"]
        }
      },
      {
        "name": "archive",
        "description": "Archive emails",
        "input_schema": {
          "type": "object",
          "properties": {
            "message_ids": {"type": "array", "items": {"type": "string"}, "description": "Array of message IDs to archive"}
          },
          "required": ["message_ids"]
        }
      }
    ]
  });
});

// OAuth Authorization endpoint
app.get('/auth', (req, res) => {
  if (!oauth2Client) {
    return res.status(500).json({
      error: 'Gmail OAuth client not initialized. Missing CLIENT_ID or CLIENT_SECRET.'
    });
  }

  const scopes = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
  ];

  const url = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: scopes,
    prompt: 'consent'
  });

  res.json({
    authorization_url: url,
    message: 'Visit this URL to authorize the application'
  });
});

// OAuth Callback endpoint
app.get('/oauth/callback', async (req, res) => {
  const { code } = req.query;

  if (!code) {
    return res.status(400).json({ error: 'Authorization code not provided' });
  }

  try {
    const { tokens } = await oauth2Client.getToken(code);
    oauth2Client.setCredentials(tokens);

    // Save tokens to file (in production, use a secure vault)
    fs.writeFileSync(CREDENTIALS_PATH, JSON.stringify(tokens));
    
    res.json({
      success: true,
      message: 'Authentication successful. Tokens saved.',
      scopes: tokens.scope
    });
  } catch (error) {
    console.error('Error retrieving access token:', error);
    res.status(500).json({
      error: 'Failed to retrieve access token',
      details: error.message
    });
  }
});

// Helper function to get authenticated Gmail service
function getGmailService() {
  if (!oauth2Client) {
    throw new Error('Gmail OAuth client not initialized. Missing CLIENT_ID or CLIENT_SECRET.');
  }

  // Load saved tokens if they exist
  if (fs.existsSync(CREDENTIALS_PATH)) {
    const tokens = JSON.parse(fs.readFileSync(CREDENTIALS_PATH));
    oauth2Client.setCredentials(tokens);
  }

  return google.gmail({ version: 'v1', auth: oauth2Client });
}

// Send Email Capability
app.post('/send_email', async (req, res) => {
  try {
    const { to, subject, body } = req.body;

    if (!to || !subject || !body) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: to, subject, body'
      });
    }

    const gmail = getGmailService();

    // Create email message
    const rawMessage = [
      `To: ${to}`,
      `Subject: ${subject}`,
      '',
      body
    ].join('\n');

    const encodedMessage = Buffer.from(rawMessage).toString('base64').replace(/\+/g, '-').replace(/\//g, '_');

    const result = await gmail.users.messages.send({
      userId: 'me',
      requestBody: {
        raw: encodedMessage
      }
    });

    res.json({
      success: true,
      message: 'Email sent successfully',
      messageId: result.data.id
    });
  } catch (error) {
    console.error('Error sending email:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to send email'
    });
  }
});

// Read Emails Capability
app.post('/read_emails', async (req, res) => {
  try {
    const { query = '', max_results = 10 } = req.body;

    const gmail = getGmailService();

    const response = await gmail.users.messages.list({
      userId: 'me',
      q: query,
      maxResults: Math.min(max_results, 100) // Limit to 100 max
    });

    const messages = response.data.messages || [];

    // Get full message details for each message
    const detailedMessages = [];
    for (const message of messages.slice(0, max_results)) {
      const msgResponse = await gmail.users.messages.get({
        userId: 'me',
        id: message.id
      });

      detailedMessages.push({
        id: msgResponse.data.id,
        snippet: msgResponse.data.snippet,
        payload: msgResponse.data.payload
      });
    }

    res.json({
      success: true,
      count: detailedMessages.length,
      messages: detailedMessages
    });
  } catch (error) {
    console.error('Error reading emails:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to read emails'
    });
  }
});

// Search Emails Capability
app.post('/search_emails', async (req, res) => {
  try {
    const { query, labels = [] } = req.body;

    if (!query) {
      return res.status(400).json({
        success: false,
        error: 'Query is required'
      });
    }

    const gmail = getGmailService();

    // Build search query with labels
    let searchQuery = query;
    if (labels.length > 0) {
      searchQuery += ` label:${labels.join(' label:')}`;
    }

    const response = await gmail.users.messages.list({
      userId: 'me',
      q: searchQuery,
      maxResults: 50
    });

    res.json({
      success: true,
      count: response.data.messages?.length || 0,
      messageIds: response.data.messages || []
    });
  } catch (error) {
    console.error('Error searching emails:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to search emails'
    });
  }
});

// Mark as Read Capability
app.post('/mark_read', async (req, res) => {
  try {
    const { message_ids } = req.body;

    if (!message_ids || !Array.isArray(message_ids)) {
      return res.status(400).json({
        success: false,
        error: 'message_ids is required and must be an array'
      });
    }

    const gmail = getGmailService();

    // Remove from UNREAD label
    for (const messageId of message_ids) {
      await gmail.users.messages.modify({
        userId: 'me',
        id: messageId,
        requestBody: {
          removeLabelIds: ['UNREAD']
        }
      });
    }

    res.json({
      success: true,
      message: `${message_ids.length} messages marked as read`,
      processed_ids: message_ids
    });
  } catch (error) {
    console.error('Error marking emails as read:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to mark emails as read'
    });
  }
});

// Archive Capability
app.post('/archive', async (req, res) => {
  try {
    const { message_ids } = req.body;

    if (!message_ids || !Array.isArray(message_ids)) {
      return res.status(400).json({
        success: false,
        error: 'message_ids is required and must be an array'
      });
    }

    const gmail = getGmailService();

    // Remove from INBOX label (archiving in Gmail means removing from inbox)
    for (const messageId of message_ids) {
      await gmail.users.messages.modify({
        userId: 'me',
        id: messageId,
        requestBody: {
          removeLabelIds: ['INBOX']
        }
      });
    }

    res.json({
      success: true,
      message: `${message_ids.length} messages archived`,
      processed_ids: message_ids
    });
  } catch (error) {
    console.error('Error archiving emails:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to archive emails'
    });
  }
});

// Health check endpoint
app.get('/', (req, res) => {
  const isInitialized = !!oauth2Client;
  
  res.json({
    status: 'healthy',
    service: 'Gmail MCP Server',
    version: '1.0.0',
    initialized: isInitialized,
    capabilities: [
      'send_email',
      'read_emails',
      'search_emails',
      'mark_read',
      'archive'
    ],
    mcp_info_endpoint: `http://localhost:${PORT}/.well-known/mcp-info`,
    auth_required: !fs.existsSync(CREDENTIALS_PATH)
  });
});

app.listen(PORT, () => {
  console.log(`Gmail MCP Server running on port ${PORT}`);
  console.log(`OAuth client initialized: ${!!oauth2Client}`);
  console.log(`Credentials file: ${CREDENTIALS_PATH}`);
  console.log(`MCP Info endpoint available at: http://localhost:${PORT}/.well-known/mcp-info`);
});