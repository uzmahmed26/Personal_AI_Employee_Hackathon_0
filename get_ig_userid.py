#!/usr/bin/env python3
"""Fetch Instagram Business Account ID linked to Facebook Page."""

import os, requests
from dotenv import load_dotenv

load_dotenv()

page_id    = os.getenv('FB_PAGE_ID')
page_token = os.getenv('FB_PAGE_ACCESS_TOKEN')

# Try to get Instagram account linked to the Facebook Page
url = f"https://graph.facebook.com/v18.0/{page_id}"
params = {
    "fields": "instagram_business_account,name",
    "access_token": page_token
}

r = requests.get(url, params=params)
data = r.json()

print(f"Page: {data.get('name', '?')}")

if 'instagram_business_account' in data:
    ig_id = data['instagram_business_account']['id']
    print(f"\nIG_USER_ID found: {ig_id}")
    print(f"\nAdd to .env: IG_USER_ID={ig_id}")
else:
    print("\nInstagram Business Account NOT linked to this Facebook Page.")
    print("\nTo fix:")
    print("1. Instagram app kholo")
    print("2. Settings -> Account -> Switch to Professional Account")
    print("3. Category select karo -> Business")
    print("4. Facebook Page se link karo (Settings -> Linked Accounts -> Facebook)")
    print("5. Phir yeh script dobara chalao")
