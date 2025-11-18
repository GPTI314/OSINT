"""
Health check system for monitoring application health.
"""

import os
import time
import psutil
from typing import Dict, List, Callable, Optional
from datetime import datetime
from enum import Enum


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """Individual health check."""

    def __init__(self, name: str, check_fn: Callable, critical: bool = False):
        """
        Initialize health check.

        Args:
            name: Check name
            check_fn: Function that returns (status, message)
            critical: Whether this check is critical
        """
        self.name = name
        self.check_fn = check_fn
        self.critical = critical
        self.last_status = HealthStatus.HEALTHY
        self.last_message = ""
        self.last_check_time: Optional[float] = None

    def execute(self) -> Dict:
        """
        Execute health check.

        Returns:
            Check result dictionary
        """
        try:
            start_time = time.time()
            status, message = self.check_fn()
            duration = time.time() - start_time

            self.last_status = status
            self.last_message = message
            self.last_check_time = time.time()

            return {
                'name': self.name,
                'status': status.value,
                'message': message,
                'critical': self.critical,
                'duration_ms': round(duration * 1000, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.last_status = HealthStatus.UNHEALTHY
            self.last_message = f"Check failed: {str(e)}"
            self.last_check_time = time.time()

            return {
                'name': self.name,
                'status': HealthStatus.UNHEALTHY.value,
                'message': self.last_message,
                'critical': self.critical,
                'timestamp': datetime.utcnow().isoformat()
            }


class HealthChecker:
    """System health checker."""

    def __init__(self):
        """Initialize health checker."""
        self.checks: Dict[str, HealthCheck] = {}
        self._register_default_checks()

    def _register_default_checks(self):
        """Register default system health checks."""

        # CPU check
        def check_cpu():
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                return HealthStatus.UNHEALTHY, f"CPU usage too high: {cpu_percent}%"
            elif cpu_percent > 75:
                return HealthStatus.DEGRADED, f"CPU usage elevated: {cpu_percent}%"
            return HealthStatus.HEALTHY, f"CPU usage normal: {cpu_percent}%"

        self.register_check('cpu', check_cpu, critical=True)

        # Memory check
        def check_memory():
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                return HealthStatus.UNHEALTHY, f"Memory usage too high: {memory.percent}%"
            elif memory.percent > 75:
                return HealthStatus.DEGRADED, f"Memory usage elevated: {memory.percent}%"
            return HealthStatus.HEALTHY, f"Memory usage normal: {memory.percent}%"

        self.register_check('memory', check_memory, critical=True)

        # Disk check
        def check_disk():
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                return HealthStatus.UNHEALTHY, f"Disk usage too high: {disk.percent}%"
            elif disk.percent > 80:
                return HealthStatus.DEGRADED, f"Disk usage elevated: {disk.percent}%"
            return HealthStatus.HEALTHY, f"Disk usage normal: {disk.percent}%"

        self.register_check('disk', check_disk, critical=True)

        # Process check
        def check_process():
            try:
                process = psutil.Process(os.getpid())
                num_threads = process.num_threads()
                if num_threads > 100:
                    return HealthStatus.DEGRADED, f"High thread count: {num_threads}"
                return HealthStatus.HEALTHY, f"Thread count normal: {num_threads}"
            except Exception as e:
                return HealthStatus.UNHEALTHY, f"Process check failed: {e}"

        self.register_check('process', check_process)

    def register_check(self, name: str, check_fn: Callable, critical: bool = False):
        """
        Register a health check.

        Args:
            name: Check name
            check_fn: Check function
            critical: Whether check is critical
        """
        self.checks[name] = HealthCheck(name, check_fn, critical)

    def remove_check(self, name: str):
        """
        Remove a health check.

        Args:
            name: Check name
        """
        if name in self.checks:
            del self.checks[name]

    def run_check(self, name: str) -> Optional[Dict]:
        """
        Run a specific health check.

        Args:
            name: Check name

        Returns:
            Check result or None if check doesn't exist
        """
        check = self.checks.get(name)
        if check:
            return check.execute()
        return None

    def run_all_checks(self) -> Dict:
        """
        Run all health checks.

        Returns:
            Health check results
        """
        results = []
        overall_status = HealthStatus.HEALTHY

        for check in self.checks.values():
            result = check.execute()
            results.append(result)

            # Determine overall status
            if result['status'] == HealthStatus.UNHEALTHY.value:
                if check.critical:
                    overall_status = HealthStatus.UNHEALTHY
                elif overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
            elif result['status'] == HealthStatus.DEGRADED.value:
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED

        return {
            'status': overall_status.value,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': results,
            'summary': {
                'total': len(results),
                'healthy': sum(1 for r in results if r['status'] == HealthStatus.HEALTHY.value),
                'degraded': sum(1 for r in results if r['status'] == HealthStatus.DEGRADED.value),
                'unhealthy': sum(1 for r in results if r['status'] == HealthStatus.UNHEALTHY.value)
            }
        }

    def is_healthy(self) -> bool:
        """
        Check if system is healthy.

        Returns:
            True if healthy
        """
        result = self.run_all_checks()
        return result['status'] == HealthStatus.HEALTHY.value

    def get_status(self) -> str:
        """
        Get overall health status.

        Returns:
            Status string
        """
        result = self.run_all_checks()
        return result['status']


# Example custom checks
def create_database_health_check(db_connection_fn: Callable) -> Callable:
    """
    Create a database health check.

    Args:
        db_connection_fn: Function to test database connection

    Returns:
        Health check function
    """
    def check_database():
        try:
            db_connection_fn()
            return HealthStatus.HEALTHY, "Database connection successful"
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Database connection failed: {str(e)}"

    return check_database


def create_api_health_check(api_url: str, timeout: int = 5) -> Callable:
    """
    Create an API health check.

    Args:
        api_url: API URL to check
        timeout: Request timeout

    Returns:
        Health check function
    """
    def check_api():
        try:
            import requests
            response = requests.get(api_url, timeout=timeout)
            if response.status_code == 200:
                return HealthStatus.HEALTHY, f"API responding: {response.status_code}"
            else:
                return HealthStatus.DEGRADED, f"API returned: {response.status_code}"
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"API check failed: {str(e)}"

    return check_api


def create_cache_health_check(cache_client) -> Callable:
    """
    Create a cache health check.

    Args:
        cache_client: Cache client (e.g., Redis)

    Returns:
        Health check function
    """
    def check_cache():
        try:
            cache_client.ping()
            return HealthStatus.HEALTHY, "Cache connection successful"
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Cache connection failed: {str(e)}"

    return check_cache
