"""
OSINT Toolkit - Main Application Entry Point
Demonstrates monitoring and logging integration.
"""

import os
import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import logging
from logging import configure_logging, get_logger
from logging.elk_handler import ELKHandler

# Import monitoring
from monitoring import setup_metrics, get_metrics_collector
from monitoring.health import HealthChecker
from monitoring.performance import monitor_performance, track_performance, get_performance_monitor

# Configure logging
configure_logging(
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
    log_dir=os.getenv('LOG_DIR', './logs'),
    enable_masking=True
)

logger = get_logger(__name__)

# Setup ELK handler
try:
    elk_handler = ELKHandler()
    elk_handler.add_to_logger(logger)
    logger.info("ELK handler configured successfully")
except Exception as e:
    logger.warning(f"Failed to configure ELK handler: {e}")

# Setup metrics
metrics = setup_metrics()
logger.info("Metrics collection started")

# Setup health checker
health_checker = HealthChecker()
logger.info("Health checker initialized")

# Create Flask app
app = Flask(__name__)


@app.before_request
def before_request():
    """Track request start time."""
    request.start_time = time.time()
    metrics.active_requests.inc()


@app.after_request
def after_request(response):
    """Log and track request metrics."""
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time

        # Record metrics
        metrics.record_request(
            method=request.method,
            endpoint=request.endpoint or 'unknown',
            status=response.status_code,
            duration=duration
        )

        metrics.active_requests.dec()

        # Log request
        logger.info(
            f"{request.method} {request.path} - {response.status_code}",
            extra={
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'duration': duration,
                'remote_addr': request.remote_addr
            }
        )

    return response


@app.errorhandler(Exception)
def handle_error(error):
    """Handle and log errors."""
    logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
    metrics.record_error(
        error_type=type(error).__name__,
        component='application'
    )
    return jsonify({'error': 'Internal server error'}), 500


@app.route('/')
def index():
    """Root endpoint."""
    return jsonify({
        'service': 'OSINT Toolkit',
        'version': '1.0.0',
        'status': 'running'
    })


@app.route('/health')
def health():
    """Health check endpoint."""
    health_status = health_checker.run_all_checks()
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code


@app.route('/metrics')
def metrics_endpoint():
    """Prometheus metrics endpoint."""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from flask import Response
    return Response(metrics.get_metrics(), mimetype=CONTENT_TYPE_LATEST)


@app.route('/performance')
def performance():
    """Performance statistics endpoint."""
    perf_monitor = get_performance_monitor()
    stats = perf_monitor.get_all_statistics()
    return jsonify(stats)


@app.route('/api/collect', methods=['POST'])
@monitor_performance('data_collection', include_system_stats=True)
def collect_data():
    """
    Example: Data collection endpoint.
    Demonstrates logging and metrics.
    """
    data = request.get_json()

    if not data:
        logger.warning("No data provided in collection request")
        return jsonify({'error': 'No data provided'}), 400

    source = data.get('source', 'unknown')
    data_type = data.get('type', 'unknown')

    logger.info(f"Collecting data from {source}", extra={
        'source': source,
        'type': data_type
    })

    # Simulate data collection
    with track_performance(f'collect_{source}'):
        time.sleep(0.1)  # Simulate work

    # Record metrics
    metrics.record_data_collection(source, data_type)

    logger.info(f"Data collected successfully from {source}")

    return jsonify({
        'status': 'success',
        'source': source,
        'type': data_type
    })


@app.route('/api/enrich', methods=['POST'])
@monitor_performance('enrichment', include_system_stats=True)
def enrich_data():
    """
    Example: Data enrichment endpoint.
    Demonstrates error tracking and metrics.
    """
    data = request.get_json()

    if not data:
        logger.warning("No data provided in enrichment request")
        return jsonify({'error': 'No data provided'}), 400

    operation = data.get('operation', 'unknown')

    logger.info(f"Enriching data with operation: {operation}")

    try:
        # Simulate enrichment
        with track_performance(f'enrich_{operation}'):
            time.sleep(0.05)

        metrics.record_enrichment(operation, 'success')
        logger.info(f"Enrichment completed: {operation}")

        return jsonify({
            'status': 'success',
            'operation': operation
        })

    except Exception as e:
        logger.error(f"Enrichment failed: {str(e)}", exc_info=True)
        metrics.record_enrichment(operation, 'failure')
        metrics.record_error(type(e).__name__, 'enrichment')
        raise


@app.route('/api/analyze', methods=['POST'])
@monitor_performance('analysis', include_system_stats=True)
def analyze_data():
    """
    Example: Data analysis endpoint.
    Demonstrates performance tracking.
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    analysis_type = data.get('type', 'general')

    logger.info(f"Starting analysis: {analysis_type}")

    # Track analysis duration
    start_time = time.time()

    # Simulate analysis
    time.sleep(0.2)

    duration = time.time() - start_time
    metrics.analysis_duration.labels(analysis_type=analysis_type).observe(duration)

    logger.info(f"Analysis completed: {analysis_type}", extra={
        'duration': duration,
        'type': analysis_type
    })

    return jsonify({
        'status': 'success',
        'type': analysis_type,
        'duration': duration
    })


def main():
    """Main application entry point."""
    logger.info("Starting OSINT Toolkit application")

    # Log sensitive data masking example
    logger.info("System initialized - contact: admin@example.com, API key: sk_test_1234567890abcdef")

    # Start Flask app
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))

    logger.info(f"Application starting on {host}:{port}")

    app.run(
        host=host,
        port=port,
        debug=False
    )


if __name__ == '__main__':
    main()
