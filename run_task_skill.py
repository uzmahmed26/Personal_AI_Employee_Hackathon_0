#!/usr/bin/env python3
"""
Task Executor Skill - CLI Runner

Simple command-line interface to create tasks using the Task Executor Skill.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from task_executor_skill import TaskExecutorSkill


def create_task(args):
    """Create a task using the Task Executor Skill"""
    executor = TaskExecutorSkill()
    
    # Parse metadata if provided
    metadata = {}
    if args.metadata:
        for item in args.metadata:
            if '=' in item:
                key, value = item.split('=', 1)
                # Try to convert to appropriate type
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                metadata[key] = value
    
    # Execute task creation
    summary = executor.execute_task(
        task_type=args.type,
        description=args.description,
        priority=args.priority,
        approval_required=args.approval,
        metadata=metadata
    )
    
    # Print formatted summary
    print(executor.format_summary(summary))
    
    return 0


def demo():
    """Run demonstration of the Task Executor Skill"""
    executor = TaskExecutorSkill()
    
    print("="*60)
    print("TASK EXECUTOR SKILL - Demo")
    print("="*60)
    print()
    
    # Demo 1: File processing task
    print("📝 Example 1: File Processing Task")
    print("-"*60)
    summary1 = executor.execute_task(
        task_type='file_arrival',
        description='Process quarterly report PDF from Inbox',
        priority='high',
        approval_required=False,
        metadata={
            'filename': 'quarterly_report_Q4_2025.pdf',
            'size': '3.2 MB'
        }
    )
    print(executor.format_summary(summary1))
    print()
    
    # Demo 2: Approval required task
    print("📝 Example 2: Approval Required Task")
    print("-"*60)
    summary2 = executor.execute_task(
        task_type='approval_required',
        description='Marketing budget approval request for $50,000 Q1 campaign',
        priority='critical',
        approval_required=True,
        metadata={
            'approval_type': 'financial',
            'amount': 50000,
            'currency': 'USD',
            'approver': 'CEO',
            'deadline': '2026-02-25'
        }
    )
    print(executor.format_summary(summary2))
    print()
    
    # Demo 3: Research task
    print("📝 Example 3: Research Task")
    print("-"*60)
    summary3 = executor.execute_task(
        task_type='research_task',
        description='Research competitor pricing strategies for Q1 2026',
        priority='medium',
        approval_required=False,
        metadata={
            'depth': 'comprehensive',
            'deadline': '2026-02-27',
            'sources': 'company_websites, industry_reports'
        }
    )
    print(executor.format_summary(summary3))
    print()
    
    print("="*60)
    print("✅ Demo completed!")
    print("="*60)
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Task Executor Skill - Create and manage tasks autonomously',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create -t file_arrival -d "Process report.pdf" -p high
  %(prog)s create -t approval_required -d "Budget approval" -p critical --approval
  %(prog)s create -t email -d "Important client email" -p high -m from=client@company.com
  %(prog)s demo
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create task command
    create_parser = subparsers.add_parser('create', help='Create a new task')
    create_parser.add_argument('-t', '--type', required=True, 
                              help='Task type (file_arrival, email, approval_required, research_task, etc.)')
    create_parser.add_argument('-d', '--description', required=True,
                              help='Task description')
    create_parser.add_argument('-p', '--priority', default='medium',
                              choices=['critical', 'high', 'medium', 'low'],
                              help='Task priority (default: medium)')
    create_parser.add_argument('--approval', action='store_true',
                              help='Require human approval')
    create_parser.add_argument('-m', '--metadata', nargs='*',
                              help='Additional metadata (format: key=value)')
    create_parser.set_defaults(func=create_task)
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demonstration')
    demo_parser.set_defaults(func=demo)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
