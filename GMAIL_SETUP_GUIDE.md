# Gmail API Setup Guide for Personal AI Employee

This guide will walk you through setting up Gmail API access for your Personal AI Employee system.

## Prerequisites

Before you begin, make sure you have:
- A Google account (Gmail address)
- Python 3.13 installed
- Administrative access to your computer

## Step 1: Enable Gmail API in Google Cloud Console

1. Open your web browser and navigate to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click on the project dropdown at the top of the page
4. Click "New Project" if you don't have an existing project
   - Give your project a name (e.g., "Personal-AI-Employee")
   - Click "Create"
5. Once your project is selected, click on the hamburger menu (three horizontal lines) in the top-left corner
6. Select "APIs & Services" > "Library"
7. In the search box, type "Gmail API"
8. Click on "Gmail API" when it appears in the search results
9. Click the "Enable" button

## Step 2: Create OAuth 2.0 Credentials

1. From the Gmail API page, click on "Manage" (or go to "APIs & Services" > "Credentials")
2. Click the "+ CREATE CREDENTIALS" button at the top
3. Select "OAuth client ID" from the dropdown
4. If prompted to configure the OAuth consent screen, click "Configure consent screen"
   - Select "External" and click "Create"
   - Fill in:
     - Application name: "Personal AI Employee"
     - User support email: your Gmail address
     - Developer contact information: your Gmail address
   - Click "Save and Continue"
   - On the scopes page, click "Save and Continue" (no scopes needed for this app)
   - On the test users page, add your Gmail address and click "Add"
   - Click "Save and Continue" then "Back to Dashboard"
5. Back on the credentials page, click "+ CREATE CREDENTIALS" again and select "OAuth client ID"
6. Choose "Desktop application" as the application type
7. Give it a name (e.g., "Personal AI Employee Desktop App")
8. Click "Create"
9. A dialog will appear with your client ID and secret
10. Click "Download" to save the credentials JSON file

## Step 3: Download credentials.json

1. After clicking download, you'll get a JSON file
2. Rename this file to `credentials.json`
3. Place it in your project directory: `C:\Users\laptop world\Desktop\Hack00\`

## Step 4: Install Required Python Packages

Open a command prompt or terminal and run:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

Or if you prefer to use a requirements.txt file:

```bash
# Create requirements.txt with the following content:
google-api-python-client
google-auth-httplib2
google-auth-oauthlib

# Then install:
pip install -r requirements.txt
```

## Step 5: First-Time Authentication Flow

When you run the gmail_watcher.py script for the first time:

1. The script will detect that there's no token file
2. It will prompt you to visit a URL in your browser
3. Log in to your Google account when prompted
4. Grant the requested permissions to the "Personal AI Employee" app
5. Copy the verification code shown after granting permissions
6. Paste it back into the command prompt where the script is running
7. The script will save your credentials for future use

## Security Notes

- Keep your `credentials.json` file secure and never share it
- The `token.json` file contains your access tokens - treat it as sensitive
- Both files should be added to your `.gitignore` if using version control
- If you suspect your credentials have been compromised, revoke the OAuth app in your Google Account settings and regenerate credentials

## Troubleshooting Common Issues

### Issue: "credentials.json not found"
- Solution: Make sure you downloaded the credentials file from Google Cloud Console and renamed it to `credentials.json`

### Issue: "Access Not Configured"
- Solution: Ensure you enabled the Gmail API in Google Cloud Console

### Issue: "Invalid Grant" or "Token has been expired"
- Solution: Delete the `token.json` file and run the script again to re-authenticate

### Issue: "Rate Limit Exceeded"
- Solution: The script is designed to check every 60 seconds to avoid this issue, but if you're still experiencing problems, increase the CHECK_INTERVAL in the script

## Verification Steps

After completing the setup:

1. Run the script: `python gmail_watcher.py`
2. Send yourself an email and mark it as important
3. Wait for the script to detect the email (within 60 seconds)
4. Check the `01_Incoming_Tasks` folder for the new email task file
5. Verify the email is marked as read in your Gmail inbox