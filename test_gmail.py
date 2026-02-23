#!/usr/bin/env python3
"""Quick test — reads last 5 Gmail emails to verify connection."""

import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

creds = Credentials(
    token=os.getenv('GMAIL_ACCESS_TOKEN'),
    refresh_token=os.getenv('GMAIL_REFRESH_TOKEN'),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=os.getenv('GMAIL_CLIENT_ID'),
    client_secret=os.getenv('GMAIL_CLIENT_SECRET'),
)

service = build('gmail', 'v1', credentials=creds)
results = service.users().messages().list(userId='me', maxResults=5).execute()
messages = results.get('messages', [])

print(f"\nGmail connected! Found {len(messages)} recent messages.")
for msg in messages:
    detail = service.users().messages().get(userId='me', id=msg['id'], format='metadata',
        metadataHeaders=['Subject','From']).execute()
    headers = {h['name']: h['value'] for h in detail['payload']['headers']}
    print(f"  - From: {headers.get('From','?')[:40]}")
    print(f"    Subject: {headers.get('Subject','(no subject)')[:50]}")
