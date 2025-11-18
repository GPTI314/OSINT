"""
Performance monitoring utilities.
"""

import time
import functools
import psutil
import os
from typing import Callable, Dict, Optional, Any
from datetime import datetime
from contextlib import contextmanager
import threading


class PerformanceMonitor:
    """Monitor and track performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: Dict[str, list] = {}
        self.lock = threading.Lock()

    def record_execution_time(self, operation: str, duration: float, metadata: Dict = None):
        """
        Record execution time for an operation.

        Args:
            operation: Operation name
            duration: Duration in seconds
            metadata: Additional metadata
        """
        with self.lock:
            if operation not in self.metrics:
                self.metrics[operation] = []

            record = {
                'duration': duration,
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': metadata or {}
            }

            self.metrics[operation].append(record)

            # Keep only last 1000 records per operation
            if len(self.metrics[operation]) > 1000:
                self.metrics[operation] = self.metrics[operation][-1000:]

    def get_statistics(self, operation: str) -> Optional[Dict]:
        """
        Get statistics for an operation.

        Args:
            operation: Operation name

        Returns:
            Statistics dictionary or None
        """
        with self.lock:
            if operation not in self.metrics or not self.metrics[operation]:
                return None

            durations = [m['duration'] for m in self.metrics[operation]]

            return {
                'operation': operation,
                'count': len(durations),
                'min': min(durations),
                'max': max(durations),
                'avg': sum(durations) / len(durations),
                'total': sum(durations),
                'recent': durations[-10:] if len(durations) >= 10 else durations
            }

    def get_all_statistics(self) -> Dict[str, Dict]:
        """
        Get statistics for all operations.

        Returns:
            Dictionary of statistics
        """
        with self.lock:
            return {
                operation: self.get_statistics(operation)
                for operation in self.metrics.keys()
            }

    def clear_metrics(self, operation: Optional[str] = None):
        """
        Clear metrics.

        Args:
            operation: Specific operation to clear, or None for all
        """
        with self.lock:
            if operation:
                if operation in self.metrics:
                    self.metrics[operation] = []
            else:
                self.metrics = {}


# Global performance monitor
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """
    Get the global performance monitor.

    Returns:
        PerformanceMonitor instance
    """
    return _performance_monitor


def monitor_performance(operation: str = None, include_system_stats: bool = False):
    """
    Decorator to monitor function performance.

    Args:
        operation: Operation name (defaults to function name)
        include_system_stats: Include system resource stats

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation or func.__name__

            # Record initial system stats
            metadata = {}
            if include_system_stats:
                process = psutil.Process(os.getpid())
                metadata['cpu_percent_before'] = process.cpu_percent()
                metadata['memory_mb_before'] = process.memory_info().rss / 1024 / 1024

            # Execute function
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                metadata['status'] = 'success'
                return result
            except Exception as e:
                metadata['status'] = 'error'
                metadata['error'] = str(e)
                raise
            finally:
                duration = time.time() - start_time

                # Record final system stats
                if include_system_stats:
                    process = psutil.Process(os.getpid())
                    metadata['cpu_percent_after'] = process.cpu_percent()
                    metadata['memory_mb_after'] = process.memory_info().rss / 1024 / 1024

                # Record metrics
                _performance_monitor.record_execution_time(op_name, duration, metadata)

        return wrapper
    return decorator


@contextmanager
def track_performance(operation: str, metadata: Dict = None):
    """
    Context manager to track performance of a code block.

    Args:
        operation: Operation name
        metadata: Additional metadata

    Example:
        with track_performance('data_processing'):
            # code to measure
            pass
    """
    start_time = time.time()
    block_metadata = metadata or {}

    try:
        yield
        block_metadata['status'] = 'success'
    except Exception as e:
        block_metadata['status'] = 'error'
        block_metadata['error'] = str(e)
        raise
    finally:
        duration = time.time() - start_time
        _performance_monitor.record_execution_time(operation, duration, block_metadata)


class ResourceTracker:
    """Track system resource usage."""

    def __init__(self):
        """Initialize resource tracker."""
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()
        self.start_cpu_times = self.process.cpu_times()
        self.start_memory = self.process.memory_info()
        self.start_io = self.process.io_counters() if hasattr(self.process, 'io_counters') else None

    def get_snapshot(self) -> Dict[str, Any]:
        """
        Get current resource usage snapshot.

        Returns:
            Resource usage dictionary
        """
        current_time = time.time()
        cpu_times = self.process.cpu_times()
        memory = self.process.memory_info()

        snapshot = {
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': current_time - self.start_time,
            'cpu': {
                'percent': self.process.cpu_percent(interval=0.1),
                'user_time': cpu_times.user - self.start_cpu_times.user,
                'system_time': cpu_times.system - self.start_cpu_times.system,
            },
            'memory': {
                'rss_mb': memory.rss / 1024 / 1024,
                'vms_mb': memory.vms / 1024 / 1024,
                'percent': self.process.memory_percent(),
                'rss_delta_mb': (memory.rss - self.start_memory.rss) / 1024 / 1024,
            },
            'threads': self.process.num_threads(),
            'fds': self.process.num_fds() if hasattr(self.process, 'num_fds') else None,
        }

        # Add I/O stats if available
        if self.start_io:
            try:
                current_io = self.process.io_counters()
                snapshot['io'] = {
                    'read_mb': (current_io.read_bytes - self.start_io.read_bytes) / 1024 / 1024,
                    'write_mb': (current_io.write_bytes - self.start_io.write_bytes) / 1024 / 1024,
                    'read_count': current_io.read_count - self.start_io.read_count,
                    'write_count': current_io.write_count - self.start_io.write_count,
                }
            except Exception:
                pass

        return snapshot

    def get_system_snapshot(self) -> Dict[str, Any]:
        """
        Get system-wide resource usage.

        Returns:
            System resource dictionary
        """
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None,
            },
            'memory': {
                'total_mb': psutil.virtual_memory().total / 1024 / 1024,
                'available_mb': psutil.virtual_memory().available / 1024 / 1024,
                'percent': psutil.virtual_memory().percent,
            },
            'disk': {
                'total_gb': psutil.disk_usage('/').total / 1024 / 1024 / 1024,
                'used_gb': psutil.disk_usage('/').used / 1024 / 1024 / 1024,
                'free_gb': psutil.disk_usage('/').free / 1024 / 1024 / 1024,
                'percent': psutil.disk_usage('/').percent,
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv,
                'packets_sent': psutil.net_io_counters().packets_sent,
                'packets_recv': psutil.net_io_counters().packets_recv,
            }
        }
