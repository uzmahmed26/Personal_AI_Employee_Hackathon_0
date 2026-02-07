#!/usr/bin/env python3
"""
WhatsApp Configuration Validator for Personal AI Employee System

This script validates WhatsApp configuration in the .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def validate_whatsapp_config():
    """
    Validate WhatsApp configuration in .env file
    """
    print("[INFO] Validating WhatsApp configuration...")
    
    # Load environment variables from .env file
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[SUCCESS] Loaded .env file from: {env_path}")
    else:
        print(f"[ERROR] .env file not found at: {env_path}")
        return False
    
    # Define required WhatsApp environment variables
    whatsapp_vars = {
        'WHATSAPP_PHONE_NUMBER': 'Your WhatsApp phone number',
        'WHATSAPP_SESSION_FILE': 'Path to WhatsApp session file',
        'WHATSAPP_TOKEN': 'WhatsApp token/API key',
        'WHATSAPP_API_KEY': 'WhatsApp API key',
        'WHATSAPP_CLIENT_ID': 'WhatsApp client ID',
        'WHATSAPP_CLIENT_SECRET': 'WhatsApp client secret',
        'WHATSAPP_BUSINESS_ACCOUNT_ID': 'WhatsApp Business Account ID',
        'WHATSAPP_ACCESS_TOKEN': 'WhatsApp Access Token'
    }
    
    found_vars = {}
    missing_vars = []
    
    for var, description in whatsapp_vars.items():
        value = os.getenv(var)
        if value:
            found_vars[var] = value
        else:
            missing_vars.append(var)
    
    print(f"\n[STATUS] WhatsApp Configuration Status:")
    print(f"   Found variables: {len(found_vars)}")
    print(f"   Missing variables: {len(missing_vars)}")
    
    if found_vars:
        print(f"\n[SUCCESS] Found WhatsApp variables:")
        for var, value in found_vars.items():
            # Mask sensitive values
            if 'TOKEN' in var or 'KEY' in var or 'SECRET' in var or 'PASSWORD' in var:
                masked_value = '*' * min(len(value), 20)
                print(f"   {var}={masked_value}")
            else:
                print(f"   {var}={value}")
    
    if missing_vars:
        print(f"\n[ERROR] Missing WhatsApp variables:")
        for var in missing_vars:
            print(f"   - {var}")
    
    # Determine if WhatsApp is properly configured
    essential_vars = ['WHATSAPP_PHONE_NUMBER']
    essential_found = all(os.getenv(var) for var in essential_vars)
    
    if essential_found and found_vars:
        print(f"\n[SUCCESS] WhatsApp appears to be configured with essential variables")
        return True
    else:
        print(f"\n[ERROR] WhatsApp is not properly configured. Essential variables missing: {missing_vars}")
        return False

def check_whatsapp_integration_availability():
    """
    Check if WhatsApp integration libraries are available
    """
    print(f"\n[INFO] Checking WhatsApp integration libraries...")
    
    available_libs = []
    unavailable_libs = []
    
    whatsapp_libs = [
        ('pywhatkit', 'Simple WhatsApp automation'),
        ('yowsup', 'WhatsApp Web protocol implementation'),
        ('whatsapp-web.js', 'Node.js wrapper for WhatsApp Web'),
        ('selenium', 'Browser automation for WhatsApp Web')
    ]
    
    for lib_name, description in whatsapp_libs:
        try:
            if lib_name == 'whatsapp-web.js':
                # This is a Node.js library, check differently
                import subprocess
                result = subprocess.run(['node', '-e', 'require("whatsapp-web.js")'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    available_libs.append((lib_name, description))
                else:
                    unavailable_libs.append((lib_name, description))
            else:
                __import__(lib_name)
                available_libs.append((lib_name, description))
        except ImportError:
            unavailable_libs.append((lib_name, description))
        except Exception:
            unavailable_libs.append((lib_name, description))
    
    if available_libs:
        print("[SUCCESS] Available libraries:")
        for lib_name, desc in available_libs:
            print(f"   - {lib_name}: {desc}")
    
    if unavailable_libs:
        print("[WARNING] Unavailable libraries (install with pip/npm):")
        for lib_name, desc in unavailable_libs:
            print(f"   - {lib_name}: {desc}")
    
    return len(available_libs) > 0

def main():
    """
    Main function to validate WhatsApp configuration
    """
    print("="*70)
    print("WhatsApp Configuration Validator")
    print("="*70)
    
    # Validate configuration
    config_valid = validate_whatsapp_config()
    
    # Check library availability
    libs_available = check_whatsapp_integration_availability()
    
    print(f"\n[STATUS] WhatsApp Integration Status:")
    print(f"   Configuration: {'Valid' if config_valid else 'Invalid'}")
    print(f"   Libraries: {'Available' if libs_available else 'Not Available'}")
    
    if config_valid and libs_available:
        print(f"\n[SUCCESS] WhatsApp is properly configured and ready to use!")
        print("   You can now implement WhatsApp messaging functionality.")
    elif config_valid:
        print(f"\n[WARNING] WhatsApp is configured but lacks required libraries.")
        print("   Install required libraries to enable WhatsApp functionality.")
    elif libs_available:
        print(f"\n[WARNING] Libraries are available but WhatsApp is not configured.")
        print("   Add WhatsApp credentials to your .env file.")
    else:
        print(f"\n[ERROR] WhatsApp is not configured and required libraries are missing.")
        print("   1. Install required libraries")
        print("   2. Add WhatsApp credentials to your .env file")
    
    print("="*70)

if __name__ == "__main__":
    main()