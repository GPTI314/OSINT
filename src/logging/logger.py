"""
Structured logging implementation with JSON format and multiple handlers.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
from pythonjsonlogger import jsonlogger
from datetime import datetime
import structlog

from .masking import DataMasker


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        # Add timestamp
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat()

        # Add log level
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

        # Add service information
        log_record['service'] = os.getenv('APP_NAME', 'osint-toolkit')
        log_record['environment'] = os.getenv('APP_ENV', 'development')


def configure_logging(
    log_level: str = "INFO",
    log_dir: str = "./logs",
    max_bytes: int = 100 * 1024 * 1024,  # 100MB
    backup_count: int = 10,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = True,
    enable_masking: bool = True
) -> None:
    """
    Configure logging with multiple handlers.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        enable_console: Enable console output
        enable_file: Enable file output
        enable_json: Enable JSON formatted logs
        enable_masking: Enable sensitive data masking
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Get log level
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if enable_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # JSON formatter
    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )

    # Standard formatter
    standard_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(json_formatter if enable_json else standard_formatter)
        root_logger.addHandler(console_handler)

    # File handler with rotation
    if enable_file:
        # JSON log file
        if enable_json:
            json_file_handler = logging.handlers.RotatingFileHandler(
                log_path / 'osint-toolkit.json.log',
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            json_file_handler.setLevel(level)
            json_file_handler.setFormatter(json_formatter)
            root_logger.addHandler(json_file_handler)

        # Standard text log file
        text_file_handler = logging.handlers.RotatingFileHandler(
            log_path / 'osint-toolkit.log',
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        text_file_handler.setLevel(level)
        text_file_handler.setFormatter(standard_formatter)
        root_logger.addHandler(text_file_handler)

        # Error log file
        error_file_handler = logging.handlers.RotatingFileHandler(
            log_path / 'osint-toolkit.error.log',
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(json_formatter if enable_json else standard_formatter)
        root_logger.addHandler(error_file_handler)

    # Add data masking filter if enabled
    if enable_masking:
        masking_filter = DataMaskingFilter()
        for handler in root_logger.handlers:
            handler.addFilter(masking_filter)


class DataMaskingFilter(logging.Filter):
    """Filter to mask sensitive data in log records."""

    def __init__(self):
        super().__init__()
        self.masker = DataMasker()

    def filter(self, record):
        """Mask sensitive data in the log message."""
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self.masker.mask_all(record.msg)

        # Mask args if present
        if hasattr(record, 'args') and record.args:
            masked_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    masked_args.append(self.masker.mask_all(arg))
                else:
                    masked_args.append(arg)
            record.args = tuple(masked_args)

        return True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name or 'osint-toolkit')


# Convenience functions for different log levels
def debug(message: str, **kwargs):
    """Log debug message."""
    get_logger().debug(message, extra=kwargs)


def info(message: str, **kwargs):
    """Log info message."""
    get_logger().info(message, extra=kwargs)


def warning(message: str, **kwargs):
    """Log warning message."""
    get_logger().warning(message, extra=kwargs)


def error(message: str, **kwargs):
    """Log error message."""
    get_logger().error(message, extra=kwargs)


def critical(message: str, **kwargs):
    """Log critical message."""
    get_logger().critical(message, extra=kwargs)
