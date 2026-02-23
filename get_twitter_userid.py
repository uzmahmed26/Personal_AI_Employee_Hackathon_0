#!/usr/bin/env python3
"""Fetch Twitter User ID using OAuth 1.0a."""

import os, time, hmac, hashlib, base64, requests
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

API_KEY    = os.getenv('TWITTER_API_KEY')
API_SECRET = os.getenv('TWITTER_API_SECRET')
AT         = os.getenv('TWITTER_ACCESS_TOKEN')
AT_SECRET  = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

if not all([API_KEY, API_SECRET, AT, AT_SECRET]):
    print("ERROR: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET missing in .env")
    exit(1)

import random, string
nonce     = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
timestamp = str(int(time.time()))
url       = "https://api.twitter.com/2/users/me"

params = {
    "oauth_consumer_key":     API_KEY,
    "oauth_nonce":            nonce,
    "oauth_signature_method": "HMAC-SHA1",
    "oauth_timestamp":        timestamp,
    "oauth_token":            AT,
    "oauth_version":          "1.0",
}

base = "&".join([
    "GET",
    quote(url, safe=""),
    quote("&".join(f"{quote(k,safe='')}={quote(v,safe='')}" for k,v in sorted(params.items())), safe="")
])
signing_key = f"{quote(API_SECRET, safe='')}&{quote(AT_SECRET, safe='')}"
sig = base64.b64encode(hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()).decode()
params["oauth_signature"] = sig

auth_header = "OAuth " + ", ".join(f'{k}="{quote(v,safe="")}"' for k,v in sorted(params.items()))

r = requests.get(url, headers={"Authorization": auth_header})
data = r.json()

if 'data' in data:
    print(f"Username       : @{data['data']['username']}")
    print(f"TWITTER_USER_ID: {data['data']['id']}")
    print(f"\nAdd to .env: TWITTER_USER_ID={data['data']['id']}")
else:
    print(f"Error: {data}")
