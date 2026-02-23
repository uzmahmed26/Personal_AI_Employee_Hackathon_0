#!/usr/bin/env python3
"""Get LinkedIn Access Token via OAuth 2.0"""

import os
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID') or os.getenv('LINKEDIN_API_KEY')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET') or os.getenv('LINKEDIN_SECRET_KEY')
REDIRECT_URI = 'http://localhost:8000/auth/linkedin/callback'
SCOPES = 'openid profile email w_member_social'

auth_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = parse_qs(urlparse(self.path).query)
        if 'code' in params:
            auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h2>Authorization successful! Close this tab and go back to terminal.</h2>')
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'<h2>Error: no code received</h2>')

    def log_message(self, format, *args):
        pass  # Suppress server logs

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERROR: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET not found in .env")
    exit(1)

# Step 1: Open browser for authorization
auth_url = (
    "https://www.linkedin.com/oauth/v2/authorization?"
    + urlencode({
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    })
)

print("Opening LinkedIn authorization page in browser...")
print(f"URL: {auth_url}\n")
webbrowser.open(auth_url)

# Step 2: Wait for callback
print("Waiting for authorization... (allow in browser)")
server = HTTPServer(('localhost', 8000), CallbackHandler)
server.handle_request()

if not auth_code:
    print("ERROR: No authorization code received")
    exit(1)

# Step 3: Exchange code for token
print("\nExchanging code for access token...")
response = requests.post(
    "https://www.linkedin.com/oauth/v2/accessToken",
    data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    },
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

data = response.json()

if 'access_token' in data:
    print("\n" + "="*50)
    print("COPY THIS INTO YOUR .env FILE:")
    print("="*50)
    print(f"LINKEDIN_ACCESS_TOKEN={data['access_token']}")
    print("="*50)
    print(f"\nExpires in: {data.get('expires_in', '?')} seconds (~{int(data.get('expires_in',0))//86400} days)")
else:
    print(f"\nERROR: {data}")
