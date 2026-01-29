#!/usr/bin/env python3
"""
LinkedIn Poster for Personal AI Employee System

This script posts content to LinkedIn using the LinkedIn API.
Note: This requires LinkedIn API credentials and proper OAuth setup.
"""

import os
import time
import requests
from pathlib import Path
from datetime import datetime
import json
import glob
from typing import Dict, List, Optional

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
LINKEDIN_QUEUE_FOLDER = "Business/LinkedIn_Queue"
LINKEDIN_POSTED_FOLDER = "Business/LinkedIn_Queue/Posted"

# Convert to Path objects
queue_path = Path(VAULT_PATH) / LINKEDIN_QUEUE_FOLDER
posted_path = Path(VAULT_PATH) / LINKEDIN_POSTED_FOLDER

# LinkedIn API endpoints
LINKEDIN_API_BASE = "https://api.linkedin.com/v2"
LINKEDIN_OAUTH_URL = "https://www.linkedin.com/oauth/v2/accessToken"

class LinkedInPoster:
    def __init__(self):
        self.access_token = None
        self.person_urn = None
        self.organization_urn = None  # For company pages
        
        # Try to load credentials from environment or config file
        self.load_credentials()
    
    def load_credentials(self):
        """
        Load LinkedIn API credentials from environment variables or config file
        """
        # Try to load from environment variables first
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI', 'https://localhost')
        
        # Load access token if available
        token_file = Path(VAULT_PATH) / 'linkedin_token.json'
        if token_file.exists():
            try:
                with open(token_file, 'r') as f:
                    token_data = json.load(f)
                    self.access_token = token_data.get('access_token')
                    self.person_urn = token_data.get('person_urn')
            except Exception as e:
                print(f"Error loading LinkedIn token: {e}")
    
    def authenticate(self):
        """
        Authenticate with LinkedIn API using OAuth 2.0
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Authenticating with LinkedIn...")
        
        # Check if we already have a valid access token
        if self.access_token:
            if self.verify_token():
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Using existing LinkedIn token")
                return True
        
        # If no valid token, we need to authenticate
        print(f"[{datetime.now().strftime('%H:%M:%S')}] LinkedIn authentication required")
        print("Please follow these steps to set up LinkedIn API access:")
        print()
        print("1. Go to https://www.linkedin.com/developers/")
        print("2. Create a new app and note your Client ID and Client Secret")
        print("3. Add your redirect URI (typically 'https://localhost')")
        print("4. Add the following permissions: r_liteprofile, w_member_social")
        print("5. Set these environment variables:")
        print("   - LINKEDIN_CLIENT_ID=your_client_id")
        print("   - LINKEDIN_CLIENT_SECRET=your_client_secret")
        print("6. Visit this URL to get an authorization code:")
        print()
        
        if not self.client_id or not self.client_secret:
            print("❌ LinkedIn credentials not found. Please set environment variables.")
            return False
        
        # Construct the authorization URL
        auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization?" +
            f"client_id={self.client_id}&" +
            f"redirect_uri={self.redirect_uri}&" +
            f"response_type=code&" +
            f"scope=r_liteprofile,w_member_social"
        )
        
        print(f"🔗 {auth_url}")
        print()
        print("After authorizing, paste the code from the URL here:")
        
        auth_code = input("Authorization code: ")
        
        # Exchange the code for an access token
        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post(LINKEDIN_OAUTH_URL, data=token_data)
            response.raise_for_status()
            
            token_response = response.json()
            self.access_token = token_response['access_token']
            
            # Save the token for future use
            token_file = Path(VAULT_PATH) / 'linkedin_token.json'
            with open(token_file, 'w') as f:
                json.dump({
                    'access_token': self.access_token,
                    'expires_in': token_response.get('expires_in'),
                    'person_urn': self.get_person_urn()
                }, f)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] LinkedIn authentication successful!")
            return True
            
        except requests.RequestException as e:
            print(f"❌ Error authenticating with LinkedIn: {e}")
            return False
    
    def verify_token(self):
        """
        Verify if the current access token is still valid
        
        Returns:
            bool: True if token is valid, False otherwise
        """
        if not self.access_token:
            return False
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        try:
            response = requests.get(
                f"{LINKEDIN_API_BASE}/me",
                headers=headers
            )
            return response.status_code == 200
        except:
            return False
    
    def get_person_urn(self):
        """
        Get the person URN for the authenticated user
        
        Returns:
            str: Person URN or None if error
        """
        if not self.access_token:
            return None
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        try:
            response = requests.get(
                f"{LINKEDIN_API_BASE}/me",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('id')
        except Exception as e:
            print(f"Error getting person URN: {e}")
            return None
    
    def post_update(self, text: str, image_urls: List[str] = None):
        """
        Post an update to LinkedIn
        
        Args:
            text (str): Text content of the post
            image_urls (List[str]): Optional list of image URLs to include
            
        Returns:
            bool: True if post was successful, False otherwise
        """
        if not self.access_token:
            print("❌ No LinkedIn access token available")
            return False
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        # Prepare the post content
        post_data = {
            "author": f"urn:li:person:{self.person_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # If there are images, prepare media attachments
        if image_urls:
            media_values = []
            for url in image_urls:
                # For simplicity, we'll just reference the URL
                # In a real implementation, you'd need to upload the image first
                pass
            
            # Update the share media category
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
        
        try:
            response = requests.post(
                f"{LINKEDIN_API_BASE}/ugcPosts",
                headers=headers,
                json=post_data
            )
            
            if response.status_code == 201:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] LinkedIn post published successfully!")
                return True
            else:
                print(f"❌ Error posting to LinkedIn: {response.status_code} - {response.text}")
                return False
        except requests.RequestException as e:
            print(f"❌ Error posting to LinkedIn: {e}")
            return False
    
    def process_queue(self):
        """
        Process all posts in the LinkedIn queue
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing LinkedIn queue...")
        
        # Get all markdown files in the queue
        queue_files = list(queue_path.glob('*.md')) + list(queue_path.glob('*.txt'))
        
        if not queue_files:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No posts in LinkedIn queue")
            return
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(queue_files)} post(s) in queue")
        
        for post_file in queue_files:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing: {post_file.name}")
            
            try:
                # Read the post content
                with open(post_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple parsing - first line could be title, rest is content
                lines = content.strip().split('\n')
                if len(lines) > 1:
                    title = lines[0].strip('# ').strip()  # Remove markdown heading markers
                    text = '\n'.join(lines[1:]).strip()
                    
                    # If no title extracted, use the first 50 chars as title
                    if not title:
                        title = text[:50] + "..." if len(text) > 50 else text
                else:
                    title = "Untitled Post"
                    text = content
                
                # Combine title and text for the post
                full_text = f"{title}\n\n{text}" if title != text else text
                
                # Post to LinkedIn
                success = self.post_update(full_text)
                
                if success:
                    # Move to posted folder
                    posted_path.mkdir(parents=True, exist_ok=True)
                    posted_file = posted_path / post_file.name
                    post_file.rename(posted_file)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Moved {post_file.name} to Posted folder")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Failed to post {post_file.name}")
                    
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Error processing {post_file.name}: {e}")
    
    def run(self):
        """
        Main method to run the LinkedIn poster
        """
        print("="*60)
        print("LinkedIn Poster - Personal AI Employee System")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Queue: {queue_path}")
        print("="*60)
        
        # Authenticate with LinkedIn
        if not self.authenticate():
            print("❌ Unable to authenticate with LinkedIn. Exiting.")
            return
        
        # Process the queue
        self.process_queue()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] LinkedIn posting completed!")

def setup_directories():
    """
    Create required directories if they don't exist
    """
    directories = [queue_path, posted_path]

    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            print(f"📁 [{datetime.now().strftime('%H:%M:%S')}] Created directory: {directory}")

def main():
    """
    Main function to run the LinkedIn poster
    """
    # Setup required directories
    setup_directories()
    
    # Create and run the LinkedIn poster
    poster = LinkedInPoster()
    poster.run()

if __name__ == "__main__":
    main()