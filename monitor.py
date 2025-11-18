"""
Celery Task Monitoring and Management Tools
Provides utilities for monitoring task queues, workers, and task status
"""
from celery_app import app, get_task_info, cancel_task, get_active_tasks, get_scheduled_tasks, get_queue_stats
from celery.result import AsyncResult
from tabulate import tabulate
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CeleryMonitor:
    """Monitor and manage Celery tasks and workers"""

    def __init__(self):
        self.inspect = app.control.inspect()

    def get_worker_stats(self) -> Dict[str, Any]:
        """Get statistics for all workers"""
        logger.info("Fetching worker statistics...")
        stats = self.inspect.stats()

        if not stats:
            logger.warning("No active workers found")
            return {}

        return stats

    def get_active_workers(self) -> List[str]:
        """Get list of active worker names"""
        stats = self.get_worker_stats()
        return list(stats.keys()) if stats else []

    def get_registered_tasks(self) -> Dict[str, List[str]]:
        """Get all registered tasks per worker"""
        logger.info("Fetching registered tasks...")
        registered = self.inspect.registered()
        return registered if registered else {}

    def get_active_tasks_detailed(self) -> Dict[str, List[Dict]]:
        """Get detailed information about active tasks"""
        logger.info("Fetching active tasks...")
        active = self.inspect.active()
        return active if active else {}

    def get_reserved_tasks(self) -> Dict[str, List[Dict]]:
        """Get reserved (prefetched) tasks"""
        logger.info("Fetching reserved tasks...")
        reserved = self.inspect.reserved()
        return reserved if reserved else {}

    def get_scheduled_tasks_detailed(self) -> Dict[str, List[Dict]]:
        """Get scheduled tasks"""
        logger.info("Fetching scheduled tasks...")
        scheduled = self.inspect.scheduled()
        return scheduled if scheduled else {}

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get detailed status of a specific task"""
        return get_task_info(task_id)

    def cancel_task_by_id(self, task_id: str, terminate: bool = False):
        """Cancel a task by ID"""
        logger.info(f"Cancelling task {task_id} (terminate={terminate})")
        cancel_task(task_id, terminate)

    def purge_queue(self, queue_name: str = None) -> int:
        """Purge all tasks from a queue"""
        if queue_name:
            logger.warning(f"Purging queue: {queue_name}")
            count = app.control.purge()
        else:
            logger.warning("Purging all queues")
            count = app.control.purge()

        logger.info(f"Purged {count} tasks")
        return count

    def get_queue_lengths(self) -> Dict[str, int]:
        """Get the number of tasks in each queue"""
        from kombu import Connection

        queue_names = ['critical', 'high', 'default', 'low', 'batch']
        lengths = {}

        try:
            with Connection(app.conf.broker_url) as conn:
                for queue_name in queue_names:
                    try:
                        queue = conn.SimpleQueue(queue_name)
                        lengths[queue_name] = queue.qsize()
                        queue.close()
                    except Exception as e:
                        logger.error(f"Error getting length for {queue_name}: {e}")
                        lengths[queue_name] = -1
        except Exception as e:
            logger.error(f"Error connecting to broker: {e}")

        return lengths

    def print_worker_stats(self):
        """Print formatted worker statistics"""
        stats = self.get_worker_stats()

        if not stats:
            print("No active workers found!")
            return

        print("\n" + "=" * 80)
        print("WORKER STATISTICS")
        print("=" * 80 + "\n")

        for worker_name, worker_stats in stats.items():
            print(f"Worker: {worker_name}")
            print(f"  Total Tasks: {worker_stats.get('total', {})}")
            print(f"  Pool: {worker_stats.get('pool', {})}")
            print(f"  Broker: {worker_stats.get('broker', {})}")
            print()

    def print_active_tasks(self):
        """Print formatted active tasks"""
        active = self.get_active_tasks_detailed()

        if not active or all(len(tasks) == 0 for tasks in active.values()):
            print("\nNo active tasks")
            return

        print("\n" + "=" * 80)
        print("ACTIVE TASKS")
        print("=" * 80 + "\n")

        for worker_name, tasks in active.items():
            if tasks:
                print(f"Worker: {worker_name}")
                for task in tasks:
                    print(f"  Task: {task['name']}")
                    print(f"    ID: {task['id']}")
                    print(f"    Args: {task.get('args', [])}")
                    print(f"    Started: {task.get('time_start', 'N/A')}")
                    print()

    def print_queue_status(self):
        """Print status of all queues"""
        lengths = self.get_queue_lengths()

        print("\n" + "=" * 80)
        print("QUEUE STATUS")
        print("=" * 80 + "\n")

        table_data = []
        for queue_name, length in lengths.items():
            status = "OK" if length >= 0 else "ERROR"
            table_data.append([queue_name, length if length >= 0 else "N/A", status])

        headers = ["Queue", "Tasks Pending", "Status"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print()

    def print_scheduled_tasks(self):
        """Print scheduled tasks"""
        scheduled = self.get_scheduled_tasks_detailed()

        if not scheduled or all(len(tasks) == 0 for tasks in scheduled.values()):
            print("\nNo scheduled tasks")
            return

        print("\n" + "=" * 80)
        print("SCHEDULED TASKS")
        print("=" * 80 + "\n")

        for worker_name, tasks in scheduled.items():
            if tasks:
                print(f"Worker: {worker_name}")
                for task in tasks:
                    print(f"  Task: {task['request']['name']}")
                    print(f"    ID: {task['request']['id']}")
                    print(f"    ETA: {task.get('eta', 'N/A')}")
                    print()

    def print_dashboard(self):
        """Print complete monitoring dashboard"""
        print("\n" + "=" * 80)
        print("CELERY TASK MONITORING DASHBOARD")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        self.print_worker_stats()
        self.print_queue_status()
        self.print_active_tasks()
        self.print_scheduled_tasks()


class TaskLogger:
    """Enhanced logging for task execution"""

    @staticmethod
    def log_task_start(task_name: str, task_id: str, args: tuple, kwargs: dict):
        """Log task start with details"""
        logger.info(f"[TASK START] {task_name}[{task_id}]")
        logger.info(f"  Args: {args}")
        logger.info(f"  Kwargs: {kwargs}")
        logger.info(f"  Timestamp: {datetime.now()}")

    @staticmethod
    def log_task_success(task_name: str, task_id: str, result: Any, duration: float):
        """Log successful task completion"""
        logger.info(f"[TASK SUCCESS] {task_name}[{task_id}]")
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info(f"  Result: {result}")

    @staticmethod
    def log_task_failure(task_name: str, task_id: str, error: Exception, duration: float):
        """Log task failure"""
        logger.error(f"[TASK FAILURE] {task_name}[{task_id}]")
        logger.error(f"  Duration: {duration:.2f}s")
        logger.error(f"  Error: {error}")

    @staticmethod
    def log_task_retry(task_name: str, task_id: str, retry_count: int, max_retries: int):
        """Log task retry"""
        logger.warning(f"[TASK RETRY] {task_name}[{task_id}]")
        logger.warning(f"  Retry: {retry_count}/{max_retries}")


def print_help():
    """Print help message"""
    help_text = """
Celery Monitor - Task Monitoring and Management Tool

Usage: python monitor.py <command> [options]

Commands:
  dashboard           Show complete monitoring dashboard
  workers             Show worker statistics
  active              Show active tasks
  scheduled           Show scheduled tasks
  queues              Show queue status
  task <task_id>      Show detailed task information
  cancel <task_id>    Cancel a specific task
  purge [queue]       Purge tasks from queue (or all queues)
  help                Show this help message

Examples:
  python monitor.py dashboard
  python monitor.py workers
  python monitor.py task abc123-def456-ghi789
  python monitor.py cancel abc123-def456-ghi789
  python monitor.py purge default
"""
    print(help_text)


def main():
    """Main entry point for monitoring CLI"""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()
    monitor = CeleryMonitor()

    try:
        if command == 'dashboard':
            monitor.print_dashboard()

        elif command == 'workers':
            monitor.print_worker_stats()

        elif command == 'active':
            monitor.print_active_tasks()

        elif command == 'scheduled':
            monitor.print_scheduled_tasks()

        elif command == 'queues':
            monitor.print_queue_status()

        elif command == 'task':
            if len(sys.argv) < 3:
                print("Error: task_id required")
                return
            task_id = sys.argv[2]
            info = monitor.get_task_status(task_id)
            print(f"\nTask Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")

        elif command == 'cancel':
            if len(sys.argv) < 3:
                print("Error: task_id required")
                return
            task_id = sys.argv[2]
            terminate = '--terminate' in sys.argv
            monitor.cancel_task_by_id(task_id, terminate)
            print(f"Task {task_id} cancelled")

        elif command == 'purge':
            queue = sys.argv[2] if len(sys.argv) > 2 else None
            count = monitor.purge_queue(queue)
            print(f"Purged {count} tasks")

        elif command == 'help':
            print_help()

        else:
            print(f"Unknown command: {command}")
            print_help()

    except Exception as e:
        logger.error(f"Error executing command: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
