#!/usr/bin/env python3
"""
Monitor all running batch benchmarks and display progress.
"""
import re
import time
from pathlib import Path
from datetime import datetime

# Task IDs and their descriptions
TASKS = {
    'b1b8931': ('Batch 1', 'Synthetic L=0', 240),
    'bc9815e': ('Batch 2', 'Synthetic L=4', 240),
    'baf7cdb': ('Batch 3', 'Synthetic L=stochastic', 240),
    'bf4fa20': ('Batch 4', 'Real L=0', 200),
    'bccd28d': ('Batch 5', 'Real L=4', 200),
    'b82389a': ('Batch 6', 'Real L=stochastic', 200),
}

OUTPUT_DIR = Path('/tmp/claude-578122960/-shared-share-malatown/tasks')

def extract_progress(output_file):
    """Extract progress information from output file."""
    if not output_file.exists():
        return None

    try:
        content = output_file.read_text()

        # Extract key metrics
        total_found = re.search(r'Total instances found: (\d+)', content)
        skipped = re.search(r'Already completed \(skipped\): (\d+)', content)
        to_run = re.search(r'Instances to run: (\d+)', content)

        # Count completed instances from log messages
        completed_matches = re.findall(r'\[(\d+)/(\d+)\] SUCCESS', content)
        completed_count = len(completed_matches)
        total_tasks = int(completed_matches[-1][1]) if completed_matches else 0

        # Count failures
        failed_matches = re.findall(r'\[(\d+)/(\d+)\] FAILED', content)
        failed_count = len(failed_matches)

        # Check if batch is complete
        batch_complete = 'BATCH RUN SUMMARY' in content

        return {
            'total_found': int(total_found.group(1)) if total_found else 0,
            'skipped': int(skipped.group(1)) if skipped else 0,
            'to_run': int(to_run.group(1)) if to_run else 0,
            'completed': completed_count,
            'failed': failed_count,
            'total_tasks': total_tasks,
            'batch_complete': batch_complete,
        }
    except Exception as e:
        return {'error': str(e)}

def format_progress_bar(completed, total, width=30):
    """Create a text progress bar."""
    if total == 0:
        return '[' + ' ' * width + '] 0%'

    percent = completed / total
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    return f'[{bar}] {percent*100:.1f}%'

def monitor_once():
    """Check all tasks once and display status."""
    print("\n" + "="*100)
    print(f"📊 BATCH BENCHMARK MONITORING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)

    total_completed = 0
    total_to_run = 0
    total_failed = 0
    all_complete = True

    for task_id, (batch_name, description, expected_instances) in TASKS.items():
        output_file = OUTPUT_DIR / f'{task_id}.output'
        progress = extract_progress(output_file)

        if progress is None:
            print(f"\n{batch_name}: {description}")
            print(f"  ⏳ Initializing...")
            all_complete = False
            continue

        if 'error' in progress:
            print(f"\n{batch_name}: {description}")
            print(f"  ⚠️  Error reading progress: {progress['error']}")
            all_complete = False
            continue

        # Update totals
        to_run = progress['to_run']
        completed = progress['completed']
        failed = progress['failed']

        total_to_run += to_run
        total_completed += completed
        total_failed += failed

        if not progress['batch_complete']:
            all_complete = False

        # Display status
        print(f"\n{batch_name}: {description}")
        print(f"  Total instances: {progress['total_found']} | Skipped: {progress['skipped']} | To run: {to_run}")

        if progress['batch_complete']:
            print(f"  ✅ COMPLETE - {completed} succeeded, {failed} failed")
        else:
            progress_bar = format_progress_bar(completed, to_run, width=40)
            print(f"  {progress_bar}")
            print(f"  Progress: {completed}/{to_run} completed, {failed} failed")

            if to_run > 0:
                remaining = to_run - completed - failed
                print(f"  Remaining: {remaining} instances")

    # Overall summary
    print("\n" + "="*100)
    print("📈 OVERALL PROGRESS")
    print("="*100)
    print(f"Total instances to process: {total_to_run}")
    print(f"Completed: {total_completed} | Failed: {total_failed} | Remaining: {total_to_run - total_completed - total_failed}")

    if total_to_run > 0:
        overall_bar = format_progress_bar(total_completed, total_to_run, width=50)
        print(f"{overall_bar}")

    if all_complete:
        print("\n🎉 ALL BATCHES COMPLETE!")
        return True

    return False

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        # Continuous monitoring mode
        interval = 60  # Check every 60 seconds
        try:
            while True:
                complete = monitor_once()
                if complete:
                    break
                print(f"\n⏱️  Next update in {interval} seconds... (Press Ctrl+C to stop)")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped by user")
    else:
        # Single check
        monitor_once()
