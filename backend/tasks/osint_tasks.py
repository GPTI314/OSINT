"""
OSINT collection tasks for Celery.
"""
from celery import Task
from typing import Dict, Any
import logging

from tasks.celery_app import app
from collectors.domain_collector import DomainCollector
from collectors.ip_collector import IPCollector
from collectors.email_collector import EmailCollector
from collectors.social_media_collector import SocialMediaCollector
from collectors.phone_collector import PhoneCollector

logger = logging.getLogger(__name__)


class OSINTTask(Task):
    """Base task class for OSINT operations."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.error(f"Task {task_id} failed: {exc}")

    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        logger.info(f"Task {task_id} completed successfully")


@app.task(base=OSINTTask, bind=True, max_retries=3)
def collect_domain_intelligence(self, domain: str, options: Dict[str, Any] = None):
    """
    Collect intelligence on a domain.

    Args:
        domain: Target domain
        options: Collection options

    Returns:
        Dict containing domain intelligence
    """
    try:
        logger.info(f"Collecting domain intelligence for: {domain}")
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Initializing'})

        collector = DomainCollector()

        self.update_state(state='PROGRESS', meta={'progress': 50, 'status': 'Collecting data'})

        import asyncio
        result = asyncio.run(collector.collect(domain, **(options or {})))

        self.update_state(state='PROGRESS', meta={'progress': 100, 'status': 'Complete'})

        return result

    except Exception as exc:
        logger.error(f"Error collecting domain intelligence: {exc}")
        self.retry(exc=exc, countdown=60)


@app.task(base=OSINTTask, bind=True, max_retries=3)
def collect_ip_intelligence(self, ip: str, options: Dict[str, Any] = None):
    """
    Collect intelligence on an IP address.

    Args:
        ip: Target IP address
        options: Collection options

    Returns:
        Dict containing IP intelligence
    """
    try:
        logger.info(f"Collecting IP intelligence for: {ip}")
        collector = IPCollector()

        import asyncio
        result = asyncio.run(collector.collect(ip, **(options or {})))

        return result

    except Exception as exc:
        logger.error(f"Error collecting IP intelligence: {exc}")
        self.retry(exc=exc, countdown=60)


@app.task(base=OSINTTask, bind=True, max_retries=3)
def collect_email_intelligence(self, email: str, options: Dict[str, Any] = None):
    """
    Collect intelligence on an email address.

    Args:
        email: Target email address
        options: Collection options

    Returns:
        Dict containing email intelligence
    """
    try:
        logger.info(f"Collecting email intelligence for: {email}")
        collector = EmailCollector()

        import asyncio
        result = asyncio.run(collector.collect(email, **(options or {})))

        return result

    except Exception as exc:
        logger.error(f"Error collecting email intelligence: {exc}")
        self.retry(exc=exc, countdown=60)


@app.task(base=OSINTTask, bind=True, max_retries=3)
def collect_social_media_intelligence(self, username: str, options: Dict[str, Any] = None):
    """
    Collect social media intelligence for a username.

    Args:
        username: Target username
        options: Collection options

    Returns:
        Dict containing social media intelligence
    """
    try:
        logger.info(f"Collecting social media intelligence for: {username}")
        collector = SocialMediaCollector()

        import asyncio
        result = asyncio.run(collector.collect(username, **(options or {})))

        return result

    except Exception as exc:
        logger.error(f"Error collecting social media intelligence: {exc}")
        self.retry(exc=exc, countdown=60)


@app.task(base=OSINTTask, bind=True, max_retries=3)
def collect_phone_intelligence(self, phone: str, options: Dict[str, Any] = None):
    """
    Collect intelligence on a phone number.

    Args:
        phone: Target phone number
        options: Collection options

    Returns:
        Dict containing phone intelligence
    """
    try:
        logger.info(f"Collecting phone intelligence for: {phone}")
        collector = PhoneCollector()

        import asyncio
        result = asyncio.run(collector.collect(phone, **(options or {})))

        return result

    except Exception as exc:
        logger.error(f"Error collecting phone intelligence: {exc}")
        self.retry(exc=exc, countdown=60)
