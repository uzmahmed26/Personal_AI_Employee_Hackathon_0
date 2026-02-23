#!/usr/bin/env python3
"""Test all connected services."""

import os, requests, time, hmac, hashlib, base64, random, string
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

results = {}

# 1. Gmail
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials(
        token=os.getenv('GMAIL_ACCESS_TOKEN'),
        refresh_token=os.getenv('GMAIL_REFRESH_TOKEN'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=os.getenv('GMAIL_CLIENT_ID'),
        client_secret=os.getenv('GMAIL_CLIENT_SECRET'),
    )
    svc = build('gmail', 'v1', credentials=creds)
    profile = svc.users().getProfile(userId='me').execute()
    results['Gmail'] = f"OK - {profile.get('emailAddress')}"
except Exception as e:
    results['Gmail'] = f"FAIL - {str(e)[:60]}"

# 2. LinkedIn
try:
    token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    r = requests.get("https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {token}"}, timeout=10)
    d = r.json()
    results['LinkedIn'] = f"OK - {d.get('name','?')} ({d.get('email','?')})"
except Exception as e:
    results['LinkedIn'] = f"FAIL - {str(e)[:60]}"

# 3. Facebook
try:
    token = os.getenv('FB_PAGE_ACCESS_TOKEN')
    page_id = os.getenv('FB_PAGE_ID')
    r = requests.get(f"https://graph.facebook.com/v18.0/{page_id}",
        params={"fields": "name,fan_count", "access_token": token}, timeout=10)
    d = r.json()
    if 'name' in d:
        results['Facebook'] = f"OK - Page: {d['name']} ({d.get('fan_count',0)} fans)"
    else:
        results['Facebook'] = f"FAIL - {d.get('error',{}).get('message','unknown')}"
except Exception as e:
    results['Facebook'] = f"FAIL - {str(e)[:60]}"

# 4. Twitter
try:
    API_KEY = os.getenv('TWITTER_API_KEY')
    API_SECRET = os.getenv('TWITTER_API_SECRET')
    AT = os.getenv('TWITTER_ACCESS_TOKEN')
    AT_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    timestamp = str(int(time.time()))
    url = "https://api.twitter.com/2/users/me"
    params = {"oauth_consumer_key": API_KEY, "oauth_nonce": nonce,
              "oauth_signature_method": "HMAC-SHA1", "oauth_timestamp": timestamp,
              "oauth_token": AT, "oauth_version": "1.0"}
    base = "&".join(["GET", quote(url, safe=""),
        quote("&".join(f"{quote(k,safe='')}={quote(v,safe='')}" for k,v in sorted(params.items())), safe="")])
    signing_key = f"{quote(API_SECRET,safe='')}&{quote(AT_SECRET,safe='')}"
    sig = base64.b64encode(hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()).decode()
    params["oauth_signature"] = sig
    auth_header = "OAuth " + ", ".join(f'{k}="{quote(v,safe="")}"' for k,v in sorted(params.items()))
    r = requests.get(url, headers={"Authorization": auth_header}, timeout=10)
    d = r.json()
    if 'data' in d:
        results['Twitter'] = f"OK - @{d['data']['username']}"
    else:
        results['Twitter'] = f"FAIL - {d.get('title','unknown')}"
except Exception as e:
    results['Twitter'] = f"FAIL - {str(e)[:60]}"

# 5. WhatsApp
try:
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    r = requests.get(f"https://graph.facebook.com/v18.0/{phone_id}",
        params={"access_token": token}, timeout=10)
    d = r.json()
    if 'id' in d:
        results['WhatsApp'] = f"OK - Number: {d.get('display_phone_number', d['id'])}"
    else:
        results['WhatsApp'] = f"FAIL - {d.get('error',{}).get('message','unknown')}"
except Exception as e:
    results['WhatsApp'] = f"FAIL - {str(e)[:60]}"

# 6. Instagram
ig_id = os.getenv('IG_USER_ID','')
if not ig_id or ig_id.startswith('your_'):
    results['Instagram'] = "SKIP - IG_USER_ID not set yet"
else:
    try:
        token = os.getenv('FB_PAGE_ACCESS_TOKEN')
        r = requests.get(f"https://graph.facebook.com/v18.0/{ig_id}",
            params={"fields": "username,name", "access_token": token}, timeout=10)
        d = r.json()
        results['Instagram'] = f"OK - @{d.get('username','?')}" if 'username' in d else f"FAIL - {d}"
    except Exception as e:
        results['Instagram'] = f"FAIL - {str(e)[:60]}"

# Print results
print("\n" + "="*50)
print("  SERVICE CONNECTION TEST RESULTS")
print("="*50)
for svc, status in results.items():
    icon = "OK  " if status.startswith("OK") else ("SKIP" if status.startswith("SKIP") else "FAIL")
    print(f"  [{icon}] {svc:12}: {status.split(' - ',1)[-1]}")
print("="*50)
