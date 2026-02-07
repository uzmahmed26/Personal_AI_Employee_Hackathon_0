import json
import requests

def test_context7_config():
    """Test if Context7 configuration is properly set up"""
    config_path = "MCP_SERVERS/context7_mcp/config.json"

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        api_key = config.get("api_config", {}).get("api_key")
        endpoint = config.get("api_config", {}).get("endpoint")

        print("Context7 MCP Configuration Test:")
        print(f"API Key present: {'Yes' if api_key else 'No'}")
        print(f"Endpoint: {endpoint}")

        if api_key and len(api_key) > 10:  # Basic validation
            print("[OK] API key appears to be properly configured")
        else:
            print("[ERROR] API key is missing or invalid")

        if endpoint and "context7" in endpoint:
            print("[OK] Endpoint appears to be correctly set")
        else:
            print("[ERROR] Endpoint is missing or incorrect")

        return bool(api_key and endpoint)

    except Exception as e:
        print(f"Error reading Context7 config: {e}")
        return False

def test_main_config():
    """Test if main MCP config has the Context7 entry with API key"""
    config_path = "mcp_config.json"

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        context7_server = None
        for server in config.get("mcp_servers", []):
            if server.get("name") == "context7":
                context7_server = server
                break

        if context7_server:
            env_vars = context7_server.get("env", {})
            api_key = env_vars.get("CONTEXT7_API_KEY")

            print("\nMain Configuration Test:")
            print(f"Context7 server found: Yes")
            print(f"API Key in main config: {'Yes' if api_key else 'No'}")

            if api_key and "ctx7sk-" in api_key:
                print("[OK] Context7 API key is properly set in main config")
                return True
            else:
                print("[ERROR] Context7 API key is missing or incorrect in main config")
                return False
        else:
            print("\nContext7 server not found in main config")
            return False

    except Exception as e:
        print(f"Error reading main config: {e}")
        return False

if __name__ == "__main__":
    config_ok = test_context7_config()
    main_config_ok = test_main_config()

    print(f"\nOverall Status: {'[SUCCESS] Configuration looks good' if config_ok and main_config_ok else '[ERROR] Configuration issues detected'}")