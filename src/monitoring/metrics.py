"""
Prometheus metrics collection and exposition.
"""

import os
import time
from typing import Dict, Optional
from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    CollectorRegistry, generate_latest,
    start_http_server, CONTENT_TYPE_LATEST
)
from flask import Flask, Response
import psutil


class MetricsCollector:
    """Collects and exposes Prometheus metrics."""

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """
        Initialize metrics collector.

        Args:
            registry: Prometheus registry (uses default if None)
        """
        self.registry = registry or CollectorRegistry()

        # Application metrics
        self.request_count = Counter(
            'osint_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )

        self.request_duration = Histogram(
            'osint_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )

        self.active_requests = Gauge(
            'osint_active_requests',
            'Number of active requests',
            registry=self.registry
        )

        # OSINT specific metrics
        self.data_collected = Counter(
            'osint_data_collected_total',
            'Total data points collected',
            ['source', 'type'],
            registry=self.registry
        )

        self.enrichment_operations = Counter(
            'osint_enrichment_operations_total',
            'Total enrichment operations',
            ['operation', 'status'],
            registry=self.registry
        )

        self.analysis_duration = Histogram(
            'osint_analysis_duration_seconds',
            'Analysis operation duration',
            ['analysis_type'],
            registry=self.registry
        )

        self.cache_operations = Counter(
            'osint_cache_operations_total',
            'Cache operations',
            ['operation', 'result'],
            registry=self.registry
        )

        # System metrics
        self.cpu_usage = Gauge(
            'osint_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )

        self.memory_usage = Gauge(
            'osint_memory_usage_bytes',
            'Memory usage in bytes',
            registry=self.registry
        )

        self.disk_usage = Gauge(
            'osint_disk_usage_percent',
            'Disk usage percentage',
            registry=self.registry
        )

        self.network_bytes_sent = Counter(
            'osint_network_bytes_sent_total',
            'Total network bytes sent',
            registry=self.registry
        )

        self.network_bytes_recv = Counter(
            'osint_network_bytes_received_total',
            'Total network bytes received',
            registry=self.registry
        )

        # Error metrics
        self.errors = Counter(
            'osint_errors_total',
            'Total errors',
            ['error_type', 'component'],
            registry=self.registry
        )

        # Database metrics
        self.db_connections = Gauge(
            'osint_db_connections_active',
            'Active database connections',
            registry=self.registry
        )

        self.db_query_duration = Histogram(
            'osint_db_query_duration_seconds',
            'Database query duration',
            ['query_type'],
            registry=self.registry
        )

        # Queue metrics
        self.queue_size = Gauge(
            'osint_queue_size',
            'Queue size',
            ['queue_name'],
            registry=self.registry
        )

        self.queue_processing_duration = Histogram(
            'osint_queue_processing_duration_seconds',
            'Queue item processing duration',
            ['queue_name'],
            registry=self.registry
        )

        # Start system metrics collection
        self._last_network_counters = psutil.net_io_counters()
        self._start_system_metrics_collection()

    def _start_system_metrics_collection(self):
        """Start collecting system metrics periodically."""
        import threading

        def collect_system_metrics():
            while True:
                try:
                    # CPU usage
                    self.cpu_usage.set(psutil.cpu_percent(interval=1))

                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.memory_usage.set(memory.used)

                    # Disk usage
                    disk = psutil.disk_usage('/')
                    self.disk_usage.set(disk.percent)

                    # Network stats
                    net_io = psutil.net_io_counters()
                    if self._last_network_counters:
                        bytes_sent_diff = net_io.bytes_sent - self._last_network_counters.bytes_sent
                        bytes_recv_diff = net_io.bytes_recv - self._last_network_counters.bytes_recv

                        if bytes_sent_diff > 0:
                            self.network_bytes_sent.inc(bytes_sent_diff)
                        if bytes_recv_diff > 0:
                            self.network_bytes_recv.inc(bytes_recv_diff)

                    self._last_network_counters = net_io

                except Exception as e:
                    print(f"Error collecting system metrics: {e}")

                time.sleep(15)  # Collect every 15 seconds

        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """
        Record HTTP request metrics.

        Args:
            method: HTTP method
            endpoint: Request endpoint
            status: HTTP status code
            duration: Request duration in seconds
        """
        self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_data_collection(self, source: str, data_type: str, count: int = 1):
        """
        Record data collection metrics.

        Args:
            source: Data source
            data_type: Type of data
            count: Number of items collected
        """
        self.data_collected.labels(source=source, type=data_type).inc(count)

    def record_enrichment(self, operation: str, status: str):
        """
        Record enrichment operation.

        Args:
            operation: Operation name
            status: Operation status (success/failure)
        """
        self.enrichment_operations.labels(operation=operation, status=status).inc()

    def record_error(self, error_type: str, component: str):
        """
        Record error metric.

        Args:
            error_type: Type of error
            component: Component where error occurred
        """
        self.errors.labels(error_type=error_type, component=component).inc()

    def get_metrics(self) -> bytes:
        """
        Get metrics in Prometheus format.

        Returns:
            Metrics data
        """
        return generate_latest(self.registry)


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def setup_metrics(port: int = None) -> MetricsCollector:
    """
    Setup and start metrics collection.

    Args:
        port: Port to expose metrics on

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector

    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()

        # Start HTTP server for metrics
        if port is None:
            port = int(os.getenv('METRICS_PORT', 8000))

        try:
            start_http_server(port, registry=_metrics_collector.registry)
            print(f"Metrics server started on port {port}")
        except Exception as e:
            print(f"Failed to start metrics server: {e}")

    return _metrics_collector


def get_metrics_collector() -> Optional[MetricsCollector]:
    """
    Get the global metrics collector instance.

    Returns:
        MetricsCollector instance or None
    """
    return _metrics_collector


def create_metrics_app() -> Flask:
    """
    Create Flask app for metrics exposition.

    Returns:
        Flask app
    """
    app = Flask(__name__)
    metrics_collector = get_metrics_collector() or setup_metrics()

    @app.route('/metrics')
    def metrics():
        """Metrics endpoint."""
        return Response(
            metrics_collector.get_metrics(),
            mimetype=CONTENT_TYPE_LATEST
        )

    @app.route('/health')
    def health():
        """Health check endpoint."""
        return {'status': 'healthy', 'timestamp': time.time()}

    return app
