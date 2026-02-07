// LinkedIn MCP Server Implementation
// MCP Protocol compliant server for LinkedIn API integration with OAuth

const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 8082;

app.use(express.json());
app.use(cors());

// LinkedIn API configuration
const CLIENT_ID = process.env.LINKEDIN_CLIENT_ID;
const CLIENT_SECRET = process.env.LINKEDIN_CLIENT_SECRET;
const REDIRECT_URI = process.env.LINKEDIN_REDIRECT_URI || `http://localhost:${PORT}/oauth/callback`;
const ACCESS_TOKEN = process.env.LINKEDIN_ACCESS_TOKEN;

// MCP Protocol Info Endpoint - Required by MCP specification
app.get('/.well-known/mcp-info', (req, res) => {
  res.json({
    "name": "linkedin-mcp",
    "description": "LinkedIn integration for AI Employee with OAuth",
    "version": "1.0.0",
    "capabilities": [
      {
        "name": "post_update",
        "description": "Post updates to LinkedIn",
        "input_schema": {
          "type": "object",
          "properties": {
            "text": {"type": "string", "description": "Text content of the post"},
            "visibility": {"type": "string", "enum": ["PUBLIC", "CONNECTIONS"], "default": "PUBLIC"}
          },
          "required": ["text"]
        }
      },
      {
        "name": "read_posts",
        "description": "Read posts from LinkedIn feed",
        "input_schema": {
          "type": "object",
          "properties": {
            "count": {"type": "number", "description": "Number of posts to retrieve"},
            "person_urn": {"type": "string", "description": "URN of the person whose posts to retrieve"}
          }
        }
      },
      {
        "name": "send_connection_requests",
        "description": "Send connection requests on LinkedIn",
        "input_schema": {
          "type": "object",
          "properties": {
            "profile_url": {"type": "string", "description": "URL of the profile to connect with"},
            "message": {"type": "string", "description": "Optional message to include with the request"}
          },
          "required": ["profile_url"]
        }
      },
      {
        "name": "endorse_skills",
        "description": "Endorse skills for a LinkedIn contact",
        "input_schema": {
          "type": "object",
          "properties": {
            "profile_url": {"type": "string", "description": "URL of the profile to endorse"},
            "skills": {"type": "array", "items": {"type": "string"}, "description": "Skills to endorse"}
          },
          "required": ["profile_url", "skills"]
        }
      },
      {
        "name": "comment_on_posts",
        "description": "Comment on LinkedIn posts",
        "input_schema": {
          "type": "object",
          "properties": {
            "post_urn": {"type": "string", "description": "URN of the post to comment on"},
            "comment": {"type": "string", "description": "Comment text"}
          },
          "required": ["post_urn", "comment"]
        }
      }
    ]
  });
});

// OAuth Authorization endpoint
app.get('/auth', (req, res) => {
  if (!CLIENT_ID || !CLIENT_SECRET) {
    return res.status(500).json({
      error: 'LinkedIn OAuth client not initialized. Missing LINKEDIN_CLIENT_ID or LINKEDIN_CLIENT_SECRET.'
    });
  }

  const scopes = [
    'openid',
    'profile',
    'email',
    'w_member_social',
    'w_organization_social',
    'rw_organization_admin'
  ];

  const authUrl = `https://www.linkedin.com/oauth/v2/authorization?` +
    `client_id=${CLIENT_ID}&` +
    `redirect_uri=${encodeURIComponent(REDIRECT_URI)}&` +
    `response_type=code&` +
    `scope=${encodeURIComponent(scopes.join(' '))}`;

  res.json({
    authorization_url: authUrl,
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
    // Exchange code for access token
    const tokenResponse = await axios.post('https://www.linkedin.com/oauth/v2/accessToken', null, {
      params: {
        grant_type: 'authorization_code',
        code: code,
        redirect_uri: REDIRECT_URI,
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET
      },
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

    const accessToken = tokenResponse.data.access_token;

    // In a real implementation, you would securely store this token
    // For this example, we'll just return it (in production, use a secure vault)
    res.json({
      success: true,
      message: 'Authentication successful',
      access_token: accessToken,
      expires_in: tokenResponse.data.expires_in
    });
  } catch (error) {
    console.error('Error retrieving access token:', error.response?.data || error.message);
    res.status(500).json({
      error: 'Failed to retrieve access token',
      details: error.response?.data || error.message
    });
  }
});

// Helper function to get authorization headers
function getAuthHeaders(token = null) {
  const authToken = token || ACCESS_TOKEN;
  if (!authToken) {
    throw new Error('No LinkedIn access token available. Please authenticate first.');
  }
  
  return {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json',
    'X-Restli-Protocol-Version': '2.0.0',
    'LinkedIn-Version': '202305'
  };
}

// Post Update Capability
app.post('/post_update', async (req, res) => {
  try {
    const { text, visibility = 'PUBLIC' } = req.body;

    if (!text) {
      return res.status(400).json({
        success: false,
        error: 'Text content is required'
      });
    }

    // Get user's URN
    const profileResponse = await axios.get('https://api.linkedin.com/v2/me', {
      headers: getAuthHeaders()
    });

    const authorUrn = `urn:li:person:${profileResponse.data.id}`;

    // Create the post
    const postData = {
      author: authorUrn,
      lifecycleState: 'PUBLISHED',
      specificContent: {
        '$type': 'com.linkedin.ugc.ShareContent',
        shareCommentary: {
          text: text
        },
        shareMediaCategory: 'NONE'
      },
      visibility: {
        '$type': 'com.linkedin.ugc.MemberNetworkVisibility',
        code: visibility
      }
    };

    const response = await axios.post('https://api.linkedin.com/v2/ugcPosts', postData, {
      headers: getAuthHeaders()
    });

    res.json({
      success: true,
      message: 'Post published successfully',
      post_id: response.data.id,
      urn: response.data.id
    });
  } catch (error) {
    console.error('Error posting update:', error.response?.data || error.message);
    res.status(500).json({
      success: false,
      error: error.response?.data?.message || error.message,
      message: 'Failed to post update'
    });
  }
});

// Read Posts Capability
app.post('/read_posts', async (req, res) => {
  try {
    const { count = 10, person_urn } = req.body;

    // If no specific person URN is provided, get the user's own posts
    let endpoint;
    if (person_urn) {
      endpoint = `https://api.linkedin.com/v2/ugcPosts?q=authors&authors=List(${person_urn})&count=${count}`;
    } else {
      // Get user's URN first
      const profileResponse = await axios.get('https://api.linkedin.com/v2/me', {
        headers: getAuthHeaders()
      });
      const userUrn = `urn:li:person:${profileResponse.data.id}`;
      endpoint = `https://api.linkedin.com/v2/ugcPosts?q=authors&authors=List(${userUrn})&count=${count}`;
    }

    const response = await axios.get(endpoint, {
      headers: getAuthHeaders()
    });

    res.json({
      success: true,
      count: response.data.elements?.length || 0,
      posts: response.data.elements || []
    });
  } catch (error) {
    console.error('Error reading posts:', error.response?.data || error.message);
    res.status(500).json({
      success: false,
      error: error.response?.data?.message || error.message,
      message: 'Failed to read posts'
    });
  }
});

// Send Connection Requests Capability
app.post('/send_connection_requests', async (req, res) => {
  try {
    const { profile_url, message = '' } = req.body;

    if (!profile_url) {
      return res.status(400).json({
        success: false,
        error: 'Profile URL is required'
      });
    }

    // Extract profile ID from URL (simplified - in reality, you'd need to resolve the URL)
    // For this example, we'll assume the profile ID is the last segment of the URL
    const profileId = profile_url.split('/').pop();
    
    if (!profileId || profileId === '') {
      return res.status(400).json({
        success: false,
        error: 'Could not extract profile ID from URL'
      });
    }

    // Get current user's profile to get their URN
    const profileResponse = await axios.get('https://api.linkedin.com/v2/me', {
      headers: getAuthHeaders()
    });
    const currentUserUrn = `urn:li:person:${profileResponse.data.id}`;

    // Create connection request
    const connectionData = {
      trackingId: 'random-tracking-id', // In practice, this should be a real tracking ID
      recipients: [`urn:li:fs_miniProfile:<b64-encoded-id>`], // LinkedIn requires encoded profile URNs
      requestId: 'initiate_connect',
      parameters: {
        inviteSource: 'member',
        message: message
      }
    };

    // Note: LinkedIn's connection API is complex and requires encoded profile URNs
    // This is a simplified representation - actual implementation would need to resolve profile IDs properly
    res.json({
      success: false,
      error: 'Connection requests require complex profile ID resolution that is beyond this example implementation',
      message: 'This capability requires additional implementation to resolve profile IDs properly'
    });
  } catch (error) {
    console.error('Error sending connection request:', error.response?.data || error.message);
    res.status(500).json({
      success: false,
      error: error.response?.data?.message || error.message,
      message: 'Failed to send connection request'
    });
  }
});

// Endorse Skills Capability
app.post('/endorse_skills', async (req, res) => {
  try {
    const { profile_url, skills } = req.body;

    if (!profile_url || !skills || !Array.isArray(skills) || skills.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Profile URL and skills array are required'
      });
    }

    // This is a simplified implementation - LinkedIn's endorsement API is complex
    // and requires proper profile ID resolution
    res.json({
      success: false,
      error: 'Skill endorsements require complex profile ID resolution that is beyond this example implementation',
      message: 'This capability requires additional implementation to resolve profile IDs properly'
    });
  } catch (error) {
    console.error('Error endorsing skills:', error.response?.data || error.message);
    res.status(500).json({
      success: false,
      error: error.response?.data?.message || error.message,
      message: 'Failed to endorse skills'
    });
  }
});

// Comment on Posts Capability
app.post('/comment_on_posts', async (req, res) => {
  try {
    const { post_urn, comment } = req.body;

    if (!post_urn || !comment) {
      return res.status(400).json({
        success: false,
        error: 'Post URN and comment are required'
      });
    }

    // Get user's URN
    const profileResponse = await axios.get('https://api.linkedin.com/v2/me', {
      headers: getAuthHeaders()
    });
    const authorUrn = `urn:li:person:${profileResponse.data.id}`;

    // Create comment
    const commentData = {
      actor: authorUrn,
      object: post_urn, // URN of the post to comment on
      message: {
        text: comment
      }
    };

    const response = await axios.post('https://api.linkedin.com/v2/comments', commentData, {
      headers: getAuthHeaders()
    });

    res.json({
      success: true,
      message: 'Comment posted successfully',
      comment_id: response.data.id,
      urn: response.data.id
    });
  } catch (error) {
    console.error('Error commenting on post:', error.response?.data || error.message);
    res.status(500).json({
      success: false,
      error: error.response?.data?.message || error.message,
      message: 'Failed to comment on post'
    });
  }
});

// Health check endpoint
app.get('/', (req, res) => {
  const hasAccessToken = !!ACCESS_TOKEN;
  
  res.json({
    status: 'healthy',
    service: 'LinkedIn MCP Server',
    version: '1.0.0',
    initialized: !!(CLIENT_ID && CLIENT_SECRET),
    authenticated: hasAccessToken,
    capabilities: [
      'post_update',
      'read_posts',
      'send_connection_requests',
      'endorse_skills',
      'comment_on_posts'
    ],
    mcp_info_endpoint: `http://localhost:${PORT}/.well-known/mcp-info`
  });
});

app.listen(PORT, () => {
  console.log(`LinkedIn MCP Server running on port ${PORT}`);
  console.log(`OAuth initialized: ${!!(CLIENT_ID && CLIENT_SECRET)}`);
  console.log(`Access token available: ${!!ACCESS_TOKEN}`);
  console.log(`MCP Info endpoint available at: http://localhost:${PORT}/.well-known/mcp-info`);
});