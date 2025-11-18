"""
Celery Configuration Settings
Defines broker, backend, task settings, rate limits, and scheduling options
"""
from datetime import timedelta
from celery.schedules import crontab

# =====================
# BROKER SETTINGS
# =====================
# Redis as message broker (alternative: RabbitMQ)
broker_url = 'redis://localhost:6379/0'

# Result backend for storing task results
result_backend = 'redis://localhost:6379/1'

# Serialization
accept_content = ['json', 'pickle']
task_serializer = 'json'
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# =====================
# TASK EXECUTION
# =====================
# Task execution settings
task_acks_late = True  # Acknowledge tasks after execution (safer)
task_reject_on_worker_lost = True  # Reject task if worker is lost
worker_prefetch_multiplier = 4  # How many tasks to prefetch per worker
worker_max_tasks_per_child = 1000  # Restart worker after N tasks (prevent memory leaks)

# Task time limits
task_soft_time_limit = 3600  # 1 hour soft limit (raises exception)
task_time_limit = 3900  # 1 hour 5 min hard limit (kills task)

# Task result settings
result_expires = 86400  # Results expire after 24 hours
task_ignore_result = False  # Store all results
task_store_errors_even_if_ignored = True

# =====================
# RETRY SETTINGS
# =====================
# Default retry policy
task_default_retry_delay = 60  # Retry after 60 seconds
task_max_retries = 3  # Maximum 3 retries

# Exponential backoff for retries
task_autoretry_for = (Exception,)  # Auto-retry for these exceptions
task_retry_backoff = True  # Use exponential backoff
task_retry_backoff_max = 600  # Max 10 minutes between retries
task_retry_jitter = True  # Add randomness to prevent thundering herd

# =====================
# RATE LIMITING
# =====================
# Global rate limits (tasks per second)
task_default_rate_limit = '100/m'  # 100 tasks per minute

# Specific task rate limits (defined in tasks)
# These are applied per task type
task_annotations = {
    'tasks.osint.domain_scan': {
        'rate_limit': '10/m',  # 10 domain scans per minute
    },
    'tasks.osint.email_enumeration': {
        'rate_limit': '20/m',  # 20 email enumerations per minute
    },
    'tasks.osint.social_media_scan': {
        'rate_limit': '5/m',  # 5 social media scans per minute
    },
    'tasks.osint.whois_lookup': {
        'rate_limit': '30/m',  # 30 WHOIS lookups per minute
    },
    'tasks.osint.dns_enumeration': {
        'rate_limit': '50/m',  # 50 DNS queries per minute
    },
}

# =====================
# WORKER SETTINGS
# =====================
# Worker pool settings
worker_pool = 'prefork'  # Options: prefork, eventlet, gevent, solo
worker_concurrency = 4  # Number of worker processes (adjust based on CPU cores)
worker_disable_rate_limits = False  # Enable rate limiting

# Worker behavior
worker_send_task_events = True  # Enable task events for monitoring
task_send_sent_event = True  # Send task-sent events

# =====================
# MONITORING & LOGGING
# =====================
# Enable monitoring
worker_enable_remote_control = True  # Allow remote control commands

# Event settings for monitoring tools (Flower, etc.)
task_track_started = True  # Track when tasks start
task_publish_retry = True  # Retry publishing task to broker if failed

# =====================
# BEAT SCHEDULE (CRON JOBS)
# =====================
beat_schedule = {
    # Every 5 minutes: Check for new threat intelligence
    'check-threat-intelligence': {
        'task': 'tasks.scheduled.check_threat_feeds',
        'schedule': timedelta(minutes=5),
        'options': {'queue': 'high', 'priority': 7}
    },

    # Every hour: Domain reputation check
    'hourly-domain-reputation': {
        'task': 'tasks.scheduled.check_domain_reputation',
        'schedule': crontab(minute=0),  # Every hour at minute 0
        'options': {'queue': 'default'}
    },

    # Every day at midnight: Generate daily report
    'daily-report': {
        'task': 'tasks.scheduled.generate_daily_report',
        'schedule': crontab(hour=0, minute=0),  # Midnight UTC
        'options': {'queue': 'batch'}
    },

    # Every Monday at 9 AM: Weekly vulnerability scan
    'weekly-vulnerability-scan': {
        'task': 'tasks.scheduled.weekly_vulnerability_scan',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
        'options': {'queue': 'default'}
    },

    # Every 15 minutes: Monitor social media mentions
    'monitor-social-media': {
        'task': 'tasks.scheduled.monitor_social_media',
        'schedule': timedelta(minutes=15),
        'options': {'queue': 'low'}
    },

    # Every 6 hours: Update IP reputation database
    'update-ip-reputation': {
        'task': 'tasks.scheduled.update_ip_reputation',
        'schedule': timedelta(hours=6),
        'options': {'queue': 'default'}
    },

    # First day of month at 2 AM: Archive old data
    'monthly-archive': {
        'task': 'tasks.scheduled.archive_old_data',
        'schedule': crontab(hour=2, minute=0, day_of_month=1),
        'options': {'queue': 'batch', 'priority': 1}
    },

    # Every 30 minutes: Clean up temporary files
    'cleanup-temp-files': {
        'task': 'tasks.scheduled.cleanup_temp_files',
        'schedule': timedelta(minutes=30),
        'options': {'queue': 'low'}
    },
}

# =====================
# SECURITY
# =====================
# Security settings
task_always_eager = False  # Set to True for testing (executes tasks synchronously)
task_eager_propagates = True  # Propagate exceptions in eager mode

# =====================
# CELERY BEAT SCHEDULER
# =====================
# Scheduler backend for beat
beat_scheduler = 'celery.beat:PersistentScheduler'
beat_schedule_filename = '/tmp/celerybeat-schedule'  # Beat schedule database

# =====================
# OPTIMIZATION
# =====================
# Optimization settings
broker_pool_limit = 10  # Connection pool size
broker_connection_retry = True
broker_connection_retry_on_startup = True
broker_connection_max_retries = 10

# Result backend optimization
result_backend_max_retries = 10
result_backend_retry_on_timeout = True

# Task compression
task_compression = 'gzip'
result_compression = 'gzip'

# =====================
# CUSTOM SETTINGS
# =====================
# Custom application settings
osint_settings = {
    'max_concurrent_scans': 10,
    'scan_timeout': 300,  # 5 minutes
    'enable_caching': True,
    'cache_ttl': 3600,  # 1 hour
}
