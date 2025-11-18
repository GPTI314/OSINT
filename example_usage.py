"""
Example Usage of OSINT Celery Task System
Demonstrates how to use various tasks, scheduling, and monitoring features
"""
from celery import chain, group, chord
from celery_app import app
from tasks.osint import (
    domain_scan, email_enumeration, social_media_scan,
    threat_intelligence, emergency_scan, bulk_export,
    whois_lookup, dns_enumeration
)
from tasks.scheduled import schedule_custom_scan
from tasks.events import (
    on_threat_detected, on_new_ioc, trigger_investigation_workflow,
    webhook_handler
)
from monitor import CeleryMonitor
import time
import json


def example_basic_tasks():
    """Example 1: Basic task execution"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Task Execution")
    print("="*80 + "\n")

    # Simple domain scan
    print("1. Submitting domain scan task...")
    result = domain_scan.delay('example.com', deep_scan=True)
    print(f"   Task ID: {result.id}")
    print(f"   Status: {result.status}")

    # Email enumeration
    print("\n2. Submitting email enumeration task...")
    result = email_enumeration.delay('example.com')
    print(f"   Task ID: {result.id}")

    # Social media scan
    print("\n3. Submitting social media scan task...")
    result = social_media_scan.delay('john_doe', platforms=['Twitter', 'LinkedIn'])
    print(f"   Task ID: {result.id}")

    print("\nTasks submitted! Use monitor.py to check status.")


def example_priority_queues():
    """Example 2: Task prioritization"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Task Prioritization")
    print("="*80 + "\n")

    # Critical priority task
    print("1. Critical priority - Emergency scan")
    result = emergency_scan.apply_async(
        args=['suspicious-domain.com', 'full'],
        queue='critical',
        priority=10
    )
    print(f"   Task ID: {result.id}")
    print(f"   Queue: critical, Priority: 10")

    # High priority task
    print("\n2. High priority - Threat intelligence")
    result = threat_intelligence.apply_async(
        args=['192.168.1.1', 'ip'],
        queue='high',
        priority=7
    )
    print(f"   Task ID: {result.id}")
    print(f"   Queue: high, Priority: 7")

    # Low priority task
    print("\n3. Low priority - Social media scan")
    result = social_media_scan.apply_async(
        args=['username'],
        queue='low',
        priority=3
    )
    print(f"   Task ID: {result.id}")
    print(f"   Queue: low, Priority: 3")

    # Batch priority task
    print("\n4. Batch priority - Bulk export")
    result = bulk_export.apply_async(
        args=['json'],
        queue='batch',
        priority=1
    )
    print(f"   Task ID: {result.id}")
    print(f"   Queue: batch, Priority: 1")


def example_retry_logic():
    """Example 3: Automatic retry with exponential backoff"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Retry Logic")
    print("="*80 + "\n")

    print("Submitting task with automatic retry on failure...")
    print("- Max retries: 5")
    print("- Retry backoff: Exponential (60s, 120s, 240s, etc.)")
    print("- Retry jitter: Enabled (adds randomness)")

    result = domain_scan.apply_async(
        args=['example.com'],
        kwargs={'deep_scan': True},
        retry=True,
        retry_policy={
            'max_retries': 5,
            'interval_start': 60,
            'interval_step': 60,
            'interval_max': 600,
        }
    )

    print(f"\nTask ID: {result.id}")
    print("Task will automatically retry if it fails due to network errors")


def example_scheduled_tasks():
    """Example 4: Schedule tasks for future execution"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Scheduled Tasks")
    print("="*80 + "\n")

    from datetime import datetime, timedelta

    # Schedule task to run in 5 minutes
    eta_time = datetime.now() + timedelta(minutes=5)
    print(f"1. Scheduling task to run at {eta_time}")
    result = domain_scan.apply_async(
        args=['scheduled-domain.com'],
        eta=eta_time
    )
    print(f"   Task ID: {result.id}")

    # Schedule task with countdown
    print("\n2. Scheduling task to run in 300 seconds")
    result = email_enumeration.apply_async(
        args=['example.com'],
        countdown=300  # 5 minutes
    )
    print(f"   Task ID: {result.id}")

    # Custom scheduled scan
    print("\n3. Scheduling custom scan")
    result = schedule_custom_scan.delay(
        'target.com',
        'vulnerability',
        '2024-12-31 23:59:59'
    )
    print(f"   Task ID: {result.id}")


def example_task_chains():
    """Example 5: Chain tasks together"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Task Chains (Sequential Execution)")
    print("="*80 + "\n")

    print("Creating task chain: WHOIS -> DNS -> Domain Scan")

    # Chain: whois_lookup -> dns_enumeration -> domain_scan
    workflow = chain(
        whois_lookup.s('example.com'),
        dns_enumeration.s('example.com'),
        domain_scan.s('example.com', deep_scan=True)
    )

    result = workflow.apply_async()
    print(f"Workflow ID: {result.id}")
    print("Tasks will execute sequentially")


def example_task_groups():
    """Example 6: Run tasks in parallel"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Task Groups (Parallel Execution)")
    print("="*80 + "\n")

    print("Creating task group - all tasks run in parallel:")

    # Group: Multiple tasks running simultaneously
    job = group(
        domain_scan.s('example1.com'),
        domain_scan.s('example2.com'),
        domain_scan.s('example3.com'),
        email_enumeration.s('example1.com'),
        whois_lookup.s('example2.com')
    )

    result = job.apply_async()
    print(f"Group ID: {result.id}")
    print("All 5 tasks will execute in parallel")


def example_task_chord():
    """Example 7: Chord - Group with callback"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Chord (Parallel + Callback)")
    print("="*80 + "\n")

    print("Creating chord: Parallel scans -> Export results")

    # Chord: Run multiple scans, then export results
    workflow = chord(
        group(
            domain_scan.s('example1.com'),
            domain_scan.s('example2.com'),
            domain_scan.s('example3.com')
        )
    )(bulk_export.s('json'))  # Callback after all complete

    result = workflow.apply_async()
    print(f"Chord ID: {result.id}")
    print("Scans run in parallel, then results are exported")


def example_event_driven():
    """Example 8: Event-driven tasks"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Event-Driven Tasks")
    print("="*80 + "\n")

    # Simulate threat detection event
    print("1. Triggering threat detection event...")
    threat_data = {
        'type': 'malware',
        'level': 'critical',
        'target': 'malicious-site.com',
        'details': 'Trojan detected in download section'
    }
    result = on_threat_detected.delay(threat_data)
    print(f"   Task ID: {result.id}")

    # Simulate new IoC event
    print("\n2. Triggering new IoC event...")
    ioc_data = {
        'type': 'ip',
        'value': '192.168.1.100',
        'source': 'threat_feed',
        'confidence': 95
    }
    result = on_new_ioc.delay(ioc_data)
    print(f"   Task ID: {result.id}")

    # Trigger investigation workflow
    print("\n3. Triggering investigation workflow...")
    result = trigger_investigation_workflow.delay(
        'suspicious-domain.com',
        'comprehensive'
    )
    print(f"   Task ID: {result.id}")


def example_webhook_integration():
    """Example 9: Webhook-triggered tasks"""
    print("\n" + "="*80)
    print("EXAMPLE 9: Webhook Integration")
    print("="*80 + "\n")

    # Simulate webhook data
    webhook_payloads = [
        {
            'event_type': 'threat_detected',
            'payload': {
                'type': 'phishing',
                'level': 'high',
                'target': 'fake-bank.com'
            }
        },
        {
            'event_type': 'new_ioc',
            'payload': {
                'type': 'domain',
                'value': 'malicious.com',
                'threat_level': 'critical'
            }
        },
        {
            'event_type': 'investigation_request',
            'payload': {
                'target': 'target-company.com',
                'type': 'comprehensive'
            }
        }
    ]

    print("Simulating webhook events:\n")
    for i, webhook_data in enumerate(webhook_payloads, 1):
        print(f"{i}. Event: {webhook_data['event_type']}")
        result = webhook_handler.delay(webhook_data)
        print(f"   Task ID: {result.id}")
        print()


def example_rate_limiting():
    """Example 10: Rate limiting in action"""
    print("\n" + "="*80)
    print("EXAMPLE 10: Rate Limiting")
    print("="*80 + "\n")

    print("Submitting 20 domain scans (rate limit: 10/minute)")
    print("Tasks will be throttled automatically\n")

    results = []
    for i in range(20):
        result = domain_scan.delay(f'example{i}.com')
        results.append(result.id)
        print(f"  {i+1}. Submitted: {result.id}")

    print(f"\nSubmitted {len(results)} tasks")
    print("Only 10 will execute per minute due to rate limiting")


def example_monitoring():
    """Example 11: Monitor tasks and queues"""
    print("\n" + "="*80)
    print("EXAMPLE 11: Task Monitoring")
    print("="*80 + "\n")

    monitor = CeleryMonitor()

    print("1. Active workers:")
    workers = monitor.get_active_workers()
    for worker in workers:
        print(f"   - {worker}")

    print("\n2. Queue status:")
    queues = monitor.get_queue_lengths()
    for queue_name, length in queues.items():
        print(f"   {queue_name}: {length} tasks pending")

    print("\n3. Active tasks:")
    active = monitor.get_active_tasks_detailed()
    if active:
        for worker, tasks in active.items():
            print(f"   Worker {worker}: {len(tasks)} tasks")
    else:
        print("   No active tasks")

    print("\nFor full dashboard, run: python monitor.py dashboard")


def example_complex_workflow():
    """Example 12: Complex investigation workflow"""
    print("\n" + "="*80)
    print("EXAMPLE 12: Complex Investigation Workflow")
    print("="*80 + "\n")

    target = 'investigation-target.com'

    print(f"Starting comprehensive investigation for: {target}\n")

    # Phase 1: Initial reconnaissance (parallel)
    print("Phase 1: Initial Reconnaissance (Parallel)")
    phase1 = group(
        whois_lookup.s(target),
        dns_enumeration.s(target),
        threat_intelligence.s(target, 'domain')
    )

    # Phase 2: Deep analysis (sequential, based on phase 1)
    print("Phase 2: Deep Domain Analysis")
    phase2 = domain_scan.s(target, deep_scan=True)

    # Phase 3: Related entity discovery (parallel)
    print("Phase 3: Related Entity Discovery")
    phase3 = group(
        email_enumeration.s(target),
        social_media_scan.s(target.split('.')[0])
    )

    # Phase 4: Export results
    print("Phase 4: Export Results")
    phase4 = bulk_export.s('json')

    # Combine into complete workflow
    workflow = chain(
        phase1,
        phase2,
        phase3,
        phase4
    )

    result = workflow.apply_async()
    print(f"\nWorkflow ID: {result.id}")
    print("Investigation started - tasks will execute in phases")


def example_task_result_retrieval():
    """Example 13: Retrieve and wait for task results"""
    print("\n" + "="*80)
    print("EXAMPLE 13: Retrieve Task Results")
    print("="*80 + "\n")

    print("1. Submit task and wait for result:")
    result = whois_lookup.delay('example.com')
    print(f"   Task ID: {result.id}")
    print(f"   Waiting for result...")

    # Wait for result (with timeout)
    try:
        output = result.get(timeout=10)
        print(f"   Result: {json.dumps(output, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n2. Check task status without blocking:")
    result = domain_scan.delay('example.com')
    print(f"   Task ID: {result.id}")
    print(f"   Status: {result.status}")
    print(f"   Ready: {result.ready()}")
    print(f"   Successful: {result.successful() if result.ready() else 'N/A'}")


def print_menu():
    """Print example menu"""
    menu = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                   OSINT CELERY TASK SYSTEM - EXAMPLES                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Select an example to run:

 1.  Basic Task Execution
 2.  Task Prioritization (Critical/High/Low/Batch Queues)
 3.  Automatic Retry with Exponential Backoff
 4.  Scheduled Tasks (Future Execution)
 5.  Task Chains (Sequential Execution)
 6.  Task Groups (Parallel Execution)
 7.  Task Chord (Parallel + Callback)
 8.  Event-Driven Tasks
 9.  Webhook Integration
10.  Rate Limiting
11.  Task Monitoring
12.  Complex Investigation Workflow
13.  Task Result Retrieval
 0.  Run All Examples

 q.  Quit

"""
    print(menu)


def main():
    """Main entry point for examples"""
    examples = {
        '1': example_basic_tasks,
        '2': example_priority_queues,
        '3': example_retry_logic,
        '4': example_scheduled_tasks,
        '5': example_task_chains,
        '6': example_task_groups,
        '7': example_task_chord,
        '8': example_event_driven,
        '9': example_webhook_integration,
        '10': example_rate_limiting,
        '11': example_monitoring,
        '12': example_complex_workflow,
        '13': example_task_result_retrieval,
    }

    while True:
        print_menu()
        choice = input("Enter your choice: ").strip()

        if choice == 'q':
            print("\nGoodbye!")
            break
        elif choice == '0':
            print("\nRunning all examples...\n")
            for func in examples.values():
                func()
                time.sleep(2)
            print("\n✓ All examples completed!")
            break
        elif choice in examples:
            examples[choice]()
            input("\nPress Enter to continue...")
        else:
            print("\nInvalid choice! Please try again.")
            time.sleep(1)


if __name__ == '__main__':
    print("\n" + "="*80)
    print("OSINT Celery Task System - Example Usage")
    print("="*80)
    print("\nNOTE: Make sure Redis and Celery workers are running before executing examples")
    print("      Start worker: celery -A celery_app worker -l info")
    print("      Start beat: celery -A celery_app beat -l info")
    print("="*80 + "\n")

    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nError: {e}")
