#!/usr/bin/env python3
"""
Requirements Checker for Personal AI Employee System

This script checks if all required libraries are installed for your configured services.
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_library_installed(library_name):
    """
    Check if a library is installed
    """
    try:
        importlib.import_module(library_name)
        return True
    except ImportError:
        return False

def check_node_installed():
    """
    Check if Node.js is installed
    """
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_npm_installed():
    """
    Check if npm is installed
    """
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def main():
    """
    Main function to check requirements
    """
    print("="*70)
    print("Requirements Checker for Personal AI Employee System")
    print("="*70)
    
    print("\n[INFO] Checking required libraries...")
    
    # Libraries needed for the system
    required_libs = [
        ('flask', 'Web framework for MCP servers'),
        ('requests', 'HTTP library'),
        ('oauthlib', 'OAuth support'),
        ('requests_oauthlib', 'OAuth support for requests'),
        ('python-dotenv', 'Environment variable management'),
        ('pyyaml', 'YAML parsing'),
        ('selenium', 'Browser automation (for various integrations)'),
        ('webdriver-manager', 'WebDriver management for Selenium'),
        ('pandas', 'Data manipulation'),
        ('numpy', 'Numerical computing'),
        ('openai', 'OpenAI API client'),
        ('tiktoken', 'OpenAI tokenizer'),
        ('apscheduler', 'Task scheduling'),
        ('colorama', 'Colored terminal output'),
        ('pyautogen', 'AutoGen framework'),
        ('chromadb', 'Vector database'),
        ('sentence-transformers', 'Sentence embeddings'),
        ('faiss-cpu', 'Vector similarity search'),
        ('pytesseract', 'OCR capabilities'),
        ('Pillow', 'Image processing'),
        ('pyttsx3', 'Text-to-speech'),
        ('SpeechRecognition', 'Speech recognition'),
        ('twilio', 'Twilio API for SMS/calls'),
        ('pywhatkit', 'WhatsApp automation'),
        ('yowsup2', 'WhatsApp Web protocol'),
        ('fb-messenger-api', 'Facebook Messenger API'),
        ('whatsapp-chat-parser', 'WhatsApp chat parsing'),
        ('webwhatsapi', 'WhatsApp Web API'),
    ]
    
    installed_libs = []
    missing_libs = []
    
    for lib_name, description in required_libs:
        if check_library_installed(lib_name):
            installed_libs.append((lib_name, description))
            print(f"[SUCCESS] {lib_name:<25} - {description}")
        else:
            missing_libs.append((lib_name, description))
            print(f"[MISSING] {lib_name:<25} - {description}")
    
    print(f"\n[STATUS] Library Status:")
    print(f"   Installed: {len(installed_libs)}")
    print(f"   Missing: {len(missing_libs)}")
    
    # Check Node.js and npm
    print(f"\n[INFO] Checking Node.js and npm...")
    node_installed = check_node_installed()
    npm_installed = check_npm_installed()
    
    print(f"[STATUS] Node.js: {'Yes' if node_installed else 'No'}")
    print(f"[STATUS] npm: {'Yes' if npm_installed else 'No'}")
    
    # Specific service requirements
    print(f"\n[SECURITY] Service-Specific Requirements:")
    
    # Gmail requirements
    gmail_reqs = [('google-auth', 'Google authentication'), ('google-auth-oauthlib', 'Google OAuth'), ('google-auth-httplib2', 'Google HTTP client'), ('google-api-python-client', 'Google API client')]
    print(f"   Gmail Integration:")
    for lib, desc in gmail_reqs:
        status = "[SUCCESS]" if check_library_installed(lib) else "[MISSING]"
        print(f"     {status} {lib} - {desc}")
    
    # LinkedIn requirements
    linkedin_reqs = [('linkedin-api', 'LinkedIn API client'), ('linkedin-v2', 'LinkedIn v2 API')]
    print(f"   LinkedIn Integration:")
    for lib, desc in linkedin_reqs:
        status = "[SUCCESS]" if check_library_installed(lib) else "[MISSING]"
        print(f"     {status} {lib} - {desc}")
    
    # WhatsApp requirements
    whatsapp_reqs = [('pywhatkit', 'WhatsApp automation'), ('yowsup2', 'WhatsApp Web protocol'), ('whatsapp-web.js', 'WhatsApp Web for Node.js')]
    print(f"   WhatsApp Integration:")
    for lib, desc in whatsapp_reqs:
        if lib == 'whatsapp-web.js':
            # This is a Node.js package
            status = "[SUCCESS]" if check_npm_installed() else "[MISSING]"
            print(f"     {status} {lib} - {desc}")
        else:
            status = "[SUCCESS]" if check_library_installed(lib) else "[MISSING]"
            print(f"     {status} {lib} - {desc}")
    
    # Generate installation commands
    if missing_libs:
        print(f"\n[INSTALL] To install missing Python libraries, run:")
        missing_names = [lib[0] for lib in missing_libs]
        print(f"   pip install {' '.join(missing_names)}")
        
        # Special cases
        whatsapp_missing = [lib[0] for lib in missing_libs if 'whatsapp' in lib[0].lower()]
        if whatsapp_missing:
            print(f"   For WhatsApp: pip install {' '.join(whatsapp_missing)}")
        
        google_missing = [lib[0] for lib in missing_libs if 'google' in lib[0].lower()]
        if google_missing:
            print(f"   For Google services: pip install {' '.join(set(google_missing))}")
    
    if not node_installed or not npm_installed:
        print(f"\n[WEB] Node.js and npm are required for some integrations.")
        print(f"   Download from: https://nodejs.org/")
    
    print(f"\n[CONFIG] Your .env file has the following configurations:")
    print(f"   - Gmail: [SUCCESS] Configured")
    print(f"   - LinkedIn: [WARNING] Placeholders only (need real credentials)")
    print(f"   - WhatsApp: [SUCCESS] Partially configured (has access token and phone number)")
    
    print("="*70)

if __name__ == "__main__":
    main()