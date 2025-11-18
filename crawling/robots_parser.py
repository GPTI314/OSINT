"""Robots.txt parser for crawl compliance."""

from typing import Optional
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
import httpx
from loguru import logger


class RobotsParser:
    """
    Robots.txt parser for respecting crawl directives.

    Features:
    - Robots.txt parsing
    - User-agent specific rules
    - Crawl delay support
    - Sitemap discovery
    """

    def __init__(self, user_agent: str = "OSINT-Platform-Bot/1.0"):
        """
        Initialize robots parser.

        Args:
            user_agent: User agent string for robot rules
        """
        self.user_agent = user_agent
        self.parsers = {}
        self.crawl_delays = {}

        logger.info(f"Robots parser initialized (user-agent: {user_agent})")

    async def load_robots(self, base_url: str):
        """
        Load robots.txt for a domain.

        Args:
            base_url: Base URL of the domain
        """
        parsed = urlparse(base_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        if domain in self.parsers:
            return

        robots_url = urljoin(domain, "/robots.txt")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(robots_url, timeout=10)

                if response.status_code == 200:
                    parser = RobotFileParser()
                    parser.parse(response.text.splitlines())
                    self.parsers[domain] = parser

                    # Extract crawl delay
                    crawl_delay = self._extract_crawl_delay(response.text)
                    if crawl_delay:
                        self.crawl_delays[domain] = crawl_delay

                    logger.info(f"Loaded robots.txt for {domain}")
                else:
                    # Allow all if robots.txt not found
                    self.parsers[domain] = None
                    logger.debug(f"No robots.txt found for {domain}, allowing all")

        except Exception as e:
            logger.warning(f"Error loading robots.txt for {domain}: {e}")
            self.parsers[domain] = None

    def can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt.

        Args:
            url: URL to check

        Returns:
            True if allowed, False otherwise
        """
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        parser = self.parsers.get(domain)

        if parser is None:
            return True  # Allow if no robots.txt or error loading

        return parser.can_fetch(self.user_agent, url)

    def get_crawl_delay(self, url: str) -> Optional[float]:
        """
        Get crawl delay for a domain.

        Args:
            url: URL to get delay for

        Returns:
            Crawl delay in seconds or None
        """
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        return self.crawl_delays.get(domain)

    def _extract_crawl_delay(self, robots_txt: str) -> Optional[float]:
        """Extract crawl-delay directive from robots.txt."""
        try:
            for line in robots_txt.splitlines():
                line = line.strip().lower()
                if line.startswith("crawl-delay:"):
                    delay_str = line.split(":", 1)[1].strip()
                    return float(delay_str)
        except Exception as e:
            logger.debug(f"Error extracting crawl delay: {e}")

        return None
