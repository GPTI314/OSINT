"""
Rate Limiter
Implements various rate limiting strategies for respectful scraping
"""

import time
import asyncio
from typing import Optional, Dict
from datetime import datetime, timedelta
from collections import deque
from threading import Lock
from loguru import logger


class RateLimiter:
    """
    Token bucket rate limiter implementation.
    Allows burst requests up to a limit while maintaining average rate.
    """

    def __init__(
        self,
        requests_per_second: float = 1.0,
        burst_size: Optional[int] = None
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Average requests per second allowed
            burst_size: Maximum burst size (defaults to 2x requests_per_second)
        """
        self.rate = requests_per_second
        self.burst_size = burst_size or int(requests_per_second * 2)
        self.tokens = self.burst_size
        self.last_update = time.time()
        self.lock = Lock()

        logger.info(f"Initialized RateLimiter: {requests_per_second} req/s, burst={self.burst_size}")

    def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens, blocking if necessary.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            Time waited in seconds
        """
        with self.lock:
            wait_time = self._update_tokens()

            while self.tokens < tokens:
                time_to_wait = (tokens - self.tokens) / self.rate
                time.sleep(time_to_wait)
                wait_time += time_to_wait
                self._update_tokens()

            self.tokens -= tokens
            return wait_time

    def _update_tokens(self) -> float:
        """Update available tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now

        # Add tokens based on elapsed time
        self.tokens = min(
            self.burst_size,
            self.tokens + elapsed * self.rate
        )

        return 0.0

    def try_acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens without blocking.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if tokens were acquired, False otherwise
        """
        with self.lock:
            self._update_tokens()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def reset(self):
        """Reset the rate limiter"""
        with self.lock:
            self.tokens = self.burst_size
            self.last_update = time.time()
            logger.debug("Rate limiter reset")


class AsyncRateLimiter:
    """
    Async version of rate limiter for concurrent operations.
    """

    def __init__(
        self,
        requests_per_second: float = 1.0,
        burst_size: Optional[int] = None
    ):
        """
        Initialize async rate limiter.

        Args:
            requests_per_second: Average requests per second allowed
            burst_size: Maximum burst size
        """
        self.rate = requests_per_second
        self.burst_size = burst_size or int(requests_per_second * 2)
        self.tokens = self.burst_size
        self.last_update = time.time()
        self.lock = asyncio.Lock()

        logger.info(f"Initialized AsyncRateLimiter: {requests_per_second} req/s")

    async def acquire(self, tokens: int = 1) -> float:
        """
        Async acquire tokens.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            Time waited in seconds
        """
        async with self.lock:
            wait_time = self._update_tokens()

            while self.tokens < tokens:
                time_to_wait = (tokens - self.tokens) / self.rate
                await asyncio.sleep(time_to_wait)
                wait_time += time_to_wait
                self._update_tokens()

            self.tokens -= tokens
            return wait_time

    def _update_tokens(self) -> float:
        """Update available tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now

        self.tokens = min(
            self.burst_size,
            self.tokens + elapsed * self.rate
        )

        return 0.0


class DomainRateLimiter:
    """
    Rate limiter that tracks limits per domain.
    """

    def __init__(
        self,
        default_requests_per_second: float = 1.0,
        domain_limits: Optional[Dict[str, float]] = None
    ):
        """
        Initialize domain-based rate limiter.

        Args:
            default_requests_per_second: Default rate for domains
            domain_limits: Custom rate limits per domain
        """
        self.default_rate = default_requests_per_second
        self.domain_limits = domain_limits or {}
        self.limiters: Dict[str, RateLimiter] = {}
        self.lock = Lock()

        logger.info(f"Initialized DomainRateLimiter with default rate={default_requests_per_second} req/s")

    def _get_limiter(self, domain: str) -> RateLimiter:
        """Get or create rate limiter for domain"""
        if domain not in self.limiters:
            rate = self.domain_limits.get(domain, self.default_rate)
            self.limiters[domain] = RateLimiter(requests_per_second=rate)
            logger.debug(f"Created rate limiter for {domain}: {rate} req/s")
        return self.limiters[domain]

    def acquire(self, domain: str, tokens: int = 1) -> float:
        """
        Acquire tokens for specific domain.

        Args:
            domain: Domain to rate limit
            tokens: Number of tokens to acquire

        Returns:
            Time waited in seconds
        """
        with self.lock:
            limiter = self._get_limiter(domain)
        return limiter.acquire(tokens)

    def set_domain_limit(self, domain: str, requests_per_second: float):
        """Set custom rate limit for domain"""
        with self.lock:
            self.domain_limits[domain] = requests_per_second
            if domain in self.limiters:
                # Recreate limiter with new rate
                self.limiters[domain] = RateLimiter(requests_per_second=requests_per_second)
            logger.info(f"Set rate limit for {domain}: {requests_per_second} req/s")


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter that tracks exact request times.
    More accurate but uses more memory.
    """

    def __init__(
        self,
        max_requests: int,
        window_seconds: int
    ):
        """
        Initialize sliding window rate limiter.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: deque = deque()
        self.lock = Lock()

        logger.info(f"Initialized SlidingWindowRateLimiter: {max_requests} requests per {window_seconds}s")

    def acquire(self) -> float:
        """Acquire permission to make a request"""
        with self.lock:
            now = time.time()

            # Remove requests outside the window
            cutoff = now - self.window_seconds
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()

            # Check if we're at the limit
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest_request = self.requests[0]
                wait_time = (oldest_request + self.window_seconds) - now
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                    time.sleep(wait_time)
                    return wait_time

            # Record this request
            self.requests.append(time.time())
            return 0.0

    def get_current_rate(self) -> int:
        """Get current number of requests in window"""
        with self.lock:
            now = time.time()
            cutoff = now - self.window_seconds
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()
            return len(self.requests)

    def reset(self):
        """Reset the rate limiter"""
        with self.lock:
            self.requests.clear()
            logger.debug("Sliding window rate limiter reset")


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts based on response codes.
    Slows down on errors, speeds up on success.
    """

    def __init__(
        self,
        initial_rate: float = 1.0,
        min_rate: float = 0.1,
        max_rate: float = 10.0,
        backoff_factor: float = 0.5,
        speedup_factor: float = 1.2
    ):
        """
        Initialize adaptive rate limiter.

        Args:
            initial_rate: Starting requests per second
            min_rate: Minimum requests per second
            max_rate: Maximum requests per second
            backoff_factor: Factor to slow down on errors
            speedup_factor: Factor to speed up on success
        """
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.backoff_factor = backoff_factor
        self.speedup_factor = speedup_factor
        self.limiter = RateLimiter(requests_per_second=initial_rate)
        self.lock = Lock()
        self.consecutive_successes = 0

        logger.info(f"Initialized AdaptiveRateLimiter: initial={initial_rate} req/s")

    def acquire(self) -> float:
        """Acquire permission to make a request"""
        return self.limiter.acquire()

    def report_success(self):
        """Report successful request"""
        with self.lock:
            self.consecutive_successes += 1

            # Speed up after multiple successes
            if self.consecutive_successes >= 5:
                new_rate = min(self.current_rate * self.speedup_factor, self.max_rate)
                if new_rate != self.current_rate:
                    self.current_rate = new_rate
                    self.limiter = RateLimiter(requests_per_second=self.current_rate)
                    logger.info(f"Increased rate to {self.current_rate:.2f} req/s")
                self.consecutive_successes = 0

    def report_error(self, status_code: Optional[int] = None):
        """Report failed request"""
        with self.lock:
            self.consecutive_successes = 0

            # Slow down on errors
            new_rate = max(self.current_rate * self.backoff_factor, self.min_rate)
            if new_rate != self.current_rate:
                self.current_rate = new_rate
                self.limiter = RateLimiter(requests_per_second=self.current_rate)
                logger.warning(f"Decreased rate to {self.current_rate:.2f} req/s (status={status_code})")

    def get_current_rate(self) -> float:
        """Get current rate"""
        return self.current_rate
