"""Celery tasks for intelligence gathering."""

from loguru import logger
from typing import Dict, Any

from .celery_app import celery_app
from osint.domain_intelligence import DomainIntelligence
from osint.ip_intelligence import IPIntelligence
from osint.email_intelligence import EmailIntelligence


@celery_app.task(name="tasks.intelligence_tasks.gather_domain_intelligence")
def gather_domain_intelligence(
    domain: str,
    include_subdomains: bool = True,
    include_technology: bool = True,
) -> Dict[str, Any]:
    """
    Gather intelligence on a domain.

    Args:
        domain: Domain to investigate
        include_subdomains: Include subdomain enumeration
        include_technology: Include technology detection

    Returns:
        Intelligence data
    """
    try:
        logger.info(f"Starting domain intelligence task: {domain}")

        intel = DomainIntelligence()

        import asyncio
        result = asyncio.run(
            intel.gather_intelligence(domain, include_subdomains, include_technology)
        )

        logger.info(f"Domain intelligence completed: {domain}")
        return result

    except Exception as e:
        logger.error(f"Domain intelligence failed: {domain} - {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "domain": domain,
        }


@celery_app.task(name="tasks.intelligence_tasks.gather_ip_intelligence")
def gather_ip_intelligence(ip_address: str) -> Dict[str, Any]:
    """
    Gather intelligence on an IP address.

    Args:
        ip_address: IP address to investigate

    Returns:
        Intelligence data
    """
    try:
        logger.info(f"Starting IP intelligence task: {ip_address}")

        intel = IPIntelligence()

        import asyncio
        result = asyncio.run(intel.gather_intelligence(ip_address))

        logger.info(f"IP intelligence completed: {ip_address}")
        return result

    except Exception as e:
        logger.error(f"IP intelligence failed: {ip_address} - {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "ip_address": ip_address,
        }


@celery_app.task(name="tasks.intelligence_tasks.gather_email_intelligence")
def gather_email_intelligence(email: str) -> Dict[str, Any]:
    """
    Gather intelligence on an email address.

    Args:
        email: Email address to investigate

    Returns:
        Intelligence data
    """
    try:
        logger.info(f"Starting email intelligence task: {email}")

        intel = EmailIntelligence()

        import asyncio
        result = asyncio.run(intel.gather_intelligence(email))

        logger.info(f"Email intelligence completed: {email}")
        return result

    except Exception as e:
        logger.error(f"Email intelligence failed: {email} - {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "email": email,
        }
