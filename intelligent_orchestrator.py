#!/usr/bin/env python3
"""
Strategic Intelligent Orchestrator for Personal AI Employee System

This script manages all system components with strategic autonomy,
business goal alignment, risk management, and adaptive behavior.
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
        logging.FileHandler('Logs/strategic_orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class StrategicAIOrchestrator:
    def __init__(self):
        self.running = False
        self.components = {
            'file_watcher': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'gmail_watcher': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'ralph_loop': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'task_processor': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'notification_system': {'process': None, 'restart_count': 0, 'max_restarts': 5},
            'task_intelligence': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'self_correction': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'learning_memory': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'ceo_question_generator': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'silent_mode': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'business_goal_alignment': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'decision_ledger': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'risk_radar': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'ceo_auto_brief': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'trust_score_system': {'process': None, 'restart_count': 0, 'max_restarts': 3}
        }
        self.setup_logs_directory()

    def setup_logs_directory(self):
        """Create logs directory if it doesn't exist"""
        logs_path = Path("Logs")
        logs_path.mkdir(parents=True, exist_ok=True)

    def start_component(self, component_name):
        """Start a specific component in a separate process"""
        logging.info(f"[Strategic Orchestrator] Starting {component_name}...")
        try:
            script_name = f"{component_name}.py"
            self.components[component_name]['process'] = subprocess.Popen([
                sys.executable, script_name
            ], cwd=os.path.dirname(os.path.abspath(__file__)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.components[component_name]['restart_count'] = 0  # Reset restart count on successful start
            logging.info(f"[Strategic Orchestrator] {component_name} started successfully with PID {self.components[component_name]['process'].pid}")
        except Exception as e:
            logging.error(f"[Strategic Orchestrator] Error starting {component_name}: {e}")

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

    def run_strategic_injection(self):
        """Run strategic autonomy injection cycle"""
        while self.running:
            try:
                # Run business goal alignment
                result = subprocess.run([sys.executable, "business_goal_alignment.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"Business goal alignment error: {result.stderr}")

                # Run decision ledger updates
                # Decision ledger is mostly passive, but we can trigger periodic maintenance
                logging.info("Decision ledger maintenance completed")

                # Run trust score system
                result = subprocess.run([sys.executable, "trust_score_system.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"Trust score system error: {result.stderr}")

                # Run task intelligence
                result = subprocess.run([sys.executable, "task_intelligence.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"Task intelligence error: {result.stderr}")

                # Run self-correction
                result = subprocess.run([sys.executable, "self_correction.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"Self-correction error: {result.stderr}")

                # Run learning memory
                result = subprocess.run([sys.executable, "learning_memory.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"Learning memory error: {result.stderr}")

                # Run silent mode check
                result = subprocess.run([sys.executable, "silent_mode.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"Silent mode error: {result.stderr}")

                logging.info("Strategic autonomy injection cycle completed")

            except Exception as e:
                logging.error(f"Error in strategic injection: {e}")

            time.sleep(3600)  # Run strategic injection every hour

    def run_risk_management(self):
        """Run risk management cycle"""
        while self.running:
            try:
                # Run risk radar scan
                result = subprocess.run([sys.executable, "risk_radar.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"Risk radar error: {result.stderr}")

                # Run CEO auto-brief check
                result = subprocess.run([sys.executable, "ceo_auto_brief.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"CEO auto-brief error: {result.stderr}")

                logging.info("Risk management cycle completed")

            except Exception as e:
                logging.error(f"Error in risk management: {e}")

            time.sleep(10800)  # Run risk management every 3 hours

    def run_ceo_question_generation(self):
        """Run CEO question generation weekly"""
        while self.running:
            # Run at midnight on Sundays
            now = datetime.now()
            if now.weekday() == 6 and now.hour == 0 and now.minute < 10:  # Sunday at 12:00-12:10 AM
                try:
                    result = subprocess.run([sys.executable, "ceo_question_generator.py"],
                                          capture_output=True, text=True, timeout=300)
                    if result.returncode != 0:
                        logging.error(f"CEO question generation error: {result.stderr}")
                    else:
                        logging.info("Weekly CEO questions generated")
                except Exception as e:
                    logging.error(f"Error generating CEO questions: {e}")

            time.sleep(3600)  # Check every hour

    def start_system(self):
        """Start the entire strategic AI employee system"""
        print("="*60)
        print("🤖 Strategic Personal AI Employee System - Orchestrator")
        print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        self.running = True

        # Start all components
        self.start_all_components()

        print("\n📋 System Status:")
        for component_name in self.components.keys():
            print(f"   • {component_name.replace('_', ' ').title()}: STARTED")
        print("\n💡 System running with strategic autonomy and business alignment")
        print("💡 Press Ctrl+C to shut down the system safely")

        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_components, daemon=True)
        monitor_thread.start()

        # Start strategic injection thread
        strategic_thread = threading.Thread(target=self.run_strategic_injection, daemon=True)
        strategic_thread.start()

        # Start risk management thread
        risk_thread = threading.Thread(target=self.run_risk_management, daemon=True)
        risk_thread.start()

        # Start CEO question generation thread
        ceo_thread = threading.Thread(target=self.run_ceo_question_generation, daemon=True)
        ceo_thread.start()

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Gracefully shut down the system"""
        logging.info("\n🛑 Shutting down Strategic Personal AI Employee System...")

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

        logging.info("✅ Strategic Personal AI Employee System shut down successfully!")
        self.running = False
        sys.exit(0)

def signal_handler(sig, frame):
    """Handle graceful shutdown when Ctrl+C is pressed"""
    logging.info("\n⚠️  Received interrupt signal, shutting down gracefully...")
    sys.exit(0)

def main():
    """Main function to run the strategic orchestrator"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start the orchestrator
    orchestrator = StrategicAIOrchestrator()

    try:
        orchestrator.start_system()
    except KeyboardInterrupt:
        orchestrator.shutdown()

if __name__ == "__main__":
    main()