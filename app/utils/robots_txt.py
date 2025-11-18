"""
Robots.txt compliance checker for ethical web scraping
"""
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import aiohttp
from typing import Optional
import logging
from app.config import settings


class RobotsTxtChecker:
    """Check robots.txt compliance before scraping"""

    def __init__(self):
        self.parsers = {}  # Cache robot parsers by domain
        self.logger = logging.getLogger(__name__)

    async def can_fetch(self, url: str, user_agent: str = None) -> bool:
        """
        Check if URL can be fetched according to robots.txt
        """
        if not settings.RESPECT_ROBOTS_TXT:
            return True

        user_agent = user_agent or settings.USER_AGENT

        try:
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

            # Get or create parser for domain
            if domain not in self.parsers:
                await self._load_robots_txt(domain)

            parser = self.parsers.get(domain)
            if not parser:
                # If can't load robots.txt, allow by default
                return True

            # Check if can fetch
            return parser.can_fetch(user_agent, url)

        except Exception as e:
            self.logger.warning(f"Error checking robots.txt for {url}: {str(e)}")
            # On error, be conservative and allow
            return True

    async def _load_robots_txt(self, domain: str):
        """Load and parse robots.txt for a domain"""
        robots_url = f"{domain}/robots.txt"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url, timeout=5) as response:
                    if response.status == 200:
                        content = await response.text()

                        # Parse robots.txt
                        parser = RobotFileParser()
                        parser.parse(content.splitlines())
                        self.parsers[domain] = parser

                        self.logger.info(f"Loaded robots.txt for {domain}")
                    else:
                        # No robots.txt file, allow all
                        self.parsers[domain] = None

        except Exception as e:
            self.logger.warning(f"Failed to load robots.txt from {robots_url}: {str(e)}")
            self.parsers[domain] = None

    def get_crawl_delay(self, url: str, user_agent: str = None) -> float:
        """
        Get crawl delay from robots.txt or use default
        """
        user_agent = user_agent or settings.USER_AGENT

        try:
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

            parser = self.parsers.get(domain)
            if parser:
                delay = parser.crawl_delay(user_agent)
                if delay:
                    return float(delay)

        except Exception as e:
            self.logger.warning(f"Error getting crawl delay for {url}: {str(e)}")

        return settings.DEFAULT_CRAWL_DELAY

    async def check_and_delay(self, url: str, user_agent: str = None) -> tuple[bool, float]:
        """
        Check if can fetch and return recommended delay
        Returns: (can_fetch, delay_seconds)
        """
        can_fetch = await self.can_fetch(url, user_agent)
        delay = self.get_crawl_delay(url, user_agent)
        return can_fetch, delay


# Global robots.txt checker instance
robots_checker = RobotsTxtChecker()
