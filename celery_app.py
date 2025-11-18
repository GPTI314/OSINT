"""
Celery Application Configuration
Provides comprehensive task queue system with prioritization, scheduling, and monitoring
"""
from celery import Celery
from celery.signals import (
    task_prerun, task_postrun, task_failure, task_success,
    task_retry, task_revoked
)
from kombu import Queue, Exchange
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Celery application instance
app = Celery('osint_tasks')

# Load configuration from config module
app.config_from_object('celery_config')

# Define task queues with different priorities
TASK_QUEUES = (
    Queue('critical', Exchange('critical'), routing_key='critical',
          queue_arguments={'x-max-priority': 10}),
    Queue('high', Exchange('high'), routing_key='high',
          queue_arguments={'x-max-priority': 7}),
    Queue('default', Exchange('default'), routing_key='default',
          queue_arguments={'x-max-priority': 5}),
    Queue('low', Exchange('low'), routing_key='low',
          queue_arguments={'x-max-priority': 3}),
    Queue('batch', Exchange('batch'), routing_key='batch',
          queue_arguments={'x-max-priority': 1}),
)

app.conf.task_queues = TASK_QUEUES

# Default queue routing
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'

# Task routing rules
app.conf.task_routes = {
    'tasks.osint.emergency_scan': {'queue': 'critical', 'priority': 10},
    'tasks.osint.threat_intelligence': {'queue': 'high', 'priority': 7},
    'tasks.osint.domain_scan': {'queue': 'default', 'priority': 5},
    'tasks.osint.email_enumeration': {'queue': 'default', 'priority': 5},
    'tasks.osint.social_media_scan': {'queue': 'low', 'priority': 3},
    'tasks.osint.bulk_export': {'queue': 'batch', 'priority': 1},
    'tasks.scheduled.*': {'queue': 'default', 'priority': 5},
}

# Auto-discover tasks
app.autodiscover_tasks(['tasks'])


# =====================
# MONITORING & LOGGING
# =====================

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """Log when a task starts"""
    logger.info(f"Task {task.name}[{task_id}] started with args={args}, kwargs={kwargs}")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None,
                         retval=None, state=None, **extra):
    """Log when a task completes"""
    logger.info(f"Task {task.name}[{task_id}] completed with state={state}")


@task_success.connect
def task_success_handler(sender=None, result=None, **extra):
    """Handle successful task completion"""
    logger.info(f"Task {sender.name} succeeded with result: {result}")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None,
                        kwargs=None, traceback=None, einfo=None, **extra):
    """Handle task failures"""
    logger.error(f"Task {sender.name}[{task_id}] failed: {exception}")
    logger.error(f"Traceback: {traceback}")

    # Here you could add alerting logic (email, Slack, etc.)
    # send_alert(f"Task {sender.name} failed", exception)


@task_retry.connect
def task_retry_handler(sender=None, task_id=None, reason=None, einfo=None, **extra):
    """Handle task retries"""
    logger.warning(f"Task {sender.name}[{task_id}] retrying: {reason}")


@task_revoked.connect
def task_revoked_handler(sender=None, request=None, terminated=None,
                         signum=None, expired=None, **extra):
    """Handle revoked tasks"""
    logger.warning(f"Task {sender.name} was revoked. Terminated: {terminated}")


# =====================
# UTILITY FUNCTIONS
# =====================

def get_task_info(task_id):
    """Get information about a task"""
    from celery.result import AsyncResult
    result = AsyncResult(task_id, app=app)

    return {
        'task_id': task_id,
        'state': result.state,
        'result': result.result if result.ready() else None,
        'traceback': result.traceback,
        'info': result.info,
    }


def cancel_task(task_id, terminate=False):
    """Cancel a running task"""
    from celery.result import AsyncResult
    result = AsyncResult(task_id, app=app)
    result.revoke(terminate=terminate)
    logger.info(f"Task {task_id} cancelled (terminate={terminate})")


def get_active_tasks():
    """Get list of currently active tasks"""
    inspect = app.control.inspect()
    active = inspect.active()
    return active


def get_scheduled_tasks():
    """Get list of scheduled tasks"""
    inspect = app.control.inspect()
    scheduled = inspect.scheduled()
    return scheduled


def get_queue_stats():
    """Get statistics about task queues"""
    inspect = app.control.inspect()
    stats = inspect.stats()
    return stats


if __name__ == '__main__':
    app.start()
