import subprocess
import sys
import os
from pathlib import Path

def start_mcp_server(server_name, server_path):
    """Start an MCP server as a subprocess"""
    try:
        print(f"Starting {server_name} server...")
        # Note: In a real implementation, you would start the actual server process
        # This is a placeholder implementation
        process = subprocess.Popen([
            sys.executable, "-c", 
            f"print('Starting {server_name} server...'); "
            f"input('Press Enter to stop {server_name} server...'); "
            f"print('{server_name} server stopped.')"
        ])
        return process
    except Exception as e:
        print(f"Failed to start {server_name} server: {e}")
        return None

def main():
    print("Starting all MCP servers for Personal AI Employee...")
    
    # Define server configurations
    servers = [
        {"name": "File System MCP", "path": "MCP_SERVERS/file_system_mcp"},
        {"name": "Gmail MCP", "path": "MCP_SERVERS/gmail_mcp"}, 
        {"name": "WhatsApp MCP", "path": "MCP_SERVERS/whatsapp_mcp"},
        {"name": "LinkedIn MCP", "path": "MCP_SERVERS/linkedin_mcp"},
        {"name": "Context 7 MCP", "path": "MCP_SERVERS/context7_mcp"}
    ]
    
    processes = []
    
    # Start all servers
    for server in servers:
        process = start_mcp_server(server["name"], server["path"])
        if process:
            processes.append((server["name"], process))
    
    print("\nAll MCP servers started successfully!")
    print("Press Ctrl+C to stop all servers...")
    
    try:
        # Keep the script running
        while True:
            pass
    except KeyboardInterrupt:
        print("\nStopping all MCP servers...")
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"{name} server stopped.")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"{name} server forcefully terminated.")
            except Exception as e:
                print(f"Error stopping {name} server: {e}")

if __name__ == "__main__":
    main()