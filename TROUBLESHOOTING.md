# Troubleshooting Guide for Gmail Watcher

## Common Errors and Solutions

### 1. FileNotFoundError: credentials.json not found
**Problem:** The script can't find the credentials.json file.
**Solution:**
- Make sure you followed the setup guide to create and download credentials.json
- Verify the file is in the same directory as gmail_watcher.py
- Check the filename is exactly "credentials.json" (case-sensitive)

### 2. Authentication/Authorization Errors
**Problem:** Issues with OAuth authentication.
**Solutions:**
- Delete the `token.json` file and run the script again to re-authenticate
- Ensure your Google account has granted the necessary permissions
- Check that the Gmail API is enabled in Google Cloud Console

### 3. Network/Connection Errors
**Problem:** Cannot connect to Gmail API.
**Solutions:**
- Check your internet connection
- Verify firewall settings aren't blocking the connection
- Try increasing timeout values if on a slow connection

### 4. API Quota Limits
**Problem:** Receiving quota exceeded errors.
**Solutions:**
- The script is designed with a 60-second interval to respect quotas
- If you're still hitting limits, increase the CHECK_INTERVAL value in the script
- Note that free Gmail accounts have generous daily quotas (1 billion units/day)

### 5. Permission Errors
**Problem:** Script can't create files in the target directory.
**Solutions:**
- Verify you have write permissions to the vault directory
- Run the script with appropriate privileges if needed
- Check that the target directory exists

## Debugging Tips

### Enable Verbose Logging
Add the following to the script for more detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test API Connection
Create a simple test script to verify Gmail API access:
```python
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Load credentials
creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.readonly'])

# Build service
service = build('gmail', 'v1', credentials=creds)

# Test connection
profile = service.users().getProfile(userId='me').execute()
print(f"Connected to: {profile['emailAddress']}")
```

### Check Email Query
If emails aren't being detected, verify the search query:
- The script looks for emails that are BOTH "important" AND "unread"
- Manually check your Gmail to ensure you have such emails
- Try temporarily changing the query to just "is:unread" to test

## Re-authentication Process

If you need to re-authenticate:
1. Delete the `token.json` file
2. Run the script again
3. Follow the OAuth flow in your browser again

## API Quotas and Limits

- Gmail API has a default daily limit of 1 billion quota units
- Our script uses minimal quota by checking every 60 seconds
- Reading an email message consumes 1 quota unit
- The script uses 'minimal' format to reduce quota usage
- Free tier allows 250 quota units per user per second (much more than we use)

## Verification Steps

To verify everything is working:

1. Send yourself an email
2. Mark it as important in Gmail
3. Ensure it remains unread
4. Run the gmail_watcher.py script
5. Within 60 seconds, check the 01_Incoming_Tasks folder for a new email task
6. Verify the original email is now marked as read in Gmail

## Contact Support

If you continue to have issues:
- Double-check all steps in the setup guide
- Verify your Google Cloud Console project settings
- Ensure all required Python packages are installed
- Check that your credentials.json file is properly formatted