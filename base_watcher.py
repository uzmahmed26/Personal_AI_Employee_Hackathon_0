#!/usr/bin/env python3
"""
Base Watcher - Abstract base class for all Personal AI Employee watchers.

All watchers (Gmail, WhatsApp, File System, etc.) inherit from this class.
It provides the common run-loop, logging, error handling, and task-file
creation pattern described in the hackathon architecture spec.

Usage:
    Subclass BaseWatcher and implement:
        - check_for_updates() -> list
        - create_action_file(item) -> Path
"""

import time
import logging
import signal
import sys
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List


class BaseWatcher(ABC):
    """
    Abstract base class for all AI Employee watchers.

    Each watcher monitors one input source (Gmail, WhatsApp, filesystem, etc.)
    and converts incoming events into .md task files in the Needs_Action/ folder
    for Claude to process.
    """

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Args:
            vault_path: Absolute path to the Obsidian vault / project root.
            check_interval: Seconds between polling cycles (default: 60).
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.done = self.vault_path / "Done"
        self.inbox = self.vault_path / "Inbox"
        self.check_interval = check_interval
        self.running = False

        # Set up per-watcher logger
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            log_dir = self.vault_path / "Logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(log_dir / f"{self.__class__.__name__.lower()}.log")
            handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            self.logger.addHandler(handler)
            self.logger.addHandler(logging.StreamHandler())
            self.logger.setLevel(logging.INFO)

        # Ensure required folders exist
        for folder in [self.needs_action, self.done, self.inbox]:
            folder.mkdir(parents=True, exist_ok=True)

        # Track processed items to avoid duplicates
        self._processed_ids: set = set()

    # ── Abstract interface ────────────────────────────────────────────────────

    @abstractmethod
    def check_for_updates(self) -> List:
        """
        Poll the input source and return a list of new items to process.

        Returns:
            List of raw items (emails, messages, file paths, etc.)
            Only return items that haven't been processed yet.
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Convert a raw item into a structured .md task file in Needs_Action/.

        The file must use YAML frontmatter with at minimum:
            type, source, received, priority, status

        Args:
            item: A single item from check_for_updates()

        Returns:
            Path to the created .md file.
        """
        pass

    # ── Common helpers ────────────────────────────────────────────────────────

    def _safe_filename(self, text: str, max_len: int = 40) -> str:
        """Sanitise text for use in a filename."""
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in text)
        return safe[:max_len]

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _isoformat(self) -> str:
        return datetime.now().isoformat()

    def _build_frontmatter(self, data: dict) -> str:
        """
        Build a YAML frontmatter block from a dict.

        Args:
            data: Key-value pairs for the frontmatter.

        Returns:
            String with --- delimiters.
        """
        lines = ["---"]
        for key, value in data.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            elif isinstance(value, bool):
                lines.append(f"{key}: {'true' if value else 'false'}")
            else:
                # Quote strings that contain special YAML characters
                str_val = str(value)
                if any(c in str_val for c in [":", "#", "[", "]", "{", "}", ","]):
                    str_val = f'"{str_val}"'
                lines.append(f"{key}: {str_val}")
        lines.append("---")
        return "\n".join(lines)

    def write_action_file(self, filename: str, frontmatter: dict, body: str) -> Path:
        """
        Write a task file to Needs_Action/.

        Args:
            filename: File name (without extension).
            frontmatter: Dict of YAML frontmatter fields.
            body: Markdown body content.

        Returns:
            Path to the created file.
        """
        filepath = self.needs_action / f"{filename}.md"

        # Avoid overwrites by appending a counter
        counter = 1
        while filepath.exists():
            filepath = self.needs_action / f"{filename}_{counter}.md"
            counter += 1

        content = self._build_frontmatter(frontmatter) + "\n\n" + body
        filepath.write_text(content, encoding="utf-8")
        self.logger.info(f"Created action file: {filepath.name}")
        return filepath

    # ── Run loop ─────────────────────────────────────────────────────────────

    def run(self):
        """
        Start the watcher's main polling loop.

        Runs until interrupted (SIGINT/SIGTERM) or self.running is set to False.
        Implements exponential back-off on transient errors.
        """
        self.running = True
        self._register_signal_handlers()

        self.logger.info(f"[{self.__class__.__name__}] Started — polling every {self.check_interval}s")

        consecutive_errors = 0

        while self.running:
            try:
                items = self.check_for_updates()
                if items:
                    self.logger.info(f"Found {len(items)} new item(s)")
                for item in items:
                    try:
                        path = self.create_action_file(item)
                        self.logger.info(f"Action file created: {path.name}")
                    except Exception as e:
                        self.logger.error(f"Failed to create action file for item: {e}")

                consecutive_errors = 0  # Reset on success

            except KeyboardInterrupt:
                break
            except Exception as e:
                consecutive_errors += 1
                backoff = min(60 * consecutive_errors, 600)  # Max 10-min backoff
                self.logger.error(f"Error in check cycle (attempt {consecutive_errors}): {e}. Retrying in {backoff}s.")
                time.sleep(backoff)
                continue

            time.sleep(self.check_interval)

        self.logger.info(f"[{self.__class__.__name__}] Stopped.")

    def stop(self):
        """Signal the run loop to stop gracefully."""
        self.running = False

    def _register_signal_handlers(self):
        """Register SIGINT / SIGTERM handlers for graceful shutdown."""
        def _handler(sig, frame):
            self.logger.info(f"Received signal {sig}, shutting down...")
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, _handler)
        try:
            signal.signal(signal.SIGTERM, _handler)
        except (OSError, ValueError):
            pass  # SIGTERM not available on Windows in some contexts
