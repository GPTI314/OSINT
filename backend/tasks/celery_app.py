"""
Celery application configuration.
"""
from celery import Celery
from config.settings import settings

# Create Celery app
app = Celery(
    "osint_tasks",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
    include=[
        "tasks.osint_tasks",
        "tasks.scraping_tasks",
        "tasks.crawling_tasks",
        "tasks.analysis_tasks",
        "tasks.report_tasks"
    ]
)

# Configure Celery
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3000,  # 50 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True
)

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    "cleanup-old-tasks": {
        "task": "tasks.maintenance.cleanup_old_tasks",
        "schedule": 86400.0,  # Once per day
    },
}

if __name__ == "__main__":
    app.start()
