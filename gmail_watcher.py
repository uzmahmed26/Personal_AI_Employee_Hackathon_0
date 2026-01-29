import os
import pickle
import time
import json
from datetime import datetime
import signal
import sys
from pathlib import Path

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
import httplib2

# Configuration constants - easily changeable
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
TASKS_FOLDER = "01_Incoming_Tasks"
CHECK_INTERVAL = 60  # seconds
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

# Convert to Path objects for easier manipulation
tasks_path = Path(VAULT_PATH) / TASKS_FOLDER

def authenticate_gmail():
    """
    Authenticate with Gmail API using OAuth 2.0
    
    Returns:
        service: Gmail API service object
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Authenticating with Gmail...")
    
    creds = None
    
    # Check if token file exists (stored credentials from previous runs)
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, ['https://www.googleapis.com/auth/gmail.readonly'])
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error loading token: {str(e)}")
    
    # If there are no valid credentials, initiate the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Refreshing credentials...")
                creds.refresh(Request())
            except RefreshError:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Token refresh failed. Need to re-authenticate.")
                # Delete the expired token file to force re-authentication
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                creds = None
        
        if not creds:
            # Check if credentials.json exists
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Credentials file '{CREDENTIALS_FILE}' not found. "
                    f"Please follow the setup instructions to create this file."
                )
            
            # Start the OAuth flow
            flow = Flow.from_client_secrets_file(
                CREDENTIALS_FILE,
                scopes=['https://www.googleapis.com/auth/gmail.readonly'],
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
            
            # Get authorization URL
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Please visit this URL to authorize the application:")
            print(auth_url)
            print()
            print(f"After authorizing, copy the verification code and paste it below:")
            
            # Get the authorization code from user
            code = input("Enter the verification code: ")
            
            # Exchange the code for credentials
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            # Save the credentials for next run
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
    
    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    
    # Get user info to confirm authentication
    try:
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile.get('emailAddress', 'Unknown')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Authentication successful!")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Connected to: {email_address}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error getting user profile: {str(e)}")
        raise
    
    return service

def get_unread_important_emails(service):
    """
    Fetch unread emails marked as important
    
    Args:
        service: Gmail API service object
    
    Returns:
        list: List of email objects with metadata
    """
    try:
        # Search for unread emails with 'important' label
        # Using 'is:important is:unread' query
        results = service.users().messages().list(
            userId='me',
            q='is:important is:unread',
            maxResults=10  # Limit to 10 emails per check to be respectful of API limits
        ).execute()
        
        messages = results.get('messages', [])
        
        # Get detailed information for each message
        emails = []
        for msg in messages:
            try:
                # Get the full message details
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='minimal'  # Use minimal format to save quota
                ).execute()
                
                # Extract headers and snippet
                headers = {}
                for header in message['payload'].get('headers', []):
                    headers[header['name']] = header['value']
                
                # Get the email snippet (preview text)
                snippet = message.get('snippet', '')
                
                # Create email data dictionary
                email_data = {
                    'id': message['id'],
                    'threadId': message['threadId'],
                    'from': headers.get('From', 'Unknown'),
                    'subject': headers.get('Subject', 'No Subject'),
                    'date': headers.get('Date', ''),
                    'snippet': snippet,
                    'labels': message.get('labelIds', [])
                }
                
                emails.append(email_data)
                
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Error processing email {msg['id']}: {str(e)}")
                continue
        
        return emails
    
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error fetching emails: {str(e)}")
        return []

def create_email_task(email_data):
    """
    Create a markdown task file for the email in the 01_Incoming_Tasks folder
    
    Args:
        email_data (dict): Dictionary containing email information
    """
    try:
        # Extract email details
        sender = email_data['from']
        subject = email_data['subject']
        snippet = email_data['snippet']
        email_id = email_data['id']
        date_str = email_data['date']
        
        # Parse the date string to a more usable format
        # Gmail date format is typically: "Wed, 15 Jan 2026 12:34:56 +0000"
        received_datetime = datetime.now()  # fallback
        try:
            # Parse the date string
            received_datetime = datetime.strptime(date_str.split(',')[1].strip().split('+')[0].strip(), '%d %b %Y %H:%M:%S')
        except:
            # If parsing fails, use current time
            pass
        
        # Format the date for the YAML frontmatter
        formatted_date = received_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Generate unique task ID using timestamp and email ID
        task_id = f"EMAIL_{received_datetime.strftime('%Y%m%d_%H%M%S')}_{email_id[:8]}"
        
        # Create the task filename
        task_filename = f"{task_id}.md"
        task_file_path = tasks_path / task_filename
        
        # Limit snippet to first 200 characters for preview
        preview_text = snippet[:200] + "..." if len(snippet) > 200 else snippet
        
        # Create the markdown content with YAML frontmatter
        markdown_content = f"""---
type: email
from: {sender}
subject: {subject}
received: {formatted_date}
priority: high
status: pending_review
email_id: {email_id}
---

## Email Received

**From:** {sender}  
**Subject:** {subject}  
**Received:** {received_datetime.strftime('%Y-%m-%d at %H:%M:%S')}

## Email Preview
{preview_text}

## Suggested Actions
- [ ] Read full email in Gmail
- [ ] Draft a reply
- [ ] Forward to relevant person
- [ ] Archive after handling
- [ ] Flag for follow-up

## Email Details
- **Gmail ID:** {email_id}
- **Labels:** {', '.join(email_data['labels'])}
- **Category:** Primary

---
*Email task created automatically by Gmail Watcher*
"""
        
        # Write the task file
        with open(task_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Task created: {task_filename}")
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error creating task for email {email_data.get('id', 'unknown')}: {str(e)}")

def mark_as_read(service, email_id):
    """
    Mark an email as read by removing the UNREAD label
    
    Args:
        service: Gmail API service object
        email_id (str): ID of the email to mark as read
    """
    try:
        # Modify the email labels to remove 'UNREAD'
        service.users().messages().modify(
            userId='me',
            id=email_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Email marked as read: {email_id[:8]}...")
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error marking email as read {email_id}: {str(e)}")

def setup_directories():
    """
    Create required directories if they don't exist
    """
    if not tasks_path.exists():
        tasks_path.mkdir(parents=True, exist_ok=True)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Created directory: {tasks_path}")

def signal_handler(sig, frame):
    """
    Handle graceful shutdown when Ctrl+C is pressed
    """
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Shutting down Gmail watcher...")
    print("Gmail watcher stopped successfully!")
    sys.exit(0)

def main():
    """
    Main function that runs the Gmail monitoring loop
    """
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Setup required directories
    setup_directories()
    
    # Print startup message
    print("="*60)
    print(f"Gmail Watcher - Personal AI Employee")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Vault: {VAULT_PATH}")
    print(f"Check Interval: {CHECK_INTERVAL} seconds")
    print("="*60)
    
    # Authenticate with Gmail
    try:
        service = authenticate_gmail()
    except FileNotFoundError as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {str(e)}")
        print("Please follow the setup instructions to configure Gmail API access.")
        return
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Authentication failed: {str(e)}")
        return
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting email monitoring...")
    
    # Set to keep track of processed email IDs to avoid duplicates
    processed_emails = set()
    
    # Main monitoring loop
    try:
        while True:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking for new important emails...")
            
            try:
                # Get unread important emails
                emails = get_unread_important_emails(service)
                
                if emails:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(emails)} unread important email(s)")
                    
                    # Process each email
                    for email_data in emails:
                        email_id = email_data['id']
                        
                        # Skip if we've already processed this email
                        if email_id in processed_emails:
                            continue
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing: \"{email_data['subject']}\" from {email_data['from']}")
                        
                        # Create a task file for this email
                        create_email_task(email_data)
                        
                        # Mark the email as read
                        mark_as_read(service, email_id)
                        
                        # Add to processed set to avoid duplicate processing
                        processed_emails.add(email_id)
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processed {len(emails)} email(s)")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] No new emails found")
            
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Error during email check: {str(e)}")
            
            # Wait for the specified interval before next check
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting {CHECK_INTERVAL} seconds before next check...")
            time.sleep(CHECK_INTERVAL)
    
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        signal_handler(None, None)

if __name__ == "__main__":
    main()