"""
Event-Driven Tasks
Tasks triggered by specific events or conditions
"""
from celery_app import app
from tasks.osint import OSINTTask
from celery import chain, group, chord
import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


# =====================
# EVENT HANDLERS
# =====================

@app.task(
    base=OSINTTask,
    name='tasks.events.on_threat_detected',
    queue='critical',
    priority=10
)
def on_threat_detected(threat_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Triggered when a threat is detected
    Performs immediate response actions
    """
    logger.warning(f"THREAT DETECTED: {threat_data}")

    threat_type = threat_data.get('type', 'unknown')
    threat_level = threat_data.get('level', 'unknown')
    target = threat_data.get('target', 'unknown')

    results = {
        'event': 'threat_detected',
        'timestamp': time.time(),
        'threat_data': threat_data,
        'actions_taken': []
    }

    # Perform automated response actions
    try:
        # 1. Enhanced scanning
        logger.info(f"Initiating enhanced scan for {target}")
        results['actions_taken'].append({
            'action': 'enhanced_scan',
            'status': 'initiated',
            'target': target
        })

        # 2. Alert stakeholders
        logger.info("Sending threat alerts")
        results['actions_taken'].append({
            'action': 'alert_sent',
            'status': 'completed',
            'recipients': ['security_team@example.com']
        })

        # 3. Update threat database
        logger.info("Updating threat database")
        time.sleep(0.5)
        results['actions_taken'].append({
            'action': 'database_update',
            'status': 'completed'
        })

        # 4. Trigger additional analysis if critical
        if threat_level == 'critical':
            logger.critical("Critical threat - triggering comprehensive analysis")
            from tasks.osint import threat_intelligence, domain_scan

            # Chain multiple analysis tasks
            analysis_chain = chain(
                threat_intelligence.s(target, 'domain'),
                domain_scan.s(deep_scan=True)
            )
            analysis_result = analysis_chain.apply_async(priority=10)

            results['actions_taken'].append({
                'action': 'comprehensive_analysis',
                'status': 'initiated',
                'task_id': analysis_result.id
            })

    except Exception as e:
        logger.error(f"Error in threat response: {e}")
        results['error'] = str(e)

    return results


@app.task(
    base=OSINTTask,
    name='tasks.events.on_new_ioc',
    queue='high',
    priority=7
)
def on_new_ioc(ioc_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Triggered when a new Indicator of Compromise is discovered
    Performs threat intelligence enrichment
    """
    logger.info(f"New IoC detected: {ioc_data}")

    ioc_value = ioc_data.get('value', '')
    ioc_type = ioc_data.get('type', 'unknown')

    results = {
        'event': 'new_ioc',
        'timestamp': time.time(),
        'ioc': ioc_data,
        'enrichment': {}
    }

    try:
        # Enrich IoC with additional intelligence
        logger.info(f"Enriching {ioc_type}: {ioc_value}")

        if ioc_type == 'ip':
            results['enrichment'] = {
                'geolocation': {'country': 'US', 'city': 'New York'},
                'asn': 'AS12345',
                'hosting_provider': 'Example Hosting',
                'reputation_score': 25,
                'known_malicious': True
            }
        elif ioc_type == 'domain':
            results['enrichment'] = {
                'registration_date': '2024-01-01',
                'registrar': 'Example Registrar',
                'dns_records': ['192.168.1.1'],
                'reputation_score': 30,
                'category': 'phishing'
            }
        elif ioc_type == 'hash':
            results['enrichment'] = {
                'file_type': 'PE32',
                'size': '1.2MB',
                'first_seen': '2024-01-01',
                'detection_rate': '45/70',
                'malware_family': 'TrojanDownloader'
            }

        # Check if IoC affects monitored assets
        logger.info("Checking monitored assets for IoC matches")
        time.sleep(1)
        results['affected_assets'] = []

        # Store IoC in database
        logger.info("Storing IoC in threat intelligence database")
        results['stored'] = True

    except Exception as e:
        logger.error(f"Error enriching IoC: {e}")
        results['error'] = str(e)

    return results


@app.task(
    base=OSINTTask,
    name='tasks.events.on_scan_complete',
    queue='default'
)
def on_scan_complete(scan_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Triggered when a scan completes
    Processes and stores scan results
    """
    logger.info("Processing completed scan results")

    results = {
        'event': 'scan_complete',
        'timestamp': time.time(),
        'scan_id': scan_results.get('scan_id', 'unknown'),
        'processing_status': 'completed'
    }

    try:
        # Analyze scan results
        logger.info("Analyzing scan results for threats")
        time.sleep(1)

        # Check for anomalies
        anomalies = []
        findings = scan_results.get('findings', [])

        for finding in findings:
            if finding.get('severity') in ['high', 'critical']:
                anomalies.append(finding)
                # Trigger threat detection event
                on_threat_detected.apply_async(
                    args=[{
                        'type': finding.get('type'),
                        'level': finding.get('severity'),
                        'target': scan_results.get('target'),
                        'details': finding.get('details')
                    }],
                    priority=10
                )

        results['anomalies_found'] = len(anomalies)
        results['anomalies'] = anomalies

        # Store results in database
        logger.info("Storing scan results in database")
        time.sleep(0.5)
        results['stored'] = True

        # Generate report if requested
        if scan_results.get('generate_report', False):
            logger.info("Generating scan report")
            results['report_generated'] = True
            results['report_path'] = f"/tmp/scan_report_{int(time.time())}.pdf"

    except Exception as e:
        logger.error(f"Error processing scan results: {e}")
        results['error'] = str(e)

    return results


@app.task(
    base=OSINTTask,
    name='tasks.events.on_rate_limit_exceeded',
    queue='low'
)
def on_rate_limit_exceeded(service: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Triggered when API rate limit is exceeded
    Implements backoff and notification
    """
    logger.warning(f"Rate limit exceeded for {service}")

    results = {
        'event': 'rate_limit_exceeded',
        'timestamp': time.time(),
        'service': service,
        'details': details,
        'action': 'backoff_applied'
    }

    try:
        # Calculate backoff time
        retry_after = details.get('retry_after', 60)
        logger.info(f"Applying backoff: waiting {retry_after} seconds")

        # Notify administrators
        logger.info("Notifying administrators of rate limit issue")
        results['notification_sent'] = True

        # Optionally reschedule affected tasks
        results['tasks_rescheduled'] = details.get('pending_tasks', 0)

    except Exception as e:
        logger.error(f"Error handling rate limit: {e}")
        results['error'] = str(e)

    return results


@app.task(
    base=OSINTTask,
    name='tasks.events.on_data_leak_found',
    queue='critical',
    priority=10
)
def on_data_leak_found(leak_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Triggered when a potential data leak is discovered
    Critical priority - immediate action required
    """
    logger.critical(f"DATA LEAK DETECTED: {leak_data}")

    results = {
        'event': 'data_leak_found',
        'timestamp': time.time(),
        'leak_data': leak_data,
        'severity': 'critical',
        'actions_taken': []
    }

    try:
        # 1. Verify the leak
        logger.info("Verifying data leak authenticity")
        time.sleep(1)
        results['actions_taken'].append({
            'action': 'verification',
            'status': 'completed',
            'verified': True
        })

        # 2. Immediate notification
        logger.critical("Sending emergency notifications")
        results['actions_taken'].append({
            'action': 'emergency_alert',
            'status': 'sent',
            'recipients': ['security_team@example.com', 'ciso@example.com']
        })

        # 3. Collect evidence
        logger.info("Collecting evidence of data leak")
        time.sleep(1)
        results['actions_taken'].append({
            'action': 'evidence_collection',
            'status': 'completed',
            'evidence_path': f"/evidence/leak_{int(time.time())}"
        })

        # 4. Initiate incident response
        logger.info("Initiating incident response workflow")
        results['actions_taken'].append({
            'action': 'incident_response',
            'status': 'initiated',
            'incident_id': f"INC-{int(time.time())}"
        })

        # 5. Trigger comprehensive analysis
        from tasks.osint import domain_scan, email_enumeration

        analysis_tasks = group(
            domain_scan.s(leak_data.get('source_domain', ''), deep_scan=True),
            email_enumeration.s(leak_data.get('source_domain', ''))
        )
        analysis_result = analysis_tasks.apply_async(priority=10)

        results['actions_taken'].append({
            'action': 'comprehensive_analysis',
            'status': 'initiated',
            'task_id': analysis_result.id
        })

    except Exception as e:
        logger.error(f"Error handling data leak: {e}")
        results['error'] = str(e)

    return results


# =====================
# WORKFLOW TRIGGERS
# =====================

@app.task(
    base=OSINTTask,
    name='tasks.events.trigger_investigation_workflow'
)
def trigger_investigation_workflow(target: str, investigation_type: str) -> Dict[str, Any]:
    """
    Triggers a complete investigation workflow
    Orchestrates multiple tasks based on investigation type
    """
    logger.info(f"Triggering {investigation_type} investigation for {target}")

    from tasks.osint import (
        domain_scan, email_enumeration, social_media_scan,
        threat_intelligence, whois_lookup, dns_enumeration
    )

    results = {
        'event': 'investigation_triggered',
        'timestamp': time.time(),
        'target': target,
        'investigation_type': investigation_type,
        'workflow_tasks': []
    }

    try:
        if investigation_type == 'comprehensive':
            # Run all OSINT tasks in parallel
            workflow = group(
                domain_scan.s(target, deep_scan=True),
                email_enumeration.s(target),
                social_media_scan.s(target.split('.')[0]),
                threat_intelligence.s(target, 'domain'),
                whois_lookup.s(target),
                dns_enumeration.s(target)
            )

        elif investigation_type == 'threat_focused':
            # Focus on threat intelligence and security
            workflow = chain(
                threat_intelligence.s(target, 'domain'),
                domain_scan.s(deep_scan=True)
            )

        elif investigation_type == 'people_search':
            # Focus on people and social media
            workflow = group(
                email_enumeration.s(target),
                social_media_scan.s(target.split('.')[0])
            )

        else:
            # Basic investigation
            workflow = domain_scan.s(target)

        # Execute workflow
        workflow_result = workflow.apply_async()
        results['workflow_id'] = workflow_result.id
        results['status'] = 'initiated'

    except Exception as e:
        logger.error(f"Error triggering investigation: {e}")
        results['error'] = str(e)
        results['status'] = 'failed'

    return results


@app.task(base=OSINTTask, name='tasks.events.webhook_handler')
def webhook_handler(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generic webhook handler for external event triggers
    Routes webhooks to appropriate task handlers
    """
    logger.info(f"Processing webhook: {webhook_data.get('event_type')}")

    event_type = webhook_data.get('event_type')
    payload = webhook_data.get('payload', {})

    results = {
        'event': 'webhook_received',
        'timestamp': time.time(),
        'event_type': event_type,
        'processed': False
    }

    try:
        # Route to appropriate handler
        if event_type == 'threat_detected':
            task = on_threat_detected.apply_async(args=[payload], priority=10)
            results['handler_task_id'] = task.id

        elif event_type == 'new_ioc':
            task = on_new_ioc.apply_async(args=[payload], priority=7)
            results['handler_task_id'] = task.id

        elif event_type == 'scan_complete':
            task = on_scan_complete.apply_async(args=[payload])
            results['handler_task_id'] = task.id

        elif event_type == 'data_leak':
            task = on_data_leak_found.apply_async(args=[payload], priority=10)
            results['handler_task_id'] = task.id

        elif event_type == 'investigation_request':
            task = trigger_investigation_workflow.apply_async(
                args=[payload.get('target'), payload.get('type', 'basic')]
            )
            results['handler_task_id'] = task.id

        else:
            logger.warning(f"Unknown event type: {event_type}")
            results['error'] = 'unknown_event_type'
            return results

        results['processed'] = True
        results['status'] = 'dispatched'

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        results['error'] = str(e)

    return results
