#!/usr/bin/env python3
"""
Autonomous Personal AI Employee System

This script runs the fully autonomous version of the Personal AI Employee system
with all the upgraded features:
- Auto task flow (Incoming → In_Progress → Completed)
- Ralph Loop (retry mechanism with max 10 retries)
- Human Approval Gate
- Weekly CEO Reports
- Crash-safe operation
"""

import os
import time
import signal
import sys
from pathlib import Path
import subprocess
import threading
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/autonomous_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class AutonomousAISystem:
    def __init__(self):
        self.running = False
        self.components = {
            'file_watcher': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'gmail_watcher': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'whatsapp_watcher': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'ralph_loop': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'task_processor': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'notification_system': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'dashboard_updater': {'process': None, 'restart_count': 0, 'max_restarts': 3},
        }
        self.setup_folders()
        self.setup_logs_directory()

    def setup_folders(self):
        """Create all required workflow and vault folders on startup."""
        required_folders = [
            # Core workflow (numbered stages)
            "01_Incoming_Tasks",
            "02_In_Progress_Tasks",
            "03_Completed_Tasks",
            "04_Approval_Workflows",
            "05_Failed_Tasks",
            # Hackathon-spec folder names
            "Inbox",
            "Needs_Action",
            "Done",
            "Pending_Approval",
            "Approved",
            # Intelligence & reporting
            "Plans",
            "Memory",
            "Decision_Ledger",
            "Logs",
            "Reports",
            "Business",
            # WhatsApp queue
            "Inbox/whatsapp_queue",
            # Social media queues
            "Business/LinkedIn_Queue",
            "Business/LinkedIn_Queue/Posted",
            "Business/Facebook_Queue",
            "Business/Facebook_Queue/Posted",
            "Business/Twitter_Queue",
            "Business/Twitter_Queue/Posted",
            "Business/Instagram_Queue",
            "Business/Instagram_Queue/Posted",
            # Briefings
            "Briefings",
        ]
        base = Path(os.path.dirname(os.path.abspath(__file__)))
        for folder in required_folders:
            (base / folder).mkdir(parents=True, exist_ok=True)

    def setup_logs_directory(self):
        """Create logs directory if it doesn't exist"""
        logs_path = Path("Logs")
        logs_path.mkdir(parents=True, exist_ok=True)

    def start_component(self, component_name):
        """Start a specific component in a separate process"""
        logging.info(f"[Autonomous System] Starting {component_name}...")
        try:
            script_name = f"{component_name}.py"
            # Some components need extra arguments for continuous/watch mode
            extra_args = {
                'dashboard_updater': ['--watch', '--interval', '60'],
            }
            cmd = [sys.executable, script_name] + extra_args.get(component_name, [])
            self.components[component_name]['process'] = subprocess.Popen(
                cmd, cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.components[component_name]['restart_count'] = 0  # Reset restart count on successful start
            logging.info(f"[Autonomous System] {component_name} started successfully with PID {self.components[component_name]['process'].pid}")
        except Exception as e:
            logging.error(f"[Autonomous System] Error starting {component_name}: {e}")

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

    def _initial_setup(self):
        """Run one-off startup tasks: generate initial dashboard and auto-plans."""
        try:
            subprocess.run([sys.executable, "dashboard_updater.py"],
                           cwd=os.path.dirname(os.path.abspath(__file__)),
                           timeout=30)
            logging.info("Initial Dashboard.md generated")
        except Exception as e:
            logging.warning(f"Could not generate initial dashboard: {e}")

        try:
            subprocess.run([sys.executable, "plan_generator.py", "--auto"],
                           cwd=os.path.dirname(os.path.abspath(__file__)),
                           timeout=30)
            logging.info("Auto-plans generated for pending tasks")
        except Exception as e:
            logging.warning(f"Could not auto-generate plans: {e}")

    def generate_weekly_reports(self):
        """Generate weekly reports periodically"""
        while self.running:
            # Run at midnight on Sundays (0 for Sunday)
            now = datetime.now()
            if now.weekday() == 6 and now.hour == 0 and now.minute < 5:  # Sunday at 12:00-12:05 AM
                try:
                    subprocess.run([sys.executable, "weekly_ceo_report.py"])
                    logging.info("Weekly CEO report generated")
                except Exception as e:
                    logging.error(f"Error generating weekly report: {e}")
            
            time.sleep(3600)  # Check every hour

    def start_system(self):
        """Start the entire autonomous AI employee system"""
        print("="*60)
        print("[AI] Autonomous Personal AI Employee System")
        print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        self.running = True

        # Run initial setup tasks synchronously before starting background components
        self._initial_setup()

        # Start all components
        self.start_all_components()

        print("\n[STATUS] System Status:")
        for component_name in self.components.keys():
            print(f"   • {component_name.replace('_', ' ').title()}: STARTED")
        print("\n[INFO] System running with crash recovery and autonomous features enabled")
        print("[INFO] Press Ctrl+C to shut down the system safely")

        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_components, daemon=True)
        monitor_thread.start()

        # Start weekly report generation thread
        report_thread = threading.Thread(target=self.generate_weekly_reports, daemon=True)
        report_thread.start()

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Gracefully shut down the system"""
        logging.info("\n🛑 Shutting down Autonomous Personal AI Employee System...")

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

        logging.info("[OK] Autonomous Personal AI Employee System shut down successfully!")
        self.running = False
        sys.exit(0)

def signal_handler(sig, frame):
    """Handle graceful shutdown when Ctrl+C is pressed"""
    logging.info("\n[WARN]  Received interrupt signal, shutting down gracefully...")
    sys.exit(0)

def main():
    """Main function to run the autonomous system"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start the system
    system = AutonomousAISystem()

    try:
        system.start_system()
    except KeyboardInterrupt:
        system.shutdown()

if __name__ == "__main__":
    main()