import requests
import json

def test_context7_server():
    """Test if the Context7 MCP server is responding properly"""
    
    # Test the health endpoint
    try:
        health_response = requests.get('http://localhost:8080/')
        print(f"Health endpoint status: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"Server healthy: {health_data.get('status') == 'healthy'}")
            print(f"Service: {health_data.get('service')}")
            print(f"Version: {health_data.get('version')}")
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
    
    # Test the MCP info endpoint
    try:
        mcp_response = requests.get('http://localhost:8080/.well-known/mcp-info')
        print(f"\nMCP Info endpoint status: {mcp_response.status_code}")
        if mcp_response.status_code == 200:
            mcp_data = mcp_response.json()
            print(f"Server name: {mcp_data.get('name')}")
            print(f"Description: {mcp_data.get('description')}")
            print(f"Capabilities: {len(mcp_data.get('capabilities', []))}")
            
            # Check if capabilities match expectations
            cap_names = [cap['name'] if isinstance(cap, dict) else cap for cap in mcp_data.get('capabilities', [])]
            expected_caps = ['context_analysis', 'data_retrieval', 'information_processing', 'knowledge_base_query']
            all_present = all(cap in cap_names for cap in expected_caps)
            print(f"All expected capabilities present: {all_present}")
            
            return mcp_response.status_code == 200 and all_present
    except Exception as e:
        print(f"Error testing MCP info endpoint: {e}")
    
    return False

if __name__ == "__main__":
    print("Testing Context7 MCP Server...")
    is_working = test_context7_server()
    print(f"\nContext7 MCP Server Status: {'WORKING' if is_working else 'NOT WORKING'}")