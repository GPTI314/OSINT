"""
Rate limiting middleware using Redis
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable
import redis.asyncio as redis
from datetime import datetime, timedelta
from app.config import settings


class RateLimiter:
    """Redis-based rate limiter"""

    def __init__(self):
        self.redis_client = None

    async def init_redis(self):
        """Initialize Redis connection"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )

    async def check_rate_limit(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limit
        Returns: (is_allowed, info_dict)
        """
        if not self.redis_client:
            await self.init_redis()

        key = f"rate_limit:{identifier}:{window_seconds}"
        current_time = datetime.utcnow()

        # Get current count
        count = await self.redis_client.get(key)

        if count is None:
            # First request in window
            await self.redis_client.setex(key, window_seconds, 1)
            return True, {
                'limit': max_requests,
                'remaining': max_requests - 1,
                'reset': int((current_time + timedelta(seconds=window_seconds)).timestamp())
            }

        count = int(count)

        if count >= max_requests:
            # Rate limit exceeded
            ttl = await self.redis_client.ttl(key)
            return False, {
                'limit': max_requests,
                'remaining': 0,
                'reset': int((current_time + timedelta(seconds=ttl)).timestamp())
            }

        # Increment counter
        await self.redis_client.incr(key)

        return True, {
            'limit': max_requests,
            'remaining': max_requests - count - 1,
            'reset': int((current_time + timedelta(seconds=window_seconds)).timestamp())
        }

    async def check_multiple_limits(
        self,
        identifier: str,
        limits: list[tuple[int, int]]
    ) -> tuple[bool, dict]:
        """
        Check multiple rate limits (e.g., per minute, per hour, per day)
        limits: [(max_requests, window_seconds), ...]
        """
        for max_requests, window_seconds in limits:
            allowed, info = await self.check_rate_limit(identifier, max_requests, window_seconds)
            if not allowed:
                return False, info

        # Return info from the strictest limit (first one)
        _, info = await self.check_rate_limit(identifier, limits[0][0], limits[0][1])
        return True, info


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests"""

    def __init__(self, app: ASGIApp, limiter: RateLimiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next: Callable):
        """Check rate limits before processing request"""
        # Skip rate limiting for health checks
        if request.url.path in ['/health', '/']:
            return await call_next(request)

        # Get identifier (IP address or user ID)
        identifier = request.client.host if request.client else "unknown"

        # If authenticated, use user ID
        if hasattr(request.state, "user"):
            identifier = f"user:{request.state.user.id}"

        # Check rate limits (per minute, per hour, per day)
        limits = [
            (settings.RATE_LIMIT_PER_MINUTE, 60),
            (settings.RATE_LIMIT_PER_HOUR, 3600),
            (settings.RATE_LIMIT_PER_DAY, 86400),
        ]

        allowed, info = await self.limiter.check_multiple_limits(identifier, limits)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    'X-RateLimit-Limit': str(info['limit']),
                    'X-RateLimit-Remaining': str(info['remaining']),
                    'X-RateLimit-Reset': str(info['reset']),
                    'Retry-After': str(info['reset'] - int(datetime.utcnow().timestamp()))
                }
            )

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers['X-RateLimit-Limit'] = str(info['limit'])
        response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
        response.headers['X-RateLimit-Reset'] = str(info['reset'])

        return response


# Global rate limiter instance
rate_limiter = RateLimiter()
