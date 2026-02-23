#!/usr/bin/env python3
"""Run this once to get your Gmail refresh token."""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

print("\n" + "="*50)
print("COPY THESE INTO YOUR .env FILE:")
print("="*50)
print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
print(f"GMAIL_ACCESS_TOKEN={creds.token}")
print("="*50)
