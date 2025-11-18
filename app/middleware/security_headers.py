"""
Security headers middleware
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable
from app.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        """Add security headers"""
        response = await call_next(request)

        # HSTS (HTTP Strict Transport Security)
        if settings.ENABLE_HSTS:
            response.headers['Strict-Transport-Security'] = f'max-age={settings.HSTS_MAX_AGE}; includeSubDomains'

        # Content Security Policy
        if settings.ENABLE_CSP:
            response.headers['Content-Security-Policy'] = settings.CSP_POLICY

        # X-Content-Type-Options
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # X-Frame-Options
        response.headers['X-Frame-Options'] = 'DENY'

        # X-XSS-Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Referrer-Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions-Policy
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        # Remove server header
        response.headers.pop('Server', None)

        return response
