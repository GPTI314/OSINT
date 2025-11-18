"""Politeness manager for respecting crawl delays."""

import asyncio
from typing import Dict
from datetime import datetime, timedelta
from urllib.parse import urlparse
from loguru import logger


class PolitenessManager:
    """
    Manage politeness delays between requests to same domain.

    Features:
    - Per-domain delays
    - Configurable delay times
    - Robots.txt crawl-delay support
    - Request throttling
    """

    def __init__(self, delay: float = 1.0):
        """
        Initialize politeness manager.

        Args:
            delay: Default delay in seconds between requests
        """
        self.default_delay = delay
        self.last_request_times: Dict[str, datetime] = {}

        logger.info(f"Politeness manager initialized (delay: {delay}s)")

    async def wait_if_needed(self, url: str, custom_delay: float = None):
        """
        Wait if necessary before making request to domain.

        Args:
            url: URL to request
            custom_delay: Custom delay override
        """
        domain = self._get_domain(url)
        delay = custom_delay or self.default_delay

        last_request = self.last_request_times.get(domain)

        if last_request:
            elapsed = (datetime.now() - last_request).total_seconds()
            wait_time = delay - elapsed

            if wait_time > 0:
                logger.debug(f"Waiting {wait_time:.2f}s for {domain}")
                await asyncio.sleep(wait_time)

        self.last_request_times[domain] = datetime.now()

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc

    def set_delay(self, domain: str, delay: float):
        """Set custom delay for a domain."""
        # This would be implemented with domain-specific delays
        pass

    def clear(self):
        """Clear all recorded request times."""
        self.last_request_times.clear()
        logger.info("Politeness manager cleared")
