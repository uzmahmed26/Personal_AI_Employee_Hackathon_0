#!/usr/bin/env python3
"""
Company-Scale AI Organization Main Entry Point

This script runs the complete company-scale AI organization with all features:
- Department AI employees
- Executive council
- Conflict resolution
- Strategy simulation
- Autonomy management
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
        logging.FileHandler('Logs/company_organization.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class CompanyOrganization:
    def __init__(self):
        self.running = False
        self.components = {
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
        logging.info(f"[Company Organization] Starting {component_name}...")
        try:
            script_name = f"{component_name}.py"
            self.components[component_name]['process'] = subprocess.Popen([
                sys.executable, script_name
            ], cwd=os.path.dirname(os.path.abspath(__file__)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.components[component_name]['restart_count'] = 0  # Reset restart count on successful start
            logging.info(f"[Company Organization] {component_name} started successfully with PID {self.components[component_name]['process'].pid}")
        except Exception as e:
            logging.error(f"[Company Organization] Error starting {component_name}: {e}")

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

    def run_company_operations(self):
        """Run company-scale operations cycle"""
        while self.running:
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
        print("🏢 Company-Scale AI Organization")
        print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        self.running = True

        # Start all components
        self.start_all_components()

        print("\n📋 System Status:")
        for component_name in self.components.keys():
            print(f"   • {component_name.replace('_', ' ').title()}: STARTED")
        
        print("\n📊 Department AI Employees:")
        print("   • Sales_AI: Managing sales tasks and pipeline")
        print("   • Ops_AI: Optimizing operations and workflows")
        print("   • Support_AI: Handling customer support and issues")
        print("   • Finance_AI: Managing budgets and financial tasks")
        
        print("\n🏛️  Executive Council:")
        print("   • Reviews department briefs weekly")
        print("   • Generates strategic summaries")
        print("   • Identifies conflicts and trade-offs")
        
        print("\n⚖️  Cross-Department Conflict Resolver:")
        print("   • Detects conflicting priorities")
        print("   • Resolves conflicts automatically")
        print("   • Escalates to CEO when needed")
        
        print("\n🔮 Quarterly Strategy Simulator:")
        print("   • Simulates next 90 days of operations")
        print("   • Generates best/worst case scenarios")
        print("   • Provides strategic recommendations")
        
        print("\n🔓 Autonomy Level Management:")
        print("   • Level 1: Observe only")
        print("   • Level 2: Recommend")
        print("   • Level 3: Execute")
        print("   • Level 4: Self-direct")
        print("   • Auto-adjusts based on trust scores")
        
        print("\n💡 Company-scale AI organization running with full autonomy and executive oversight")
        print("💡 Press Ctrl+C to shut down the system safely")

        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_components, daemon=True)
        monitor_thread.start()

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
        logging.info("\n🛑 Shutting down Company-Scale AI Organization...")

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

        logging.info("✅ Company-Scale AI Organization shut down successfully!")
        self.running = False
        sys.exit(0)

def signal_handler(sig, frame):
    """Handle graceful shutdown when Ctrl+C is pressed"""
    logging.info("\n⚠️  Received interrupt signal, shutting down gracefully...")
    sys.exit(0)

def main():
    """Main function to run the company organization"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start the organization
    organization = CompanyOrganization()

    try:
        organization.start_system()
    except KeyboardInterrupt:
        organization.shutdown()

if __name__ == "__main__":
    main()