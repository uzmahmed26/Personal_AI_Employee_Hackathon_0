import json
import os
from pathlib import Path
import subprocess
import psutil
import time

def check_server_status(server_name, config_path):
    """Check if a server is running and its status"""
    try:
        # Check if config file exists
        config_file = Path(config_path) / "config.json"
        if not config_file.exists():
            return {"status": "missing_config", "details": "Configuration file not found"}

        # Read the config to get server info
        with open(config_file, 'r') as f:
            config = json.load(f)

        # Look for running processes (this is a simplified check)
        server_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Simple check if any process contains the server name
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else proc.info['name']
                if server_name.lower() in cmdline.lower():
                    server_processes.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if server_processes:
            return {
                "status": "running",
                "details": f"Running with PID(s): {server_processes}",
                "capabilities": config.get("server", {}).get("capabilities", [])
            }
        else:
            return {
                "status": "not_running",
                "details": "Config exists but no process found",
                "capabilities": config.get("server", {}).get("capabilities", [])
            }
    except Exception as e:
        return {"status": "error", "details": str(e)}

def display_mcp_status():
    """Display the status of all MCP servers"""
    print("="*60)
    print("MCP SERVER STATUS FOR PERSONAL AI EMPLOYEE")
    print("="*60)

    servers = [
        {"name": "File System MCP", "path": "MCP_SERVERS/file_system_mcp", "operation": "File operations (read/write/list)"},
        {"name": "Gmail MCP", "path": "MCP_SERVERS/gmail_mcp", "operation": "Email operations (send/read/search)"},
        {"name": "WhatsApp MCP", "path": "MCP_SERVERS/whatsapp_mcp", "operation": "WhatsApp messaging"},
        {"name": "LinkedIn MCP", "path": "MCP_SERVERS/linkedin_mcp", "operation": "LinkedIn posting and engagement"},
        {"name": "Context 7 MCP", "path": "MCP_SERVERS/context7_mcp", "operation": "Context analysis and data retrieval"}
    ]

    all_working = True

    for server in servers:
        status_info = check_server_status(server["name"], server["path"])

        print(f"\n{server['name']}:")
        print(f"  Operation: {server['operation']}")
        print(f"  Status: {status_info['status']}")
        print(f"  Details: {status_info['details']}")
        print(f"  Capabilities: {', '.join(status_info.get('capabilities', []))}")

        if status_info['status'] != 'running':
            all_working = False

    print("\n" + "="*60)
    if all_working:
        print("[SUCCESS] ALL MCP SERVERS ARE WORKING PROPERLY")
        print("Your Personal AI Employee can perform all operations:")
        print("- File system operations")
        print("- Gmail operations")
        print("- WhatsApp messaging")
        print("- LinkedIn posting")
        print("- Context analysis")
    else:
        print("[WARNING] SOME MCP SERVERS ARE NOT RUNNING")
        print("Please start the servers using: python start_mcp_servers.py")
    print("="*60)

def check_claude_mcp_config():
    """Check if Claude MCP configuration exists and is valid"""
    config_path = "mcp_config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"\nClaude MCP Configuration: [OK] Found ({len(config.get('mcp_servers', []))} servers configured)")
            return True
        except Exception as e:
            print(f"\nClaude MCP Configuration: [ERROR] Invalid - {str(e)}")
            return False
    else:
        print(f"\nClaude MCP Configuration: [ERROR] Not found")
        return False

if __name__ == "__main__":
    display_mcp_status()
    check_claude_mcp_config()