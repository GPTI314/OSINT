"""HTTP session pooling for efficient connections."""

import asyncio
from typing import Optional
import httpx
from loguru import logger


class SessionPool:
    """
    HTTP session pool for managing persistent connections.

    Features:
    - Connection pooling
    - Automatic cleanup
    - Connection limits
    - Timeout management
    """

    def __init__(self, max_sessions: int = 10):
        """
        Initialize session pool.

        Args:
            max_sessions: Maximum number of concurrent sessions
        """
        self.max_sessions = max_sessions
        self.sessions = []
        self.semaphore = asyncio.Semaphore(max_sessions)
        self.lock = asyncio.Lock()

        logger.info(f"Session pool initialized with {max_sessions} max sessions")

    async def get_session(
        self,
        timeout: int = 30,
        follow_redirects: bool = True,
        **kwargs
    ) -> httpx.AsyncClient:
        """
        Get an HTTP session from the pool.

        Args:
            timeout: Request timeout in seconds
            follow_redirects: Whether to follow redirects
            **kwargs: Additional httpx.AsyncClient arguments

        Returns:
            httpx.AsyncClient instance
        """
        await self.semaphore.acquire()

        try:
            async with self.lock:
                # Reuse existing session if available
                if self.sessions:
                    session = self.sessions.pop()
                    return session

            # Create new session
            limits = httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
            )

            session = httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=follow_redirects,
                limits=limits,
                **kwargs
            )

            return session

        except Exception as e:
            self.semaphore.release()
            logger.error(f"Error getting session: {e}")
            raise

    async def release_session(self, session: httpx.AsyncClient):
        """
        Release a session back to the pool.

        Args:
            session: Session to release
        """
        try:
            async with self.lock:
                if len(self.sessions) < self.max_sessions:
                    self.sessions.append(session)
                else:
                    await session.aclose()
        finally:
            self.semaphore.release()

    async def close(self):
        """Close all sessions in the pool."""
        async with self.lock:
            for session in self.sessions:
                try:
                    await session.aclose()
                except Exception as e:
                    logger.error(f"Error closing session: {e}")
            self.sessions.clear()

        logger.info("Session pool closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
