// WhatsApp MCP Server Implementation
// MCP Protocol compliant server for WhatsApp Business API integration with OAuth

const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 8083;

app.use(express.json());
app.use(cors());

// WhatsApp Business API configuration
const ACCESS_TOKEN = process.env.WHATSAPP_ACCESS_TOKEN;
const PHONE_NUMBER_ID = process.env.WHATSAPP_PHONE_NUMBER_ID;
const BASE_URL = 'https://graph.facebook.com/v18.0';

// MCP Protocol Info Endpoint - Required by MCP specification
app.get('/.well-known/mcp-info', (req, res) => {
  res.json({
    "name": "whatsapp-mcp",
    "description": "WhatsApp Business API integration for AI Employee with OAuth",
    "version": "1.0.0",
    "capabilities": [
      {
        "name": "send_message",
        "description": "Send messages via WhatsApp Business API",
        "input_schema": {
          "type": "object",
          "properties": {
            "to": {"type": "string", "description": "Recipient phone number in international format"},
            "message": {"type": "string", "description": "Message text content"},
            "type": {"type": "string", "enum": ["text", "image", "document"], "default": "text"}
          },
          "required": ["to", "message"]
        }
      },
      {
        "name": "read_messages",
        "description": "Read incoming messages from WhatsApp",
        "input_schema": {
          "type": "object",
          "properties": {
            "limit": {"type": "number", "description": "Maximum number of messages to retrieve"}
          }
        }
      },
      {
        "name": "send_media",
        "description": "Send media files via WhatsApp",
        "input_schema": {
          "type": "object",
          "properties": {
            "to": {"type": "string", "description": "Recipient phone number in international format"},
            "media_url": {"type": "string", "description": "URL of the media file to send"},
            "caption": {"type": "string", "description": "Optional caption for the media"},
            "media_type": {"type": "string", "enum": ["image", "document", "video"]}
          },
          "required": ["to", "media_url", "media_type"]
        }
      },
      {
        "name": "check_status",
        "description": "Check message delivery status",
        "input_schema": {
          "type": "object",
          "properties": {
            "message_id": {"type": "string", "description": "ID of the message to check status for"}
          },
          "required": ["message_id"]
        }
      }
    ]
  });
});

// Send Message Capability
app.post('/send_message', async (req, res) => {
  try {
    const { to, message, type = 'text' } = req.body;

    if (!to || !message) {
      return res.status(400).json({
        success: false,
        error: 'Recipient phone number (to) and message content are required'
      });
    }

    if (!ACCESS_TOKEN || !PHONE_NUMBER_ID) {
      return res.status(500).json({
        success: false,
        error: 'WhatsApp API credentials not configured. Missing ACCESS_TOKEN or PHONE_NUMBER_ID.'
      });
    }

    // Format phone number (remove any non-digit characters except +)
    const formattedTo = to.replace(/[^\d+]/g, '');

    // Prepare the message payload
    let messagePayload;
    switch (type) {
      case 'text':
        messagePayload = {
          messaging_product: 'whatsapp',
          to: formattedTo,
          type: 'text',
          text: {
            body: message
          }
        };
        break;
      default:
        return res.status(400).json({
          success: false,
          error: `Unsupported message type: ${type}`
        });
    }

    // Send the message via WhatsApp Business API
    const response = await axios.post(
      `${BASE_URL}/${PHONE_NUMBER_ID}/messages`,
      messagePayload,
      {
        headers: {
          'Authorization': `Bearer ${ACCESS_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );

    res.json({
      success: true,
      message: 'Message sent successfully',
      message_id: response.data.messages ? response.data.messages[0]?.id : null,
      recipient: formattedTo
    });
  } catch (error) {
    console.error('Error sending WhatsApp message:', error.response?.data || error.message);
    res.status(500).json({
      success: false,
      error: error.response?.data?.error?.message || error.message,
      message: 'Failed to send WhatsApp message'
    });
  }
});

// Send Media Capability
app.post('/send_media', async (req, res) => {
  try {
    const { to, media_url, caption = '', media_type = 'image' } = req.body;

    if (!to || !media_url || !media_type) {
      return res.status(400).json({
        success: false,
        error: 'Recipient phone number (to), media_url, and media_type are required'
      });
    }

    if (!ACCESS_TOKEN || !PHONE_NUMBER_ID) {
      return res.status(500).json({
        success: false,
        error: 'WhatsApp API credentials not configured. Missing ACCESS_TOKEN or PHONE_NUMBER_ID.'
      });
    }

    // Format phone number
    const formattedTo = to.replace(/[^\d+]/g, '');

    // Prepare the media message payload
    let mediaPayload;
    switch (media_type) {
      case 'image':
        mediaPayload = {
          messaging_product: 'whatsapp',
          to: formattedTo,
          type: 'image',
          image: {
            link: media_url,
            caption: caption
          }
        };
        break;
      case 'document':
        mediaPayload = {
          messaging_product: 'whatsapp',
          to: formattedTo,
          type: 'document',
          document: {
            link: media_url,
            caption: caption
          }
        };
        break;
      case 'video':
        mediaPayload = {
          messaging_product: 'whatsapp',
          to: formattedTo,
          type: 'video',
          video: {
            link: media_url,
            caption: caption
          }
        };
        break;
      default:
        return res.status(400).json({
          success: false,
          error: `Unsupported media type: ${media_type}`
        });
    }

    // Send the media message via WhatsApp Business API
    const response = await axios.post(
      `${BASE_URL}/${PHONE_NUMBER_ID}/messages`,
      mediaPayload,
      {
        headers: {
          'Authorization': `Bearer ${ACCESS_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );

    res.json({
      success: true,
      message: 'Media sent successfully',
      message_id: response.data.messages ? response.data.messages[0]?.id : null,
      recipient: formattedTo
    });
  } catch (error) {
    console.error('Error sending WhatsApp media:', error.response?.data || error.message);
    res.status(500).json({
      success: false,
      error: error.response?.data?.error?.message || error.message,
      message: 'Failed to send WhatsApp media'
    });
  }
});

// Read Messages Capability (Placeholder - in real implementation, this would be a webhook)
app.post('/read_messages', async (req, res) => {
  try {
    const { limit = 10 } = req.body;

    // Note: Reading messages in WhatsApp Business API is typically done via webhooks
    // This is a placeholder that explains the limitation
    res.json({
      success: false,
      error: 'Reading messages requires webhook implementation',
      message: 'WhatsApp messages are received via webhooks. This server would need to implement a webhook endpoint to receive incoming messages from WhatsApp.'
    });
  } catch (error) {
    console.error('Error reading WhatsApp messages:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to read WhatsApp messages'
    });
  }
});

// Check Message Status Capability
app.post('/check_status', async (req, res) => {
  try {
    const { message_id } = req.body;

    if (!message_id) {
      return res.status(400).json({
        success: false,
        error: 'Message ID is required'
      });
    }

    // WhatsApp Business API doesn't have a direct message status endpoint
    // Status updates are received via webhooks
    res.json({
      success: false,
      error: 'Message status checking requires webhook implementation',
      message: 'Message status updates are received via webhooks. This server would need to implement a webhook endpoint to receive status updates from WhatsApp.'
    });
  } catch (error) {
    console.error('Error checking message status:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to check message status'
    });
  }
});

// Webhook endpoint for receiving messages and status updates from WhatsApp
app.post('/webhook', express.raw({type: 'application/json'}), (req, res) => {
  try {
    const signature = req.headers['x-hub-signature'];
    // In a real implementation, you would verify the signature here
    
    const body = JSON.parse(req.body);
    
    // Handle different types of webhook events
    if (body.object === 'whatsapp_business_account') {
      const entry = body.entry[0];
      if (entry.changes && entry.changes[0]) {
        const changes = entry.changes[0];
        const field = changes.field;
        
        if (field === 'messages') {
          // Handle incoming messages
          const messages = changes.value.messages;
          if (messages) {
            messages.forEach(msg => {
              console.log(`Received message from ${msg.from}: ${msg.text?.body || '[media message]'}`);
              // Process the message as needed
            });
          }
          
          // Handle message status updates
          const statuses = changes.value.statuses;
          if (statuses) {
            statuses.forEach(status => {
              console.log(`Message ${status.id} status: ${status.status}`);
              // Process the status update as needed
            });
          }
        }
      }
    }
    
    // Respond to acknowledge receipt
    res.status(200).json({ success: true });
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Webhook verification endpoint
app.get('/webhook', (req, res) => {
  const VERIFY_TOKEN = process.env.WHATSAPP_VERIFY_TOKEN || 'verify_token'; // Should match the token configured in WhatsApp
  
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];
  
  if (mode && token) {
    if (mode === 'subscribe' && token === VERIFY_TOKEN) {
      console.log('Webhook verified successfully');
      res.status(200).send(challenge);
    } else {
      res.status(403).json({ success: false, error: 'Invalid verification token' });
    }
  } else {
    res.status(400).json({ success: false, error: 'Missing verification parameters' });
  }
});

// Health check endpoint
app.get('/', (req, res) => {
  const hasCredentials = !!(ACCESS_TOKEN && PHONE_NUMBER_ID);
  
  res.json({
    status: 'healthy',
    service: 'WhatsApp MCP Server',
    version: '1.0.0',
    initialized: hasCredentials,
    capabilities: [
      'send_message',
      'read_messages',
      'send_media',
      'check_status'
    ],
    mcp_info_endpoint: `http://localhost:${PORT}/.well-known/mcp-info`,
    webhook_endpoint: `http://localhost:${PORT}/webhook`
  });
});

app.listen(PORT, () => {
  console.log(`WhatsApp MCP Server running on port ${PORT}`);
  console.log(`Credentials configured: ${!!(ACCESS_TOKEN && PHONE_NUMBER_ID)}`);
  console.log(`Webhook endpoint: http://localhost:${PORT}/webhook`);
  console.log(`MCP Info endpoint available at: http://localhost:${PORT}/.well-known/mcp-info`);
});