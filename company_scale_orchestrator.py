#!/usr/bin/env python3
"""
Company-Scale AI Organization Orchestrator with Production Safety

This script manages the entire company-scale AI organization with:
- Department AI employees
- Executive council
- Conflict resolution
- Strategy simulation
- Autonomy management
- Governance and safety features
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
        logging.FileHandler('Logs/company_scale_orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class CompanyScaleOrchestrator:
    def __init__(self):
        self.running = False
        self.components = {
            'governance_layer': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'kill_switch_safe_mode': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'ethics_compliance_monitor': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'production_health_monitor': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'immutable_audit_trail': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'department_ais': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'executive_council': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'cross_dept_conflict_resolver': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'quarterly_strategy_simulator': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'autonomy_level_manager': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'business_goal_alignment': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'risk_radar': {'process': None, 'restart_count': 0, 'max_restarts': 3},
            'trust_score_system': {'process': None, 'restart_count': 0, 'max_restarts': 3}
        }
        self.setup_logs_directory()

    def setup_logs_directory(self):
        """Create logs directory if it doesn't exist"""
        logs_path = Path("Logs")
        logs_path.mkdir(parents=True, exist_ok=True)

    def start_component(self, component_name):
        """Start a specific component in a separate process"""
        logging.info(f"[Company Orchestrator] Starting {component_name}...")
        try:
            script_name = f"{component_name}.py"
            self.components[component_name]['process'] = subprocess.Popen([
                sys.executable, script_name
            ], cwd=os.path.dirname(os.path.abspath(__file__)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.components[component_name]['restart_count'] = 0  # Reset restart count on successful start
            logging.info(f"[Company Orchestrator] {component_name} started successfully with PID {self.components[component_name]['process'].pid}")
        except Exception as e:
            logging.error(f"[Company Orchestrator] Error starting {component_name}: {e}")

    def start_all_components(self):
        """Start all system components"""
        for component_name in self.components.keys():
            self.start_component(component_name)

    def monitor_components(self):
        """Monitor all components and restart failed ones"""
        while self.running:
            # Check if safe mode is enabled
            safe_mode_enabled = self.is_safe_mode_enabled()
            if safe_mode_enabled:
                logging.info("Safe mode enabled - pausing non-critical operations")
                time.sleep(10)  # Longer sleep in safe mode
                continue

            for component_name, component_info in self.components.items():
                # Skip certain components in safe mode
                if safe_mode_enabled and component_name in ['department_ais', 'executive_council', 'cross_dept_conflict_resolver']:
                    continue

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

    def is_safe_mode_enabled(self) -> bool:
        """Check if safe mode is enabled"""
        try:
            result = subprocess.run([sys.executable, "kill_switch_safe_mode.py"],
                                  capture_output=True, text=True, timeout=10)
            # Check if safe mode is active by looking at the output
            if "SAFE MODE ACTIVE" in result.stdout:
                return True
        except Exception as e:
            logging.error(f"Error checking safe mode status: {e}")

        return False

    def run_governance_operations(self):
        """Run governance and safety operations"""
        while self.running:
            try:
                # Run ethics and compliance monitoring
                result = subprocess.run([sys.executable, "ethics_compliance_monitor.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"Ethics compliance monitor error: {result.stderr}")

                # Run production health monitoring
                result = subprocess.run([sys.executable, "production_health_monitor.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"Production health monitor error: {result.stderr}")

                # Run immutable audit trail maintenance
                result = subprocess.run([sys.executable, "immutable_audit_trail.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"Immutable audit trail error: {result.stderr}")

                # Check safe mode status
                result = subprocess.run([sys.executable, "kill_switch_safe_mode.py"],
                                      capture_output=True, text=True, timeout=10)
                if "SAFE MODE ACTIVE" in result.stdout:
                    logging.warning("Safe mode is active - system in read-only mode")

                logging.info("Governance operations cycle completed")

            except Exception as e:
                logging.error(f"Error in governance operations: {e}")

            time.sleep(3600)  # Run governance operations every hour

    def run_company_operations(self):
        """Run company-scale operations cycle"""
        while self.running:
            # Check if safe mode is enabled
            safe_mode_enabled = self.is_safe_mode_enabled()
            if safe_mode_enabled:
                logging.info("Safe mode enabled - pausing company operations")
                time.sleep(300)  # Sleep longer in safe mode
                continue

            try:
                # Run department AI operations
                result = subprocess.run([sys.executable, "department_ais.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"Department AIs error: {result.stderr}")

                # Run autonomy level management
                result = subprocess.run([sys.executable, "autonomy_level_manager.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"Autonomy manager error: {result.stderr}")

                # Run conflict resolution
                result = subprocess.run([sys.executable, "cross_dept_conflict_resolver.py"],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logging.error(f"Conflict resolver error: {result.stderr}")

                logging.info("Company operations cycle completed")

            except Exception as e:
                logging.error(f"Error in company operations: {e}")

            time.sleep(1800)  # Run company operations every 30 minutes

    def run_executive_council_cycle(self):
        """Run executive council cycle weekly"""
        while self.running:
            # Check if safe mode is enabled
            safe_mode_enabled = self.is_safe_mode_enabled()
            if safe_mode_enabled:
                time.sleep(3600)  # Just sleep in safe mode
                continue

            # Run at midnight on Sundays
            now = datetime.now()
            if now.weekday() == 6 and now.hour == 0 and now.minute < 10:  # Sunday at 12:00-12:10 AM
                try:
                    result = subprocess.run([sys.executable, "executive_council.py"],
                                          capture_output=True, text=True, timeout=300)
                    if result.returncode != 0:
                        logging.error(f"Executive council error: {result.stderr}")
                    else:
                        logging.info("Executive council cycle completed")
                except Exception as e:
                    logging.error(f"Error in executive council: {e}")

            time.sleep(3600)  # Check every hour

    def run_strategy_simulation(self):
        """Run strategy simulation monthly"""
        while self.running:
            # Check if safe mode is enabled
            safe_mode_enabled = self.is_safe_mode_enabled()
            if safe_mode_enabled:
                time.sleep(3600)  # Just sleep in safe mode
                continue

            # Run at the beginning of each month
            now = datetime.now()
            if now.day == 1 and now.hour == 1 and now.minute < 10:  # 1st of month at 1:00-1:10 AM
                try:
                    result = subprocess.run([sys.executable, "quarterly_strategy_simulator.py"],
                                          capture_output=True, text=True, timeout=600)  # Longer timeout for simulation
                    if result.returncode != 0:
                        logging.error(f"Strategy simulation error: {result.stderr}")
                    else:
                        logging.info("Quarterly strategy simulation completed")
                except Exception as e:
                    logging.error(f"Error in strategy simulation: {e}")

            time.sleep(3600)  # Check every hour

    def start_system(self):
        """Start the entire company-scale AI organization"""
        print("="*60)
        print("🏢 Company-Scale AI Organization with Production Safety")
        print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        self.running = True

        # Initialize governance layer first
        self.start_component('governance_layer')
        time.sleep(2)  # Allow governance to initialize

        # Start all components
        for component_name in self.components.keys():
            if component_name != 'governance_layer':  # Already started
                self.start_component(component_name)

        print("\n📋 System Status:")
        for component_name in self.components.keys():
            print(f"   • {component_name.replace('_', ' ').title()}: STARTED")

        print("\n🛡️  Governance & Safety Features:")
        print("   • AI Policies defined and enforced")
        print("   • Autonomy Boundaries established")
        print("   • Human Override Protocol active")
        print("   • Kill Switch and Safe Mode enabled")
        print("   • Ethics & Compliance Monitoring active")
        print("   • Production Health Monitoring active")
        print("   • Immutable Audit Trail maintained")

        print("\n💡 Company-scale AI organization running with full governance and safety measures")
        print("💡 Press Ctrl+C to shut down the system safely")

        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_components, daemon=True)
        monitor_thread.start()

        # Start governance operations thread
        governance_thread = threading.Thread(target=self.run_governance_operations, daemon=True)
        governance_thread.start()

        # Start company operations thread
        operations_thread = threading.Thread(target=self.run_company_operations, daemon=True)
        operations_thread.start()

        # Start executive council thread
        council_thread = threading.Thread(target=self.run_executive_council_cycle, daemon=True)
        council_thread.start()

        # Start strategy simulation thread
        strategy_thread = threading.Thread(target=self.run_strategy_simulation, daemon=True)
        strategy_thread.start()

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Gracefully shut down the system"""
        logging.info("\n🛑 Shutting down Company-Scale AI Organization with Production Safety...")

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

        logging.info("✅ Company-Scale AI Organization with Production Safety shut down successfully!")
        self.running = False
        sys.exit(0)

def signal_handler(sig, frame):
    """Handle graceful shutdown when Ctrl+C is pressed"""
    logging.info("\n⚠️  Received interrupt signal, shutting down gracefully...")
    sys.exit(0)

def main():
    """Main function to run the company-scale orchestrator"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start the orchestrator
    orchestrator = CompanyScaleOrchestrator()

    try:
        orchestrator.start_system()
    except KeyboardInterrupt:
        orchestrator.shutdown()

if __name__ == "__main__":
    main()