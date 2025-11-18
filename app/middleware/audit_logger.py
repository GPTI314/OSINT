"""
Audit logging middleware for tracking all API requests
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable
import time
import json
from datetime import datetime
from app.database.models import AuditLog
from app.database.base import async_session
from pythonjsonlogger import jsonlogger
import logging
from pathlib import Path


class AuditLogger:
    """Handle audit logging to database and file"""

    def __init__(self):
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)

        # Configure JSON logger for audit logs
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)

        # JSON file handler
        handler = logging.FileHandler("logs/audit.log")
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(message)s %(user_id)s %(action)s %(status)s %(ip_address)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    async def log_request(
        self,
        user_id: int = None,
        action: str = "",
        resource_type: str = "",
        resource_id: str = "",
        status: str = "success",
        method: str = "",
        endpoint: str = "",
        ip_address: str = "",
        user_agent: str = "",
        request_data: dict = None,
        response_data: dict = None,
        error_message: str = None,
        duration_ms: int = 0,
        pii_accessed: bool = False,
        data_exported: bool = False
    ):
        """Log audit entry to database and file"""
        try:
            # Log to file (immediate)
            self.logger.info(
                "API Request",
                extra={
                    'timestamp': datetime.utcnow().isoformat(),
                    'user_id': user_id,
                    'action': action,
                    'status': status,
                    'ip_address': ip_address,
                    'method': method,
                    'endpoint': endpoint,
                    'duration_ms': duration_ms
                }
            )

            # Log to database (async)
            async with async_session() as db:
                audit_log = AuditLog(
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    status=status,
                    method=method,
                    endpoint=endpoint,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    request_data=self._sanitize_data(request_data),
                    response_data=self._sanitize_data(response_data),
                    error_message=error_message,
                    duration_ms=duration_ms,
                    pii_accessed=pii_accessed,
                    data_exported=data_exported
                )
                db.add(audit_log)
                await db.commit()

        except Exception as e:
            # Don't fail the request if logging fails
            logging.error(f"Audit logging failed: {str(e)}")

    def _sanitize_data(self, data: dict) -> dict:
        """Remove sensitive data from logs"""
        if not data:
            return None

        sanitized = data.copy()
        sensitive_fields = [
            'password', 'token', 'secret', 'api_key', 'access_token',
            'refresh_token', 'authorization', 'credit_card', 'ssn'
        ]

        for key in list(sanitized.keys()):
            if any(field in key.lower() for field in sensitive_fields):
                sanitized[key] = "***REDACTED***"

        return sanitized


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to audit all API requests"""

    def __init__(self, app: ASGIApp, logger: AuditLogger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log all requests"""
        start_time = time.time()

        # Extract request info
        method = request.method
        endpoint = str(request.url.path)
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")

        # Get user ID if authenticated
        user_id = None
        if hasattr(request.state, "user"):
            user_id = request.state.user.id

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Determine status
        status = "success" if response.status_code < 400 else "failure"

        # Determine action from endpoint
        action = f"{method} {endpoint}"

        # Check if PII was accessed (based on endpoint)
        pii_accessed = any(term in endpoint.lower() for term in ['user', 'profile', 'personal'])

        # Check if data was exported
        data_exported = 'export' in endpoint.lower() or 'download' in endpoint.lower()

        # Log the request
        await self.logger.log_request(
            user_id=user_id,
            action=action,
            status=status,
            method=method,
            endpoint=endpoint,
            ip_address=ip_address,
            user_agent=user_agent,
            duration_ms=duration_ms,
            pii_accessed=pii_accessed,
            data_exported=data_exported
        )

        return response


# Global audit logger instance
audit_logger = AuditLogger()
