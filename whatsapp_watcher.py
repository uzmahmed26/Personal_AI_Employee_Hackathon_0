#!/usr/bin/env python3
"""
WhatsApp Watcher — Personal AI Employee System

Monitors WhatsApp for incoming messages and converts them into task files
in Needs_Action/ for Claude to process.

Two modes:
  1. Webhook mode (production): Receives messages via the WhatsApp MCP server
     webhook endpoint. Run whatsapp_mcp_server.py alongside this watcher.
  2. Queue file mode (development/fallback): Reads message JSON files dropped
     into Inbox/whatsapp_queue/ by external tools.

Environment variables (set in .env):
  WHATSAPP_ACCESS_TOKEN       — Meta Cloud API bearer token
  WHATSAPP_PHONE_NUMBER_ID    — Your WhatsApp Business phone number ID
  WHATSAPP_WEBHOOK_VERIFY_TOKEN
  WHATSAPP_KEYWORDS           — Comma-separated keywords to flag (default: urgent,invoice,payment,help,asap)

Usage:
  python whatsapp_watcher.py
"""

import os
import json
import re
import time
from pathlib import Path
from datetime import datetime
from typing import List

# Load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from base_watcher import BaseWatcher

VAULT_PATH = Path(__file__).parent

# Keywords that flag a WhatsApp message as requiring action
DEFAULT_KEYWORDS = ["urgent", "asap", "invoice", "payment", "help", "price",
                    "quote", "contract", "deadline", "emergency", "confirm"]


class WhatsAppWatcher(BaseWatcher):
    """
    Watcher that monitors WhatsApp messages and creates action tasks.

    In queue-file mode it reads JSON files from Inbox/whatsapp_queue/ that
    follow the Meta webhook payload format (or a simplified version).

    In webhook integration mode it reads from the shared queue file written
    by whatsapp_mcp_server.py.
    """

    def __init__(self, vault_path: str = str(VAULT_PATH), check_interval: int = 30):
        super().__init__(vault_path, check_interval=check_interval)

        # Queue directories
        self.queue_dir = self.inbox / "whatsapp_queue"
        self.queue_dir.mkdir(parents=True, exist_ok=True)

        # Shared queue file written by the MCP webhook server
        self.webhook_queue_file = self.vault_path / "Inbox" / "whatsapp_incoming.json"

        # Keywords that flag a message as requiring action
        keywords_env = os.getenv("WHATSAPP_KEYWORDS", "")
        if keywords_env:
            self.keywords = [k.strip().lower() for k in keywords_env.split(",") if k.strip()]
        else:
            self.keywords = DEFAULT_KEYWORDS

        self.logger.info(f"WhatsApp Watcher initialized. Monitoring: {self.queue_dir}")
        self.logger.info(f"Keywords: {', '.join(self.keywords)}")

    # ── BaseWatcher implementation ────────────────────────────────────────────

    def check_for_updates(self) -> List[dict]:
        """
        Check for new WhatsApp messages from two sources:
          1. JSON files in Inbox/whatsapp_queue/ (dropped by automation or tests)
          2. whatsapp_incoming.json shared queue file (from MCP webhook server)

        Returns:
            List of message dicts not yet processed.
        """
        messages = []

        # Source 1: Individual JSON files in queue dir
        for json_file in sorted(self.queue_dir.glob("*.json")):
            if json_file.stem in self._processed_ids:
                continue
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Handle both single message and list of messages
                if isinstance(data, list):
                    for msg in data:
                        msg["_source_file"] = str(json_file)
                        messages.append(msg)
                else:
                    data["_source_file"] = str(json_file)
                    messages.append(data)
                self._processed_ids.add(json_file.stem)
                # Move to Done after reading
                done_path = self.done / json_file.name
                json_file.rename(done_path)
            except Exception as e:
                self.logger.error(f"Error reading queue file {json_file.name}: {e}")

        # Source 2: Shared webhook queue file
        if self.webhook_queue_file.exists():
            try:
                with open(self.webhook_queue_file, "r", encoding="utf-8") as f:
                    queue_data = json.load(f)

                pending = queue_data if isinstance(queue_data, list) else queue_data.get("pending", [])
                new_messages = []
                processed = []

                for msg in pending:
                    msg_id = msg.get("id") or msg.get("wamid") or str(hash(json.dumps(msg, sort_keys=True)))
                    if msg_id not in self._processed_ids:
                        msg["_msg_id"] = msg_id
                        new_messages.append(msg)
                        processed.append(msg_id)

                if new_messages:
                    messages.extend(new_messages)
                    # Clear processed messages from queue file
                    remaining = [m for m in pending
                                 if (m.get("id") or m.get("wamid") or str(hash(json.dumps(m, sort_keys=True)))) not in processed]
                    with open(self.webhook_queue_file, "w", encoding="utf-8") as f:
                        json.dump({"pending": remaining}, f, indent=2)
                    self._processed_ids.update(processed)

            except Exception as e:
                self.logger.error(f"Error reading webhook queue: {e}")

        return messages

    def create_action_file(self, item: dict) -> Path:
        """
        Convert a WhatsApp message dict into a Needs_Action task file.
        """
        # Normalise message fields (support Meta Cloud API format + simplified format)
        sender = (item.get("from") or item.get("sender") or
                  self._extract_meta_sender(item) or "Unknown")
        text = (item.get("text") or item.get("body") or item.get("message") or
                self._extract_meta_text(item) or "")
        msg_id = (item.get("id") or item.get("wamid") or item.get("_msg_id") or
                  f"wa_{self._timestamp()}")
        timestamp = item.get("timestamp") or self._isoformat()

        # Determine priority based on keywords
        text_lower = text.lower()
        matched_keywords = [kw for kw in self.keywords if kw in text_lower]
        priority = "high" if matched_keywords else "medium"

        # Detect if this is a request that needs a response
        is_question = "?" in text or any(w in text_lower for w in ["can you", "could you", "please", "would you"])
        requires_reply = is_question or bool(matched_keywords)

        # Build suggested actions
        actions = []
        if any(kw in text_lower for kw in ["invoice", "payment", "price", "quote"]):
            actions.append("Generate and send invoice/quote")
        if any(kw in text_lower for kw in ["urgent", "asap", "emergency"]):
            actions.append("Escalate — respond within 1 hour")
        if requires_reply:
            actions.append("Draft reply message")
        if not actions:
            actions.append("Review and determine appropriate response")

        frontmatter = {
            "type": "whatsapp",
            "source": "whatsapp",
            "from": sender,
            "message_id": msg_id,
            "received": timestamp,
            "priority": priority,
            "status": "pending_review",
            "approval": requires_reply,  # WhatsApp replies need HITL approval
            "matched_keywords": matched_keywords if matched_keywords else [],
            "requires_reply": requires_reply,
        }

        body = f"""## WhatsApp Message

**From:** {sender}
**Received:** {timestamp}
**Priority:** {priority.title()}
**Keywords Matched:** {', '.join(matched_keywords) if matched_keywords else 'None'}

---

### Message Content

{text}

---

### Suggested Actions

{chr(10).join(f'- [ ] {action}' for action in actions)}

### To Approve a Reply

Move this file to `Approved/` folder, or set `approved: true` in the frontmatter.
The system will then use the WhatsApp MCP server to send the reply.

---
*Detected by WhatsApp Watcher — {self._isoformat()}*
"""

        safe_sender = self._safe_filename(re.sub(r'\D', '', sender) or sender, max_len=20)
        filename = f"WHATSAPP_{safe_sender}_{self._timestamp()}"
        return self.write_action_file(filename, frontmatter, body)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _extract_meta_sender(self, item: dict) -> str:
        """Extract sender from Meta Cloud API webhook payload."""
        try:
            entry = item.get("entry", [{}])[0]
            change = entry.get("changes", [{}])[0]
            value = change.get("value", {})
            messages = value.get("messages", [])
            if messages:
                return messages[0].get("from", "")
        except (IndexError, KeyError, TypeError):
            pass
        return ""

    def _extract_meta_text(self, item: dict) -> str:
        """Extract message text from Meta Cloud API webhook payload."""
        try:
            entry = item.get("entry", [{}])[0]
            change = entry.get("changes", [{}])[0]
            value = change.get("value", {})
            messages = value.get("messages", [])
            if messages:
                msg = messages[0]
                return msg.get("text", {}).get("body", "")
        except (IndexError, KeyError, TypeError):
            pass
        return ""


def main():
    """Run the WhatsApp Watcher."""
    import logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    watcher = WhatsAppWatcher(check_interval=30)
    watcher.run()


if __name__ == "__main__":
    main()
