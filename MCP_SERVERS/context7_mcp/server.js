// Context7 MCP Server Implementation
// MCP Protocol compliant server for Context7 API integration

const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 8080;

app.use(express.json());
app.use(cors());

// Read API key from environment
const API_KEY = process.env.CONTEXT7_API_KEY || 'ctx7sk-e4a85452-50e5-4ac0-a590-9987fc59c1aa';

// MCP Protocol Info Endpoint - Required by MCP specification
app.get('/.well-known/mcp-info', (req, res) => {
  res.json({
    "name": "context7-mcp",
    "description": "Context7 integration for AI Employee",
    "version": "1.0.0",
    "capabilities": [
      {
        "name": "context_analysis",
        "description": "Analyze context from provided data",
        "input_schema": {
          "type": "object",
          "properties": {
            "query": {"type": "string", "description": "Query to analyze"},
            "context": {"type": "string", "description": "Context data to analyze"}
          },
          "required": ["query", "context"]
        }
      },
      {
        "name": "data_retrieval",
        "description": "Retrieve data from various sources",
        "input_schema": {
          "type": "object",
          "properties": {
            "source": {"type": "string", "description": "Source to retrieve data from"},
            "query": {"type": "string", "description": "Query for data retrieval"}
          },
          "required": ["source", "query"]
        }
      },
      {
        "name": "information_processing",
        "description": "Process information with specified operations",
        "input_schema": {
          "type": "object",
          "properties": {
            "data": {"type": "string", "description": "Data to process"},
            "operation": {"type": "string", "description": "Operation to perform"}
          },
          "required": ["data", "operation"]
        }
      },
      {
        "name": "knowledge_base_query",
        "description": "Query knowledge base with filters",
        "input_schema": {
          "type": "object",
          "properties": {
            "query": {"type": "string", "description": "Query for knowledge base"},
            "filters": {"type": "object", "description": "Filters for the query"}
          },
          "required": ["query"]
        }
      }
    ]
  });
});

// Context Analysis Capability
app.post('/context_analysis', async (req, res) => {
  try {
    const { query, context } = req.body;

    // Forward request to Context7 API using the MCP endpoint
    const response = await axios.post('https://mcp.context7.com/mcp', {
      action: 'analyze_context',
      query,
      context,
      api_key: API_KEY
    }, {
      headers: {
        'CONTEXT7_API_KEY': API_KEY,
        'Content-Type': 'application/json'
      }
    });

    res.json({
      success: true,
      result: response.data,
      message: 'Context analysis completed successfully'
    });
  } catch (error) {
    console.error('Error in context_analysis:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to perform context analysis'
    });
  }
});

// Data Retrieval Capability
app.post('/data_retrieval', async (req, res) => {
  try {
    const { source, query } = req.body;

    // Forward request to Context7 API
    const response = await axios.post('https://mcp.context7.com/mcp', {
      action: 'retrieve_data',
      source,
      query,
      api_key: API_KEY
    }, {
      headers: {
        'CONTEXT7_API_KEY': API_KEY,
        'Content-Type': 'application/json'
      }
    });

    res.json({
      success: true,
      result: response.data,
      message: 'Data retrieval completed successfully'
    });
  } catch (error) {
    console.error('Error in data_retrieval:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to retrieve data'
    });
  }
});

// Information Processing Capability
app.post('/information_processing', async (req, res) => {
  try {
    const { data, operation } = req.body;

    // Forward request to Context7 API
    const response = await axios.post('https://mcp.context7.com/mcp', {
      action: 'process_information',
      data,
      operation,
      api_key: API_KEY
    }, {
      headers: {
        'CONTEXT7_API_KEY': API_KEY,
        'Content-Type': 'application/json'
      }
    });

    res.json({
      success: true,
      result: response.data,
      message: 'Information processing completed successfully'
    });
  } catch (error) {
    console.error('Error in information_processing:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to process information'
    });
  }
});

// Knowledge Base Query Capability
app.post('/knowledge_base_query', async (req, res) => {
  try {
    const { query, filters = {} } = req.body;

    // Forward request to Context7 API
    const response = await axios.post('https://mcp.context7.com/mcp', {
      action: 'query_knowledge_base',
      query,
      filters,
      api_key: API_KEY
    }, {
      headers: {
        'CONTEXT7_API_KEY': API_KEY,
        'Content-Type': 'application/json'
      }
    });

    res.json({
      success: true,
      result: response.data,
      message: 'Knowledge base query completed successfully'
    });
  } catch (error) {
    console.error('Error in knowledge_base_query:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to query knowledge base'
    });
  }
});

// Health check endpoint
app.get('/', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'Context7 MCP Server',
    version: '1.0.0',
    capabilities: [
      'context_analysis',
      'data_retrieval',
      'information_processing',
      'knowledge_base_query'
    ],
    mcp_info_endpoint: `http://localhost:${PORT}/.well-known/mcp-info`
  });
});

app.listen(PORT, () => {
  console.log(`Context7 MCP Server running on port ${PORT}`);
  console.log(`API Key loaded: ${API_KEY ? 'Yes' : 'No'}`);
  console.log(`MCP Info endpoint available at: http://localhost:${PORT}/.well-known/mcp-info`);
});