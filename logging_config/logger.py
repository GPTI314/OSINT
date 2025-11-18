"""Structured logging configuration."""

import sys
from pathlib import Path
from loguru import logger
from config.settings import settings


def setup_logging():
    """
    Setup application logging with loguru.

    Features:
    - JSON formatting
    - File rotation
    - Console output
    - Log levels
    - Structured logging
    """
    # Remove default logger
    logger.remove()

    # Console logging
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=settings.log_level,
        colorize=True,
    )

    # File logging
    if settings.log_file_enabled:
        log_path = Path(settings.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        if settings.log_format == "json":
            logger.add(
                settings.log_file_path,
                format="{message}",
                level=settings.log_level,
                rotation=settings.log_file_max_size,
                retention=settings.log_file_backup_count,
                compression="zip",
                serialize=True,  # JSON format
            )
        else:
            logger.add(
                settings.log_file_path,
                format=(
                    "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                    "{name}:{function}:{line} | {message}"
                ),
                level=settings.log_level,
                rotation=settings.log_file_max_size,
                retention=settings.log_file_backup_count,
                compression="zip",
            )

    # ELK Stack integration
    if settings.elk_enabled:
        try:
            from logging_config.elk_integration import ELKHandler
            elk_handler = ELKHandler(
                host=settings.logstash_host,
                port=settings.logstash_port,
            )
            logger.add(elk_handler, level=settings.log_level)
        except Exception as e:
            logger.warning(f"Failed to setup ELK logging: {e}")

    logger.info("Logging configured successfully")


def get_logger(name: str):
    """
    Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logger.bind(name=name)
