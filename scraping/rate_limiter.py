"""Rate limiting for web scraping."""

import asyncio
from typing import Optional
from datetime import datetime, timedelta
from collections import deque
from loguru import logger


class RateLimiter:
    """
    Rate limiter for controlling request frequency.

    Features:
    - Per-minute rate limiting
    - Per-hour rate limiting
    - Token bucket algorithm
    - Async support
    """

    def __init__(
        self,
        calls_per_minute: int = 60,
        calls_per_hour: Optional[int] = None,
    ):
        """
        Initialize rate limiter.

        Args:
            calls_per_minute: Maximum calls per minute
            calls_per_hour: Maximum calls per hour (optional)
        """
        self.calls_per_minute = calls_per_minute
        self.calls_per_hour = calls_per_hour

        # Track recent requests
        self.minute_requests: deque = deque()
        self.hour_requests: deque = deque()

        self.lock = asyncio.Lock()

        logger.info(
            f"Rate limiter initialized: {calls_per_minute} calls/min, "
            f"{calls_per_hour or 'unlimited'} calls/hour"
        )

    async def acquire(self):
        """
        Acquire permission to make a request.

        Will wait if rate limit is exceeded.
        """
        async with self.lock:
            now = datetime.now()

            # Clean up old requests
            self._cleanup_old_requests(now)

            # Check per-minute limit
            if len(self.minute_requests) >= self.calls_per_minute:
                oldest_minute_request = self.minute_requests[0]
                wait_time = (oldest_minute_request + timedelta(minutes=1) - now).total_seconds()
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    now = datetime.now()
                    self._cleanup_old_requests(now)

            # Check per-hour limit
            if self.calls_per_hour and len(self.hour_requests) >= self.calls_per_hour:
                oldest_hour_request = self.hour_requests[0]
                wait_time = (oldest_hour_request + timedelta(hours=1) - now).total_seconds()
                if wait_time > 0:
                    logger.debug(f"Hourly rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    now = datetime.now()
                    self._cleanup_old_requests(now)

            # Record this request
            self.minute_requests.append(now)
            if self.calls_per_hour:
                self.hour_requests.append(now)

    def _cleanup_old_requests(self, now: datetime):
        """Remove requests older than the time windows."""
        # Remove requests older than 1 minute
        minute_threshold = now - timedelta(minutes=1)
        while self.minute_requests and self.minute_requests[0] < minute_threshold:
            self.minute_requests.popleft()

        # Remove requests older than 1 hour
        if self.calls_per_hour:
            hour_threshold = now - timedelta(hours=1)
            while self.hour_requests and self.hour_requests[0] < hour_threshold:
                self.hour_requests.popleft()

    async def reset(self):
        """Reset rate limiter."""
        async with self.lock:
            self.minute_requests.clear()
            self.hour_requests.clear()
            logger.info("Rate limiter reset")

    def get_current_rate(self) -> dict:
        """Get current rate statistics."""
        return {
            "requests_last_minute": len(self.minute_requests),
            "requests_last_hour": len(self.hour_requests) if self.calls_per_hour else None,
            "limit_per_minute": self.calls_per_minute,
            "limit_per_hour": self.calls_per_hour,
        }
