#!/usr/bin/env python3
"""Fetch Facebook Page ID using existing Page Access Token."""

import os, requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('FB_PAGE_ACCESS_TOKEN')
r = requests.get(f"https://graph.facebook.com/v18.0/me?fields=id,name&access_token={token}")
data = r.json()

if 'id' in data:
    print(f"Page Name : {data.get('name')}")
    print(f"FB_PAGE_ID: {data['id']}")
else:
    print(f"Error: {data}")
