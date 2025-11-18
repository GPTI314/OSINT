"""Core scraping engine."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from loguru import logger

from .static_scraper import StaticScraper
from .dynamic_scraper import DynamicScraper
from .api_scraper import APIScraper
from .proxy_manager import ProxyManager
from .user_agent_rotator import UserAgentRotator
from .rate_limiter import RateLimiter
from .session_pool import SessionPool


class ScrapingEngine:
    """
    Core scraping engine that orchestrates different scraper types.

    Supports:
    - Static HTML scraping
    - Dynamic JavaScript scraping
    - API endpoint scraping
    - Proxy rotation
    - User-Agent rotation
    - Rate limiting
    - Session pooling
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize scraping engine.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

        # Initialize components
        self.proxy_manager = ProxyManager(self.config.get("proxy", {}))
        self.user_agent_rotator = UserAgentRotator()
        self.rate_limiter = RateLimiter(
            calls_per_minute=self.config.get("rate_limit_per_minute", 60)
        )
        self.session_pool = SessionPool(
            max_sessions=self.config.get("max_sessions", 10)
        )

        # Initialize scrapers
        self.static_scraper = StaticScraper(
            session_pool=self.session_pool,
            proxy_manager=self.proxy_manager,
            user_agent_rotator=self.user_agent_rotator,
            rate_limiter=self.rate_limiter,
        )

        self.dynamic_scraper = DynamicScraper(
            proxy_manager=self.proxy_manager,
            user_agent_rotator=self.user_agent_rotator,
        )

        self.api_scraper = APIScraper(
            session_pool=self.session_pool,
            proxy_manager=self.proxy_manager,
            rate_limiter=self.rate_limiter,
        )

        logger.info("Scraping engine initialized")

    async def scrape(
        self,
        url: str,
        scraper_type: str = "static",
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Scrape a URL using the specified scraper type.

        Args:
            url: URL to scrape
            scraper_type: Type of scraper to use (static, dynamic, api)
            config: Additional configuration for the scraper

        Returns:
            Scraping result containing data and metadata
        """
        start_time = datetime.utcnow()
        config = config or {}

        try:
            logger.info(f"Starting scrape: {url} (type: {scraper_type})")

            # Select and execute scraper
            if scraper_type == "static":
                result = await self.static_scraper.scrape(url, config)
            elif scraper_type == "dynamic":
                result = await self.dynamic_scraper.scrape(url, config)
            elif scraper_type == "api":
                result = await self.api_scraper.scrape(url, config)
            else:
                raise ValueError(f"Unknown scraper type: {scraper_type}")

            # Add metadata
            result["metadata"] = {
                "url": url,
                "scraper_type": scraper_type,
                "start_time": start_time.isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
            }

            logger.info(f"Scrape completed: {url}")
            return result

        except Exception as e:
            logger.error(f"Scrape failed: {url} - {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "url": url,
                    "scraper_type": scraper_type,
                    "start_time": start_time.isoformat(),
                    "end_time": datetime.utcnow().isoformat(),
                },
            }

    async def scrape_batch(
        self,
        urls: List[str],
        scraper_type: str = "static",
        config: Optional[Dict[str, Any]] = None,
        max_concurrent: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs concurrently.

        Args:
            urls: List of URLs to scrape
            scraper_type: Type of scraper to use
            config: Additional configuration
            max_concurrent: Maximum concurrent requests

        Returns:
            List of scraping results
        """
        logger.info(f"Starting batch scrape: {len(urls)} URLs")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def scrape_with_semaphore(url: str):
            async with semaphore:
                return await self.scrape(url, scraper_type, config)

        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "metadata": {"url": urls[i]},
                })
            else:
                processed_results.append(result)

        logger.info(f"Batch scrape completed: {len(urls)} URLs")
        return processed_results

    async def close(self):
        """Clean up resources."""
        logger.info("Closing scraping engine")
        await self.session_pool.close()
        await self.dynamic_scraper.close()
        logger.info("Scraping engine closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
