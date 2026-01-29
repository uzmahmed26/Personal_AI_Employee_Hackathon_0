#!/usr/bin/env python3
"""
CEO Question Generator for Personal AI Employee System

This module analyzes weekly reports and generates strategic questions
about risks, blockers, and decisions needed.
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import yaml
import json
from collections import Counter

# Configuration constants
VAULT_PATH = r"C:\Users\laptop world\Desktop\Hack00"
REPORTS_FOLDER = "Reports"
COMPLETED_TASKS_FOLDER = "03_Completed_Tasks"
LOGS_FOLDER = "Logs"
MEMORY_FOLDER = "Memory"

# Convert to Path objects
reports_path = Path(VAULT_PATH) / REPORTS_FOLDER
completed_tasks_path = Path(VAULT_PATH) / COMPLETED_TASKS_FOLDER
logs_path = Path(VAULT_PATH) / LOGS_FOLDER
memory_path = Path(VAULT_PATH) / MEMORY_FOLDER

class CEOQuestionGenerator:
    def __init__(self):
        self.setup_reports_directory()

    def setup_reports_directory(self):
        """Create reports directory if it doesn't exist"""
        reports_path.mkdir(parents=True, exist_ok=True)

    def get_recent_weekly_reports(self):
        """Get the most recent weekly reports"""
        reports = []
        
        for report_file in reports_path.glob("Weekly_CEO_Report_*.md"):
            try:
                # Extract date from filename (format: Weekly_CEO_Report_YYYYMMDD.md)
                date_str = report_file.name.split('_')[3].split('.')[0]
                report_date = datetime.strptime(date_str, '%Y%m%d')
                
                # Only include recent reports (last 4 weeks)
                if (datetime.now() - report_date).days <= 28:
                    reports.append({
                        'file_path': report_file,
                        'date': report_date
                    })
            except Exception as e:
                print(f"Error parsing report date from {report_file}: {e}")
        
        # Sort by date (most recent first)
        reports.sort(key=lambda x: x['date'], reverse=True)
        return reports

    def analyze_report_content(self, report_file_path):
        """Analyze the content of a weekly report"""
        try:
            with open(report_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract sections from the report
            lines = content.split('\n')
            analysis = {
                'total_completed': 0,
                'total_retries': 0,
                'task_types': Counter(),
                'priorities': Counter(),
                'top_tasks': [],
                'retry_analysis': {},
                'efficiency': 0.0
            }
            
            for line in lines:
                line_lower = line.lower().strip()
                
                if line_lower.startswith('- **total tasks completed:'):
                    try:
                        analysis['total_completed'] = int(line.split(':')[1].strip())
                    except:
                        pass
                elif line_lower.startswith('- **total retry attempts:'):
                    try:
                        analysis['total_retries'] = int(line.split(':')[1].strip())
                    except:
                        pass
                elif line_lower.startswith('- ') and ':' in line:
                    # Parse task types and priorities
                    if 'tasks completed by type' in content or 'task completion by type' in content:
                        if ':' in line and not line.startswith('- **'):
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                task_type = parts[0].replace('-', '').strip()
                                count = parts[1].strip()
                                try:
                                    analysis['task_types'][task_type] = int(count)
                                except:
                                    pass
                    elif 'tasks completed by priority' in content or 'task completion by priority' in content:
                        if ':' in line and not line.startswith('- **'):
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                priority = parts[0].replace('-', '').strip()
                                count = parts[1].strip()
                                try:
                                    analysis['priorities'][priority] = int(count)
                                except:
                                    pass
            
            return analysis
        except Exception as e:
            print(f"Error analyzing report {report_file_path}: {e}")
            return {}

    def analyze_retry_logs(self):
        """Analyze retry logs to identify systemic issues"""
        retry_issues = {
            'frequent_retry_tasks': Counter(),
            'common_failure_reasons': Counter(),
            'trend_over_time': []
        }
        
        # Look for recent retry logs
        for log_file in logs_path.glob("retry_log_*.json"):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                
                for log_entry in logs:
                    task_file = log_entry.get('task_file', 'unknown')
                    reason = log_entry.get('reason', 'unknown')
                    
                    retry_issues['frequent_retry_tasks'][task_file] += 1
                    retry_issues['common_failure_reasons'][reason] += 1
                    
                    # Track trends
                    timestamp = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00'))
                    retry_issues['trend_over_time'].append({
                        'timestamp': timestamp,
                        'task': task_file,
                        'reason': reason
                    })
            except Exception as e:
                print(f"Error reading retry log {log_file}: {e}")
        
        return retry_issues

    def analyze_completed_tasks(self):
        """Analyze completed tasks for patterns"""
        task_analysis = {
            'completion_trends': Counter(),
            'average_completion_time': 0,
            'task_complexity_patterns': Counter()
        }
        
        if not completed_tasks_path.exists():
            return task_analysis
        
        # Analyze recent completed tasks
        for task_file in completed_tasks_path.glob('*.md'):
            try:
                # Get file modification time (when it was completed)
                mod_time = datetime.fromtimestamp(task_file.stat().st_mtime)
                
                # Group by week
                week_key = mod_time.strftime('%Y-W%U')
                task_analysis['completion_trends'][week_key] += 1
                
                # Analyze content for complexity indicators
                with open(task_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple heuristics for complexity
                if len(content) > 1000:  # Large content
                    task_analysis['task_complexity_patterns']['large_content'] += 1
                if 'complex' in content.lower() or 'complicated' in content.lower():
                    task_analysis['task_complexity_patterns']['marked_complex'] += 1
            except Exception as e:
                print(f"Error analyzing completed task {task_file}: {e}")
        
        return task_analysis

    def generate_ceo_questions(self):
        """Generate strategic questions for the CEO"""
        # Get recent reports
        recent_reports = self.get_recent_weekly_reports()
        
        # Analyze reports
        report_analyses = []
        for report in recent_reports[:4]:  # Analyze last 4 reports
            analysis = self.analyze_report_content(report['file_path'])
            report_analyses.append(analysis)
        
        # Analyze retry logs
        retry_analysis = self.analyze_retry_logs()
        
        # Analyze completed tasks
        task_analysis = self.analyze_completed_tasks()
        
        # Generate questions
        questions = []
        
        # Questions about productivity and efficiency
        if report_analyses:
            latest_analysis = report_analyses[0]
            total_completed = latest_analysis.get('total_completed', 0)
            total_retries = latest_analysis.get('total_retries', 0)
            
            if total_completed > 0:
                questions.append(f"1. Productivity Trend: We completed {total_completed} tasks this week. Is this volume meeting expectations?")
            
            if total_retries > 10:  # Significant retry activity
                questions.append(f"2. System Reliability: We had {total_retries} retry attempts this week. Should we investigate underlying causes?")
        
        # Questions about task types and priorities
        if report_analyses:
            all_task_types = Counter()
            all_priorities = Counter()
            
            for analysis in report_analyses:
                all_task_types.update(analysis.get('task_types', {}))
                all_priorities.update(analysis.get('priorities', {}))
            
            if all_task_types:
                most_common_type = all_task_types.most_common(1)
                if most_common_type:
                    task_type, count = most_common_type[0]
                    questions.append(f"3. Task Distribution: {task_type.title()} tasks dominate our workload ({count} this period). Should we optimize for this type?")
            
            if all_priorities:
                highest_priority_count = all_priorities.get('high', 0) + all_priorities.get('critical', 0)
                if highest_priority_count > 20:  # Many high-priority tasks
                    questions.append(f"4. Priority Management: We handled {highest_priority_count} high/critical priority tasks. Is our priority assignment appropriate?")
        
        # Questions about failures and retries
        frequent_retry_tasks = retry_analysis.get('frequent_retry_tasks', Counter()).most_common(3)
        for task_name, count in frequent_retry_tasks:
            if count > 5:  # Frequently retried
                questions.append(f"5. Task Reliability: '{task_name}' required {count} retry attempts. Does this task need redesign or special handling?")
        
        common_failure_reasons = retry_analysis.get('common_failure_reasons', Counter()).most_common(3)
        for reason, count in common_failure_reasons:
            if count > 10:  # Common failure pattern
                questions.append(f"6. System Issues: '{reason}' caused {count} failures. Should we address this systemic issue?")
        
        # Questions about trends
        if task_analysis['completion_trends']:
            trend_values = list(task_analysis['completion_trends'].values())
            if len(trend_values) >= 2:
                recent_avg = sum(trend_values[-2:]) / 2  # Last 2 weeks
                earlier_avg = sum(trend_values[:-2]) / max(1, len(trend_values) - 2)  # Earlier weeks
                
                if recent_avg < earlier_avg * 0.8:  # 20% decrease
                    questions.append("7. Performance Trend: Task completion rate has decreased. Should we investigate capacity or process issues?")
                elif recent_avg > earlier_avg * 1.2:  # 20% increase
                    questions.append("8. Performance Trend: Task completion rate has increased significantly. Are we properly resourced for this pace?")
        
        # Questions about complexity
        if task_analysis['task_complexity_patterns']:
            complex_tasks = sum(task_analysis['task_complexity_patterns'].values())
            if complex_tasks > 5:
                questions.append(f"9. Task Complexity: We've seen {complex_tasks} complex tasks recently. Should we invest in automation or expertise?")
        
        # Add risk and blocker questions
        questions.append("10. Strategic Risks: What external factors could disrupt our current task processing efficiency?")
        questions.append("11. Resource Planning: Do we have adequate resources to handle projected task volumes?")
        questions.append("12. Process Improvement: Which recurring tasks should we consider automating further?")
        
        return questions

    def save_ceo_questions(self, questions):
        """Save CEO questions to a markdown file"""
        content = f"""# CEO Strategic Questions

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This document contains strategic questions derived from system analytics and performance data.

## Questions for Leadership

"""
        
        for question in questions:
            content += f"{question}\n\n"
        
        content += f"""
## Data Sources

- Weekly CEO Reports: Last 4 weeks analyzed
- Retry Logs: System reliability data
- Completed Tasks: Performance trends
- System Memory: Historical patterns

---
*Automatically generated by CEO Question Generator*
"""

        # Create the questions file
        questions_file = reports_path / f"CEO_Questions_{datetime.now().strftime('%Y%m%d')}.md"
        with open(questions_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"CEO questions saved to: {questions_file}")
        return questions_file

    def run_question_generation(self):
        """Run the CEO question generation process"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Generating CEO strategic questions")
        
        # Generate questions
        questions = self.generate_ceo_questions()
        
        if questions:
            # Save to file
            self.save_ceo_questions(questions)
            print(f"Generated {len(questions)} strategic questions for CEO review")
        else:
            print("No strategic questions generated - insufficient data")

def main():
    """Main function to run the CEO question generator"""
    print("="*60)
    print("CEO QUESTION GENERATOR")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    generator = CEOQuestionGenerator()
    generator.run_question_generation()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] CEO question generation completed")

if __name__ == "__main__":
    main()