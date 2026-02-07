# Personal AI Employee System - Folder Structure

## Overview
This document describes the complete folder structure of the Personal AI Employee System and explains how each component works together.

## Folder Structure

```
Personal_AI_Employee_System/
├── 01_Incoming_Tasks/           # New tasks arrive here
├── 02_In_Progress_Tasks/        # Tasks currently being processed
├── 03_Completed_Tasks/          # Tasks that have been completed
├── 04_Approval_Workflows/       # Tasks requiring human approval
├── 05_Failed_Tasks/             # Tasks that failed processing
├── Business/                    # Business-related documents and policies
├── Inbox/                       # Incoming files triggering the system
├── Logs/                        # System logs and debugging information
├── MCP_SERVERS/                 # Multiple concurrent process servers
│   ├── context7_mcp/            # Context 7 microservice
│   ├── file_system_mcp/         # File system microservice
│   ├── gmail_mcp/               # Gmail integration microservice
│   ├── linkedin_mcp/            # LinkedIn integration microservice
│   └── whatsapp_mcp/            # WhatsApp integration microservice
├── Memory/                      # Learning and memory storage
├── node_modules/                # Node.js dependencies (excluded from repo)
├── Plans/                       # Strategic planning documents
├── Reports/                     # Generated reports and analytics
├── __pycache__/                 # Python cache (excluded from repo)
├── .env.example                 # Template for environment variables
├── .gitignore                   # Git ignore rules
├── autonomous_system.py         # Main autonomous system orchestrator
├── intelligent_system.py        # Intelligent system with learning
├── file_watcher.py              # File system monitoring
├── gmail_watcher.py             # Gmail monitoring
├── task_processor.py            # Task processing engine
├── ralph_loop.py                # Auto-retry mechanism
├── dashboard_generator.py       # Dashboard and reporting
├── [other source files...]      # Core system components
└── README.md                    # Main documentation
```

## How the System Works

### 1. Task Flow
- **Inbox**: Files placed here trigger the system
- **01_Incoming_Tasks**: New tasks created from monitored sources
- **02_In_Progress_Tasks**: Tasks actively being processed
- **03_Completed_Tasks**: Successfully completed tasks
- **04_Approval_Workflows**: Tasks requiring human approval
- **05_Failed_Tasks**: Tasks that failed and need attention

### 2. Microservice Architecture (MCP_SERVERS)
Each MCP (Microservice Control Point) handles specific functions:
- **context7_mcp**: Context management and state
- **file_system_mcp**: File system operations
- **gmail_mcp**: Gmail integration and email processing
- **linkedin_mcp**: LinkedIn integration and social media
- **whatsapp_mcp**: WhatsApp messaging integration

### 3. Intelligence Layer
- **Memory/**: Stores learned patterns, success/failure rates, and optimization strategies
- **Learning**: System improves over time based on past performance
- **Self-correction**: Automatically adjusts strategies based on failures

### 4. Automation Features
- **Auto-task flow**: Tasks automatically move between stages
- **Ralph Loop**: Auto-retry mechanism with up to 10 retries
- **Approval gate**: Human approval for critical tasks
- **Weekly CEO reports**: Automated reporting system

## Setting Up the System

1. Clone the repository
2. Install dependencies: `npm install` and `pip install -r requirements.txt`
3. Set up environment variables using `.env.example` as template
4. Configure MCP servers as needed
5. Run the system: `python autonomous_system.py`

## Security & Privacy
- Sensitive data (API keys, tokens) stored in `.env` (not in repository)
- Temporary task data kept out of version control
- Logs and memory data managed separately for privacy

## Contributing
The system is designed to be modular and extensible. New MCP services can be added to expand functionality, and the learning system adapts to new patterns over time.