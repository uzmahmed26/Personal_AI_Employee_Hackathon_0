#!/usr/bin/env python3
"""
Main Orchestrator for Personal AI Employee System

This script manages both the file watcher and gmail watcher simultaneously,
allowing you to run your entire AI employee system from a single entry point.
"""

import threading
import time
import signal
import sys
from pathlib import Path
import subprocess
import os

class PersonalAIEmployee:
    def __init__(self):
        self.running = False
        self.file_watcher_process = None
        self.gmail_watcher_process = None
        
    def start_file_watcher(self):
        """Start the file watcher in a separate process"""
        print("[Main Orchestrator] Starting File Watcher...")
        try:
            # Start file watcher as a subprocess
            self.file_watcher_process = subprocess.Popen([
                sys.executable, "file_watcher.py"
            ], cwd=os.path.dirname(os.path.abspath(__file__)))
            print("[Main Orchestrator] File Watcher started successfully")
        except Exception as e:
            print(f"[Main Orchestrator] Error starting File Watcher: {e}")
    
    def start_gmail_watcher(self):
        """Start the gmail watcher in a separate process"""
        print("[Main Orchestrator] Starting Gmail Watcher...")
        try:
            # Start gmail watcher as a subprocess
            self.gmail_watcher_process = subprocess.Popen([
                sys.executable, "gmail_watcher.py"
            ], cwd=os.path.dirname(os.path.abspath(__file__)))
            print("[Main Orchestrator] Gmail Watcher started successfully")
        except Exception as e:
            print(f"[Main Orchestrator] Error starting Gmail Watcher: {e}")
            
    def start_system(self):
        """Start the entire AI employee system"""
        print("="*60)
        print("🤖 Personal AI Employee System - Main Orchestrator")
        print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        self.running = True
        
        # Start both watchers
        self.start_file_watcher()
        self.start_gmail_watcher()
        
        print("\n📋 System Status:")
        print("   • File Watcher: RUNNING")
        print("   • Gmail Watcher: RUNNING")
        print("   • Task Management: ACTIVE")
        print("\n💡 Press Ctrl+C to shut down the system safely")
        
        # Monitor processes
        try:
            while self.running:
                # Check if processes are still running
                if self.file_watcher_process and self.file_watcher_process.poll() is not None:
                    print("[Main Orchestrator] File Watcher process ended unexpectedly")
                    break
                
                if self.gmail_watcher_process and self.gmail_watcher_process.poll() is not None:
                    print("[Main Orchestrator] Gmail Watcher process ended unexpectedly")
                    break
                
                time.sleep(1)  # Check every second
                
        except KeyboardInterrupt:
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shut down the system"""
        print("\n🛑 Shutting down Personal AI Employee System...")
        
        # Terminate processes if they're running
        if self.file_watcher_process:
            try:
                self.file_watcher_process.terminate()
                self.file_watcher_process.wait(timeout=5)  # Wait up to 5 seconds
            except subprocess.TimeoutExpired:
                self.file_watcher_process.kill()  # Force kill if it doesn't terminate
            
        if self.gmail_watcher_process:
            try:
                self.gmail_watcher_process.terminate()
                self.gmail_watcher_process.wait(timeout=5)  # Wait up to 5 seconds
            except subprocess.TimeoutExpired:
                self.gmail_watcher_process.kill()  # Force kill if it doesn't terminate
        
        print("✅ Personal AI Employee System shut down successfully!")
        self.running = False
        sys.exit(0)

def signal_handler(sig, frame):
    """Handle graceful shutdown when Ctrl+C is pressed"""
    print("\n⚠️  Received interrupt signal, shutting down gracefully...")
    # In a real implementation, we would call orchestrator.shutdown()
    # But since this is called from main, we'll just exit
    sys.exit(0)

def main():
    """Main function to run the orchestrator"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and start the orchestrator
    orchestrator = PersonalAIEmployee()
    
    try:
        orchestrator.start_system()
    except KeyboardInterrupt:
        orchestrator.shutdown()

if __name__ == "__main__":
    main()