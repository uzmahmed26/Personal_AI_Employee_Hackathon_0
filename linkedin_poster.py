#!/usr/bin/env python3
"""
LinkedIn Poster Automation Script

This script automatically posts scheduled content to LinkedIn using browser automation.
It watches a designated folder for .md files with scheduling information and posts
them when the scheduled time arrives.
"""

import os
import sys
import time
import asyncio
import argparse
import yaml
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from playwright.async_api import async_playwright
import re


# Configuration
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
QUEUE_FOLDER = os.path.join(VAULT_PATH, "Business", "LinkedIn_Queue")
POSTED_FOLDER = os.path.join(VAULT_PATH, "Business", "LinkedIn_Queue", "Posted")
SESSION_FOLDER = os.path.join(VAULT_PATH, "linkedin_session")
CHECK_INTERVAL = 300  # 5 minutes
HEADLESS = True  # False for debugging
MAX_POSTS_PER_HOUR = 5
CHARACTER_LIMIT = 3000  # LinkedIn character limit


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(VAULT_PATH, 'Logs', 'linkedin_poster.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class LinkedInPoster:
    def __init__(self, headless: bool = HEADLESS):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.posts_this_hour = 0
        self.last_hour = datetime.now().hour
        
    async def setup_session(self):
        """Setup LinkedIn session by allowing manual login."""
        logger.info("Setting up LinkedIn session. Please log in to LinkedIn.")
        logger.info("After logging in, close the browser to save the session.")

        async with async_playwright() as p:
            # Create a persistent context with session storage
            self.context = await p.chromium.launch_persistent_context(
                SESSION_FOLDER,
                headless=False,  # Always visible during setup
                viewport={'width': 1280, 'height': 800}
            )

            self.page = await self.context.new_page()
            await self.page.goto("https://www.linkedin.com")

            # Wait for user to manually log in
            print("Please log in to LinkedIn in the opened browser.")
            print("After you have successfully logged in, press Ctrl+C in this terminal to continue...")
            try:
                # Keep the script running until interrupted
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Interrupt received. Closing browser and saving session...")

            # Close the context to save session
            await self.context.close()

        logger.info("LinkedIn session saved successfully.")

    async def load_session(self):
        """Load existing LinkedIn session."""
        try:
            async with async_playwright() as p:
                # Create a persistent context with saved session
                self.context = await p.chromium.launch_persistent_context(
                    SESSION_FOLDER,
                    headless=self.headless,
                    viewport={'width': 1280, 'height': 800}
                )
                
                self.page = await self.context.new_page()
                
                # Navigate to LinkedIn to verify session
                await self.page.goto("https://www.linkedin.com/feed/")
                await self.page.wait_for_timeout(2000)
                
                # Check if we're still logged in by looking for elements that appear when logged in
                try:
                    # Look for the create post button to verify login
                    await self.page.wait_for_selector("button[aria-label='Create a post']", timeout=5000)
                    logger.info("Successfully loaded LinkedIn session.")
                    return True
                except:
                    logger.error("Session may have expired. Please run with --setup to log in again.")
                    return False
                    
        except Exception as e:
            logger.error(f"Error loading LinkedIn session: {str(e)}")
            return False

    async def navigate_to_create_post(self):
        """Navigate to the LinkedIn create post page."""
        try:
            # Try multiple ways to get to the create post page
            # Method 1: Using the main create post button
            try:
                create_button = await self.page.wait_for_selector(
                    "button[aria-label='Create a post']",
                    timeout=10000
                )
                await create_button.click()
                await self.page.wait_for_timeout(2000)
                return True
            except:
                pass
            
            # Method 2: Using the share box
            try:
                share_box = await self.page.wait_for_selector(
                    "div[role='textbox'][aria-label*='share']",
                    timeout=5000
                )
                await share_box.click()
                await self.page.wait_for_timeout(2000)
                return True
            except:
                pass
                
            # Method 3: Using the navigation menu
            try:
                nav_item = await self.page.wait_for_selector(
                    "nav li a[href='/feed/']",
                    timeout=5000
                )
                await nav_item.click()
                await self.page.wait_for_timeout(1000)
                
                create_button = await self.page.wait_for_selector(
                    "button[aria-label='Create a post']",
                    timeout=5000
                )
                await create_button.click()
                await self.page.wait_for_timeout(2000)
                return True
            except:
                pass
                
            logger.error("Could not find create post button. LinkedIn UI may have changed.")
            return False
            
        except Exception as e:
            logger.error(f"Error navigating to create post: {str(e)}")
            return False

    async def post_content(self, content: str):
        """Post content to LinkedIn."""
        try:
            # Check rate limit
            current_hour = datetime.now().hour
            if current_hour != self.last_hour:
                self.posts_this_hour = 0
                self.last_hour = current_hour
            
            if self.posts_this_hour >= MAX_POSTS_PER_HOUR:
                logger.warning(f"Rate limit reached: {MAX_POSTS_PER_HOUR} posts this hour. Skipping post.")
                return False
            
            # Truncate content if too long
            if len(content) > CHARACTER_LIMIT:
                logger.warning(f"Post content exceeds LinkedIn's character limit ({CHARACTER_LIMIT}). Truncating...")
                content = content[:CHARACTER_LIMIT]
            
            # Navigate to create post
            if not await self.navigate_to_create_post():
                return False
            
            # Find the content editor and paste content
            try:
                # Wait for the content editor to be available
                content_editor = await self.page.wait_for_selector(
                    "div[contenteditable='true'][data-testid='post-content']",
                    timeout=10000
                )
                
                # Clear any existing content and paste new content
                await content_editor.focus()
                await self.page.keyboard.press("Control+A")  # Select all
                await self.page.keyboard.press("Delete")    # Delete selected
                await content_editor.fill(content)
                
                await self.page.wait_for_timeout(1000)
            except:
                # Alternative selector for content editor
                try:
                    content_editor = await self.page.wait_for_selector(
                        "div[contenteditable='true'][aria-label*='Share your insight']",
                        timeout=5000
                    )
                    
                    await content_editor.focus()
                    await self.page.keyboard.press("Control+A")
                    await self.page.keyboard.press("Delete")
                    await content_editor.fill(content)
                    
                    await self.page.wait_for_timeout(1000)
                except:
                    logger.error("Could not find content editor. LinkedIn UI may have changed.")
                    return False
            
            # Click the post button
            try:
                post_button = await self.page.wait_for_selector(
                    "button[aria-label='Post'][type='submit']",
                    timeout=10000
                )
                
                # Scroll to make sure button is visible
                await post_button.scroll_into_view_if_needed()
                await self.page.wait_for_timeout(500)
                
                # Click the post button
                await post_button.click()
                
                # Wait for post to be submitted
                await self.page.wait_for_timeout(3000)
                
                # Check if post was successful by looking for confirmation
                try:
                    # Look for elements that indicate the post was published
                    await self.page.wait_for_selector(
                        "article[data-id]", 
                        timeout=5000
                    )
                    logger.info("Post successfully published to LinkedIn!")
                    self.posts_this_hour += 1
                    return True
                except:
                    # If we can't confirm the post, assume it worked after waiting
                    logger.info("Post likely published to LinkedIn (could not confirm).")
                    self.posts_this_hour += 1
                    return True
                    
            except Exception as e:
                logger.error(f"Error clicking post button: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Error posting content to LinkedIn: {str(e)}")
            return False

    async def close(self):
        """Close the browser context."""
        if self.context:
            await self.context.close()

    def check_schedule_validity(self, scheduled_time_str: str) -> bool:
        """Check if the scheduled time is valid (not in the past)."""
        try:
            scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
            current_time = datetime.now(scheduled_time.tzinfo) if scheduled_time.tzinfo else datetime.now()
            return scheduled_time <= current_time
        except:
            logger.error(f"Invalid scheduled time format: {scheduled_time_str}")
            return False


async def process_queue():
    """Process the LinkedIn post queue."""
    poster = LinkedInPoster(headless=HEADLESS)
    
    try:
        # Load session
        if not await poster.load_session():
            logger.error("Failed to load LinkedIn session. Please run with --setup to log in.")
            return
        
        # Get all .md files in the queue folder
        queue_path = Path(QUEUE_FOLDER)
        if not queue_path.exists():
            logger.info(f"Queue folder does not exist: {QUEUE_FOLDER}. Creating it...")
            queue_path.mkdir(parents=True, exist_ok=True)
            return
        
        md_files = list(queue_path.glob("*.md"))
        
        for file_path in md_files:
            try:
                # Read the file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse frontmatter
                if content.startswith('---'):
                    end_frontmatter = content.find('---', 3)
                    if end_frontmatter != -1:
                        frontmatter = content[3:end_frontmatter].strip()
                        post_content = content[end_frontmatter + 3:].strip()
                        
                        try:
                            metadata = yaml.safe_load(frontmatter)
                            
                            # Check if this is a LinkedIn post
                            if metadata.get('type') != 'linkedin_post':
                                continue
                            
                            # Check status - only process pending posts
                            if metadata.get('status') != 'pending':
                                continue
                            
                            # Check if scheduled time has arrived
                            scheduled_for = metadata.get('scheduled_for')
                            if not scheduled_for:
                                logger.warning(f"No scheduled_for time in {file_path.name}. Skipping.")
                                continue
                            
                            if not poster.check_schedule_validity(scheduled_for):
                                logger.info(f"Scheduled time not yet arrived for {file_path.name}. Skipping.")
                                continue
                            
                            # Post the content
                            success = await poster.post_content(post_content)
                            
                            if success:
                                # Update metadata
                                metadata['status'] = 'posted'
                                metadata['posted_at'] = datetime.now().isoformat()
                                
                                # Rewrite the file with updated metadata
                                updated_frontmatter = yaml.dump(metadata, default_flow_style=False)
                                updated_content = f"---\n{updated_frontmatter}---\n\n{post_content}"
                                
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(updated_content)
                                
                                # Move file to posted folder
                                posted_path = Path(POSTED_FOLDER)
                                posted_path.mkdir(parents=True, exist_ok=True)
                                new_file_path = posted_path / file_path.name
                                file_path.rename(new_file_path)
                                
                                logger.info(f"Successfully processed and moved {file_path.name} to Posted folder.")
                            else:
                                logger.error(f"Failed to post {file_path.name}. See logs above.")
                                
                        except yaml.YAMLError as e:
                            logger.error(f"Error parsing YAML frontmatter in {file_path.name}: {str(e)}")
                    else:
                        logger.warning(f"Invalid frontmatter format in {file_path.name}")
                else:
                    logger.warning(f"No frontmatter found in {file_path.name}")
                    
            except Exception as e:
                logger.error(f"Error processing file {file_path.name}: {str(e)}")
    
    finally:
        await poster.close()


async def main():
    global HEADLESS

    parser = argparse.ArgumentParser(description="LinkedIn Poster Automation")
    parser.add_argument('--setup', action='store_true', help='Setup LinkedIn session with manual login')
    parser.add_argument('--headless', action='store_true', default=not HEADLESS,
                       help='Run in headless mode (default: %s)' % HEADLESS)
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode for testing')

    args = parser.parse_args()

    HEADLESS = args.headless
    
    # Create required directories
    Path(QUEUE_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(POSTED_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(SESSION_FOLDER).mkdir(parents=True, exist_ok=True)
    
    # Setup mode
    if args.setup:
        poster = LinkedInPoster(headless=False)  # Always visible during setup
        await poster.setup_session()
        await poster.close()
        return
    
    # Dry run mode
    if args.dry_run:
        logger.info("Running in DRY RUN mode. No actual posts will be made.")
        queue_path = Path(QUEUE_FOLDER)
        if not queue_path.exists():
            logger.info(f"Queue folder does not exist: {QUEUE_FOLDER}")
            return
        
        md_files = list(queue_path.glob("*.md"))
        logger.info(f"Found {len(md_files)} files in queue:")
        for file_path in md_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.startswith('---'):
                end_frontmatter = content.find('---', 3)
                if end_frontmatter != -1:
                    frontmatter = content[3:end_frontmatter].strip()
                    try:
                        metadata = yaml.safe_load(frontmatter)
                        if metadata.get('type') == 'linkedin_post' and metadata.get('status') == 'pending':
                            scheduled_for = metadata.get('scheduled_for', 'N/A')
                            logger.info(f"  - {file_path.name} (scheduled: {scheduled_for})")
                    except yaml.YAMLError:
                        logger.error(f"  - {file_path.name} (invalid YAML)")
        return
    
    # Normal operation - run continuously
    logger.info("Starting LinkedIn poster. Checking queue every 5 minutes...")
    logger.info(f"Queue folder: {QUEUE_FOLDER}")
    logger.info(f"Posted folder: {POSTED_FOLDER}")
    
    while True:
        try:
            await process_queue()
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
        
        logger.info(f"Waiting {CHECK_INTERVAL} seconds before next check...")
        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    # Install playwright browsers if not already installed
    import subprocess
    import sys
    
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        logger.warning("Failed to install Playwright browsers. Make sure to install them manually.")
    
    asyncio.run(main())