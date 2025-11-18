"""
OSINT Toolkit - Logging Module
Provides structured logging with JSON format, log levels, and sensitive data masking.
"""

from .logger import get_logger, configure_logging
from .masking import DataMasker

__all__ = ['get_logger', 'configure_logging', 'DataMasker']
