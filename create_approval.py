#!/usr/bin/env python3
"""
Helper Script for Creating Approval Requests

This script provides functionality for AI employees or automation to create
approval requests that will be reviewed by humans. It generates unique IDs,
creates properly formatted files with frontmatter, and places them in the
appropriate directory for review.
"""

import os
import sys
import argparse
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import json
from typing import Dict, Any, Optional


# Configuration
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
PENDING_DIR = os.path.join(VAULT_PATH, "04_Approval_Workflows", "Pending")


def generate_approval_id():
    """Generate a unique approval ID using timestamp and UUID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_part = str(uuid.uuid4())[:8]  # Take first 8 chars of UUID
    return f"{timestamp}_{unique_part}"


def format_details_for_type(approval_type: str, data: Dict[str, Any]) -> str:
    """Format details section based on approval type."""
    if approval_type == 'email_draft':
        to_addr = data.get('to', 'N/A')
        subject = data.get('subject', 'N/A')
        body = data.get('body', 'N/A')
        
        details = f"""**To:** {to_addr}

**Subject:** {subject}

**Body:**
{body}
"""
    elif approval_type == 'payment':
        amount = data.get('amount', 'N/A')
        recipient = data.get('recipient', 'N/A')
        description = data.get('description', 'N/A')
        
        details = f"""**Amount:** {amount}

**Recipient:** {recipient}

**Description:** {description}
"""
    elif approval_type == 'social_post':
        platform = data.get('platform', 'N/A')
        content = data.get('content', 'N/A')
        hashtags = data.get('hashtags', [])
        
        details = f"""**Platform:** {platform}

**Content:**
{content}

**Hashtags:** {', '.join(hashtags) if hashtags else 'None'}
"""
    else:
        # Generic handler for other types
        details = "**Details:**\n"
        for key, value in data.items():
            details += f"\n**{key.replace('_', ' ').title()}:** {value}"
    
    return details


def format_proposed_action(approval_type: str, data: Dict[str, Any]) -> str:
    """Format the proposed action section based on approval type."""
    if approval_type == 'email_draft':
        to_addr = data.get('to', 'N/A')
        subject = data.get('subject', 'N/A')
        return f"Send an email to **{to_addr}** with the subject **'{subject}'**."
    elif approval_type == 'payment':
        amount = data.get('amount', 'N/A')
        recipient = data.get('recipient', 'N/A')
        return f"Process a payment of **{amount}** to **{recipient}**."
    elif approval_type == 'social_post':
        platform = data.get('platform', 'N/A')
        content_preview = data.get('content', '')[:50] + "..." if len(data.get('content', '')) > 50 else data.get('content', '')
        return f"Post content to **{platform}**: '{content_preview}'"
    else:
        return f"Perform action of type **{approval_type.replace('_', ' ').title()}**"


def create_approval_request(approval_type: str, data: Dict[str, Any], description: Optional[str] = None):
    """
    Create an approval request file.
    
    Args:
        approval_type: Type of approval (e.g., 'email_draft', 'payment', 'social_post')
        data: Dictionary containing all relevant data for the approval
        description: Optional custom description for the proposed action
    """
    # Generate unique ID
    approval_id = generate_approval_id()
    
    # Create metadata
    created_time = datetime.now().isoformat()
    expires_time = (datetime.now() + timedelta(hours=24)).isoformat()
    
    metadata = {
        'type': 'approval_request',
        'action': approval_type,
        'created': created_time,
        'expires': expires_time,
        'status': 'pending',
        'approval_id': approval_id
    }
    
    # Format the content
    frontmatter = yaml.dump(metadata, default_flow_style=False)
    
    proposed_action = description or format_proposed_action(approval_type, data)
    details = format_details_for_type(approval_type, data)
    
    content = f"""---
{frontmatter}---

## Proposed Action
{proposed_action}

## Details
{details}

## To Approve
Run: python approve.py approve {approval_id}.md

## To Reject
Run: python approve.py reject {approval_id}.md

## Auto-Expire
This approval will expire in 24 hours if not actioned.
"""
    
    # Ensure directory exists
    pending_dir = Path(PENDING_DIR)
    pending_dir.mkdir(parents=True, exist_ok=True)
    
    # Create file with unique name
    filename = f"{approval_id}.md"
    filepath = pending_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Approval request created: {filepath}")
    return str(filepath)


def main():
    parser = argparse.ArgumentParser(description="Create Approval Request Helper")
    
    parser.add_argument('--type', required=True, 
                       choices=['email_draft', 'payment', 'social_post'],
                       help="Type of approval request")
    parser.add_argument('--to', help="Email recipient (for email_draft)")
    parser.add_argument('--subject', help="Email subject (for email_draft)")
    parser.add_argument('--body', help="Email body (for email_draft)")
    parser.add_argument('--amount', help="Payment amount (for payment)")
    parser.add_argument('--recipient', help="Payment recipient (for payment)")
    parser.add_argument('--description', help="Payment description (for payment)")
    parser.add_argument('--platform', help="Social media platform (for social_post)")
    parser.add_argument('--content', help="Social media content (for social_post)")
    parser.add_argument('--hashtags', help="Comma-separated hashtags (for social_post)")
    
    args = parser.parse_args()
    
    # Build data dictionary based on type and provided arguments
    data = {}
    
    if args.type == 'email_draft':
        data['to'] = args.to or ''
        data['subject'] = args.subject or ''
        data['body'] = args.body or ''
    elif args.type == 'payment':
        data['amount'] = args.amount or ''
        data['recipient'] = args.recipient or ''
        data['description'] = args.description or ''
    elif args.type == 'social_post':
        data['platform'] = args.platform or ''
        data['content'] = args.content or ''
        if args.hashtags:
            data['hashtags'] = [tag.strip() for tag in args.hashtags.split(',')]
        else:
            data['hashtags'] = []
    
    # Validate required fields based on type
    if args.type == 'email_draft':
        if not args.to or not args.subject:
            print("Error: --to and --subject are required for email_draft")
            sys.exit(1)
    elif args.type == 'payment':
        if not args.amount or not args.recipient:
            print("Error: --amount and --recipient are required for payment")
            sys.exit(1)
    elif args.type == 'social_post':
        if not args.platform or not args.content:
            print("Error: --platform and --content are required for social_post")
            sys.exit(1)
    
    # Create the approval request
    create_approval_request(approval_type=args.type, data=data)


if __name__ == "__main__":
    main()