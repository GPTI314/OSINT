"""Celery application configuration."""

from celery import Celery
from config.settings import settings

# Create Celery application
celery_app = Celery(
    "osint_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "tasks.scraping_tasks",
        "tasks.crawling_tasks",
        "tasks.intelligence_tasks",
        "tasks.processing_tasks",
        "tasks.analysis_tasks",
    ],
)

# Configure Celery
celery_app.conf.update(
    task_track_started=settings.celery_task_track_started,
    task_time_limit=settings.celery_task_time_limit,
    task_soft_time_limit=settings.celery_task_soft_time_limit,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "tasks.scraping_tasks.*": {"queue": "scraping"},
        "tasks.crawling_tasks.*": {"queue": "crawling"},
        "tasks.intelligence_tasks.*": {"queue": "intelligence"},
        "tasks.processing_tasks.*": {"queue": "processing"},
        "tasks.analysis_tasks.*": {"queue": "analysis"},
    },
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
)

# Optional: Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-old-jobs": {
        "task": "tasks.scraping_tasks.cleanup_old_jobs",
        "schedule": 3600.0,  # Every hour
    },
}
