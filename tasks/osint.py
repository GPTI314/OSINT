"""
OSINT Collection Tasks
Implements various OSINT data collection tasks with retry logic, rate limiting, and prioritization
"""
from celery import Task
from celery_app import app
from celery.exceptions import SoftTimeLimitExceeded
import logging
import time
import random
import requests
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


# =====================
# BASE TASK CLASS
# =====================
class OSINTTask(Task):
    """
    Base task class with common functionality
    Provides error handling, logging, and retry logic
    """
    autoretry_for = (requests.RequestException, ConnectionError, TimeoutError)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        logger.error(f'{self.name}[{task_id}] failed: {exc}')
        # Send notification, log to database, etc.
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        logger.warning(f'{self.name}[{task_id}] retry: {exc}')
        super().on_retry(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        logger.info(f'{self.name}[{task_id}] succeeded')
        super().on_success(retval, task_id, args, kwargs)


# =====================
# CRITICAL PRIORITY TASKS
# =====================
@app.task(
    base=OSINTTask,
    name='tasks.osint.emergency_scan',
    queue='critical',
    priority=10,
    time_limit=600,
    soft_time_limit=550
)
def emergency_scan(target: str, scan_type: str = 'full') -> Dict[str, Any]:
    """
    Emergency security scan - highest priority
    Used for immediate threat detection
    """
    logger.info(f"Emergency scan initiated for: {target}")

    try:
        results = {
            'target': target,
            'scan_type': scan_type,
            'timestamp': time.time(),
            'status': 'completed',
            'findings': []
        }

        # Simulate emergency scan
        logger.info(f"Running {scan_type} scan on {target}")
        time.sleep(2)  # Simulate scan time

        # Mock findings
        results['findings'] = [
            {'severity': 'high', 'type': 'open_port', 'details': 'Port 22 exposed'},
            {'severity': 'critical', 'type': 'vulnerability', 'details': 'CVE-2024-XXXX detected'}
        ]

        return results

    except SoftTimeLimitExceeded:
        logger.error(f"Emergency scan timed out for {target}")
        raise


@app.task(
    base=OSINTTask,
    name='tasks.osint.threat_intelligence',
    queue='high',
    priority=7,
    rate_limit='30/m'
)
def threat_intelligence(ioc: str, ioc_type: str) -> Dict[str, Any]:
    """
    Threat intelligence lookup - high priority
    Checks IoC (Indicator of Compromise) against threat feeds
    """
    logger.info(f"Threat intelligence check for {ioc_type}: {ioc}")

    results = {
        'ioc': ioc,
        'ioc_type': ioc_type,
        'timestamp': time.time(),
        'threat_level': 'unknown',
        'sources': []
    }

    # Simulate threat feed checks
    threat_feeds = ['VirusTotal', 'AbuseIPDB', 'AlienVault OTX', 'Shodan']

    for feed in threat_feeds:
        try:
            # Simulate API call
            time.sleep(0.5)
            logger.info(f"Checking {feed} for {ioc}")

            # Mock result
            if random.random() > 0.7:
                results['sources'].append({
                    'feed': feed,
                    'status': 'malicious',
                    'confidence': random.randint(60, 100)
                })
                results['threat_level'] = 'high'
            else:
                results['sources'].append({
                    'feed': feed,
                    'status': 'clean',
                    'confidence': random.randint(80, 100)
                })

        except Exception as e:
            logger.error(f"Error checking {feed}: {e}")
            results['sources'].append({
                'feed': feed,
                'status': 'error',
                'error': str(e)
            })

    return results


# =====================
# DEFAULT PRIORITY TASKS
# =====================
@app.task(
    base=OSINTTask,
    name='tasks.osint.domain_scan',
    queue='default',
    priority=5,
    rate_limit='10/m',
    max_retries=3,
    default_retry_delay=60
)
def domain_scan(domain: str, deep_scan: bool = False) -> Dict[str, Any]:
    """
    Domain reconnaissance scan
    Collects DNS, WHOIS, subdomain, and SSL certificate information
    """
    logger.info(f"Domain scan started for: {domain}")

    results = {
        'domain': domain,
        'timestamp': time.time(),
        'dns_records': {},
        'whois': {},
        'subdomains': [],
        'ssl_info': {},
        'deep_scan': deep_scan
    }

    try:
        # Simulate DNS lookups
        logger.info(f"Performing DNS lookup for {domain}")
        time.sleep(1)
        results['dns_records'] = {
            'A': ['192.168.1.1', '192.168.1.2'],
            'MX': ['mail.example.com'],
            'NS': ['ns1.example.com', 'ns2.example.com'],
            'TXT': ['v=spf1 include:_spf.google.com ~all']
        }

        # Simulate WHOIS lookup
        logger.info(f"Performing WHOIS lookup for {domain}")
        time.sleep(1)
        results['whois'] = {
            'registrar': 'Example Registrar',
            'creation_date': '2020-01-01',
            'expiration_date': '2025-01-01',
            'status': 'active'
        }

        # Subdomain enumeration
        if deep_scan:
            logger.info(f"Performing subdomain enumeration for {domain}")
            time.sleep(2)
            results['subdomains'] = [
                f'www.{domain}',
                f'mail.{domain}',
                f'ftp.{domain}',
                f'admin.{domain}'
            ]

        # SSL certificate check
        logger.info(f"Checking SSL certificate for {domain}")
        time.sleep(1)
        results['ssl_info'] = {
            'issued_to': domain,
            'issued_by': 'Example CA',
            'valid_from': '2024-01-01',
            'valid_to': '2025-01-01',
            'signature_algorithm': 'SHA256withRSA'
        }

        return results

    except Exception as e:
        logger.error(f"Domain scan failed for {domain}: {e}")
        raise


@app.task(
    base=OSINTTask,
    name='tasks.osint.email_enumeration',
    queue='default',
    priority=5,
    rate_limit='20/m'
)
def email_enumeration(domain: str, pattern: str = None) -> Dict[str, Any]:
    """
    Email address enumeration
    Discovers email addresses associated with a domain
    """
    logger.info(f"Email enumeration for domain: {domain}")

    results = {
        'domain': domain,
        'pattern': pattern,
        'timestamp': time.time(),
        'emails_found': [],
        'sources': []
    }

    # Simulate email discovery from various sources
    sources = ['Hunter.io', 'LinkedIn', 'GitHub', 'Company Website']

    for source in sources:
        try:
            logger.info(f"Checking {source} for email addresses")
            time.sleep(0.5)

            # Mock email discovery
            num_emails = random.randint(1, 5)
            for i in range(num_emails):
                email = f"user{i}@{domain}"
                if email not in results['emails_found']:
                    results['emails_found'].append(email)

            results['sources'].append({
                'source': source,
                'emails_found': num_emails
            })

        except Exception as e:
            logger.error(f"Error checking {source}: {e}")

    return results


@app.task(
    base=OSINTTask,
    name='tasks.osint.whois_lookup',
    queue='default',
    rate_limit='30/m'
)
def whois_lookup(domain: str) -> Dict[str, Any]:
    """
    WHOIS information lookup
    """
    logger.info(f"WHOIS lookup for: {domain}")

    time.sleep(1)  # Simulate API call

    return {
        'domain': domain,
        'registrar': 'Example Registrar Inc.',
        'registration_date': '2020-01-15',
        'expiration_date': '2025-01-15',
        'nameservers': ['ns1.example.com', 'ns2.example.com'],
        'status': ['clientTransferProhibited', 'clientUpdateProhibited'],
        'dnssec': 'unsigned'
    }


@app.task(
    base=OSINTTask,
    name='tasks.osint.dns_enumeration',
    queue='default',
    rate_limit='50/m'
)
def dns_enumeration(domain: str, record_types: List[str] = None) -> Dict[str, Any]:
    """
    DNS record enumeration
    """
    if record_types is None:
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']

    logger.info(f"DNS enumeration for {domain}: {record_types}")

    results = {
        'domain': domain,
        'timestamp': time.time(),
        'records': {}
    }

    for record_type in record_types:
        time.sleep(0.2)  # Simulate DNS query
        results['records'][record_type] = [f'{record_type.lower()}.{domain}']

    return results


# =====================
# LOW PRIORITY TASKS
# =====================
@app.task(
    base=OSINTTask,
    name='tasks.osint.social_media_scan',
    queue='low',
    priority=3,
    rate_limit='5/m'
)
def social_media_scan(username: str, platforms: List[str] = None) -> Dict[str, Any]:
    """
    Social media profile discovery
    Searches for user profiles across social media platforms
    """
    if platforms is None:
        platforms = ['Twitter', 'LinkedIn', 'Facebook', 'Instagram', 'GitHub']

    logger.info(f"Social media scan for username: {username}")

    results = {
        'username': username,
        'timestamp': time.time(),
        'profiles_found': []
    }

    for platform in platforms:
        try:
            logger.info(f"Checking {platform} for {username}")
            time.sleep(1)  # Simulate API call

            # Mock profile discovery
            if random.random() > 0.4:
                results['profiles_found'].append({
                    'platform': platform,
                    'url': f'https://{platform.lower()}.com/{username}',
                    'status': 'found',
                    'followers': random.randint(10, 10000),
                    'verified': random.choice([True, False])
                })
            else:
                results['profiles_found'].append({
                    'platform': platform,
                    'status': 'not_found'
                })

        except Exception as e:
            logger.error(f"Error checking {platform}: {e}")

    return results


# =====================
# BATCH PROCESSING TASKS
# =====================
@app.task(
    base=OSINTTask,
    name='tasks.osint.bulk_export',
    queue='batch',
    priority=1,
    time_limit=7200  # 2 hours
)
def bulk_export(export_format: str = 'json', filters: Dict = None) -> Dict[str, Any]:
    """
    Bulk data export - lowest priority
    Exports collected OSINT data in specified format
    """
    logger.info(f"Bulk export started: format={export_format}")

    time.sleep(5)  # Simulate export processing

    return {
        'format': export_format,
        'filters': filters,
        'timestamp': time.time(),
        'records_exported': random.randint(1000, 10000),
        'file_path': f'/tmp/export_{int(time.time())}.{export_format}'
    }


# =====================
# CHAINED TASKS
# =====================
@app.task(base=OSINTTask, name='tasks.osint.full_target_analysis')
def full_target_analysis(target: str) -> Dict[str, Any]:
    """
    Complete target analysis - chains multiple tasks
    Demonstrates task composition and workflow
    """
    logger.info(f"Full target analysis for: {target}")

    from celery import chain, group

    # Create a workflow: domain scan -> (threat intel + social media scan) -> export
    workflow = chain(
        domain_scan.s(target, deep_scan=True),
        group(
            threat_intelligence.s(target, 'domain'),
            social_media_scan.s(target.split('.')[0])
        ),
        bulk_export.s('json')
    )

    # Execute workflow
    result = workflow.apply_async()

    return {
        'target': target,
        'workflow_id': result.id,
        'status': 'started'
    }


# =====================
# UTILITY TASKS
# =====================
@app.task(name='tasks.osint.healthcheck')
def healthcheck() -> Dict[str, str]:
    """Simple health check task"""
    return {
        'status': 'healthy',
        'timestamp': time.time()
    }
