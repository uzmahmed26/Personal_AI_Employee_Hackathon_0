#!/usr/bin/env python3
"""Quick test - verify LinkedIn connection."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('LINKEDIN_ACCESS_TOKEN')
if not token:
    print("ERROR: LINKEDIN_ACCESS_TOKEN not found in .env")
    exit(1)

headers = {"Authorization": f"Bearer {token}", "X-Restli-Protocol-Version": "2.0.0"}

# Get profile
r = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
data = r.json()

if 'sub' in data:
    print("LinkedIn connected!")
    print(f"  Name : {data.get('name', '?')}")
    print(f"  Email: {data.get('email', '?')}")
    print(f"  ID   : {data.get('sub', '?')}")
else:
    print(f"ERROR: {data}")
