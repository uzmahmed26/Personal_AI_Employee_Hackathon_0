#!/usr/bin/env python3
"""
Enhanced Main Orchestrator for Personal AI Employee System

This script manages all system components with crash recovery and auto-restart capabilities.
"""

import threading
import time
import signal
import sys
from pathlib import Path
import subprocess
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class EnhancedPersonalAIEmployee:
    def __init__(self):
        self.running = False
        self.components = {
            'file_watcher': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'gmail_watcher': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'ralph_loop': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'notification_system': {'process': None, 'restart_count': 0, 'max_restarts': 5}
        }
        self.setup_logs_directory()

    def setup_logs_directory(self):
        """Create logs directory if it doesn't exist"""
        logs_path = Path("Logs")
        logs_path.mkdir(parents=True, exist_ok=True)

    def start_component(self, component_name):
        """Start a specific component in a separate process"""
        logging.info(f"[Main Orchestrator] Starting {component_name}...")
        try:
            script_name = f"{component_name.replace('ralph_loop', 'ralph_loop').replace('notification_system', 'notification_system').replace('gmail_watcher', 'gmail_watcher').replace('file_watcher', 'file_watcher')}.py"
            self.components[component_name]['process'] = subprocess.Popen([
                sys.executable, script_name
            ], cwd=os.path.dirname(os.path.abspath(__file__)))
            self.components[component_name]['restart_count'] = 0  # Reset restart count on successful start
            logging.info(f"[Main Orchestrator] {component_name} started successfully with PID {self.components[component_name]['process'].pid}")
        except Exception as e:
            logging.error(f"[Main Orchestrator] Error starting {component_name}: {e}")

    def start_all_components(self):
        """Start all system components"""
        for component_name in self.components.keys():
            self.start_component(component_name)

    def monitor_components(self):
        """Monitor all components and restart failed ones"""
        while self.running:
            for component_name, component_info in self.components.items():
                process = component_info['process']
                
                if process and process.poll() is not None:  # Process has ended
                    logging.warning(f"{component_name} process ended with return code {process.returncode}")
                    
                    # Check if we've exceeded restart attempts
                    if component_info['restart_count'] < component_info['max_restarts']:
                        component_info['restart_count'] += 1
                        logging.info(f"Restarting {component_name} (attempt {component_info['restart_count']}/{component_info['max_restarts']})")
                        self.start_component(component_name)
                    else:
                        logging.error(f"Max restart attempts reached for {component_name}. Manual intervention required.")
            
            time.sleep(5)  # Check every 5 seconds

    def start_system(self):
        """Start the entire AI employee system with crash recovery"""
        print("="*60)
        print("🤖 Enhanced Personal AI Employee System - Main Orchestrator")
        print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        self.running = True

        # Start all components
        self.start_all_components()

        print("\n📋 System Status:")
        for component_name in self.components.keys():
            print(f"   • {component_name.replace('_', ' ').title()}: STARTED")
        print("\n💡 System running with crash recovery enabled")
        print("💡 Press Ctrl+C to shut down the system safely")

        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_components, daemon=True)
        monitor_thread.start()

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Gracefully shut down the system"""
        logging.info("\n🛑 Shutting down Enhanced Personal AI Employee System...")

        # Terminate all processes
        for component_name, component_info in self.components.items():
            if component_info['process']:
                try:
                    component_info['process'].terminate()
                    component_info['process'].wait(timeout=10)  # Wait up to 10 seconds
                    logging.info(f"{component_name} terminated successfully")
                except subprocess.TimeoutExpired:
                    component_info['process'].kill()  # Force kill if it doesn't terminate
                    logging.warning(f"{component_name} killed forcefully")
                except Exception as e:
                    logging.error(f"Error terminating {component_name}: {e}")

        logging.info("✅ Enhanced Personal AI Employee System shut down successfully!")
        self.running = False
        sys.exit(0)

def signal_handler(sig, frame):
    """Handle graceful shutdown when Ctrl+C is pressed"""
    logging.info("\n⚠️  Received interrupt signal, shutting down gracefully...")
    sys.exit(0)

def main():
    """Main function to run the enhanced orchestrator"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start the orchestrator
    orchestrator = EnhancedPersonalAIEmployee()

    try:
        orchestrator.start_system()
    except KeyboardInterrupt:
        orchestrator.shutdown()

if __name__ == "__main__":
    main()