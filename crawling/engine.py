"""Core crawling engine for web crawling."""

from typing import Dict, Any, Optional, Set, List
from datetime import datetime
import asyncio
from urllib.parse import urljoin, urlparse
from loguru import logger

from .queue_manager import QueueManager
from .robots_parser import RobotsParser
from .link_extractor import LinkExtractor
from .duplicate_detector import DuplicateDetector
from .politeness_manager import PolitenessManager
from scraping.static_scraper import StaticScraper


class CrawlingEngine:
    """
    Core web crawling engine.

    Features:
    - BFS/DFS crawling
    - Robots.txt compliance
    - Duplicate detection
    - Politeness delays
    - Link extraction
    - Resume capability
    - Depth limiting
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize crawling engine.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.max_depth = self.config.get("max_depth", 3)
        self.max_pages = self.config.get("max_pages", 1000)
        self.allowed_domains = self.config.get("allowed_domains", [])
        self.exclude_patterns = self.config.get("exclude_patterns", [])

        # Initialize components
        self.queue_manager = QueueManager()
        self.robots_parser = RobotsParser()
        self.link_extractor = LinkExtractor()
        self.duplicate_detector = DuplicateDetector()
        self.politeness_manager = PolitenessManager(
            delay=self.config.get("politeness_delay", 1.0)
        )

        # State tracking
        self.crawled_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.pages_crawled = 0
        self.is_running = False

        logger.info("Crawling engine initialized")

    async def crawl(
        self,
        start_url: str,
        callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        Start crawling from a seed URL.

        Args:
            start_url: Starting URL for crawl
            callback: Optional callback function for each page

        Returns:
            Crawl statistics and results
        """
        start_time = datetime.utcnow()
        self.is_running = True

        try:
            logger.info(f"Starting crawl from: {start_url}")

            # Parse start URL
            parsed = urlparse(start_url)
            base_domain = parsed.netloc

            # Add allowed domain if not specified
            if not self.allowed_domains:
                self.allowed_domains = [base_domain]

            # Load robots.txt
            await self.robots_parser.load_robots(f"{parsed.scheme}://{parsed.netloc}")

            # Add start URL to queue
            self.queue_manager.add_url(start_url, depth=0)

            # Crawl loop
            while self.is_running and not self.queue_manager.is_empty():
                if self.pages_crawled >= self.max_pages:
                    logger.info(f"Max pages reached: {self.max_pages}")
                    break

                # Get next URL
                url_info = self.queue_manager.get_next_url()
                if not url_info:
                    break

                url = url_info["url"]
                depth = url_info["depth"]

                # Skip if already crawled or is duplicate
                if url in self.crawled_urls or self.duplicate_detector.is_duplicate(url):
                    continue

                # Check depth limit
                if depth > self.max_depth:
                    continue

                # Check robots.txt
                if not self.robots_parser.can_fetch(url):
                    logger.debug(f"Blocked by robots.txt: {url}")
                    continue

                # Check domain restrictions
                if not self._is_allowed_domain(url):
                    continue

                # Apply politeness delay
                await self.politeness_manager.wait_if_needed(url)

                # Crawl page
                try:
                    page_data = await self._crawl_page(url)

                    if page_data.get("success"):
                        self.crawled_urls.add(url)
                        self.pages_crawled += 1

                        # Execute callback if provided
                        if callback:
                            await callback(url, page_data)

                        # Extract and queue new links
                        if depth < self.max_depth:
                            links = self.link_extractor.extract_links(
                                page_data.get("html", ""),
                                base_url=url
                            )

                            for link in links:
                                if link not in self.crawled_urls:
                                    self.queue_manager.add_url(link, depth=depth + 1)

                        logger.info(
                            f"Crawled [{self.pages_crawled}/{self.max_pages}]: {url} "
                            f"(depth: {depth})"
                        )
                    else:
                        self.failed_urls.add(url)
                        logger.warning(f"Failed to crawl: {url}")

                except Exception as e:
                    logger.error(f"Error crawling {url}: {e}")
                    self.failed_urls.add(url)

            # Crawl complete
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            results = {
                "success": True,
                "start_url": start_url,
                "pages_crawled": self.pages_crawled,
                "pages_failed": len(self.failed_urls),
                "duration_seconds": duration,
                "crawled_urls": list(self.crawled_urls),
                "failed_urls": list(self.failed_urls),
            }

            logger.info(
                f"Crawl completed: {self.pages_crawled} pages in {duration:.2f}s"
            )
            return results

        except Exception as e:
            logger.error(f"Crawl failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "pages_crawled": self.pages_crawled,
            }
        finally:
            self.is_running = False

    async def _crawl_page(self, url: str) -> Dict[str, Any]:
        """Crawl a single page."""
        scraper = StaticScraper()
        return await scraper.scrape(url, {"include_html": True})

    def _is_allowed_domain(self, url: str) -> bool:
        """Check if URL domain is allowed."""
        parsed = urlparse(url)
        domain = parsed.netloc

        if not self.allowed_domains:
            return True

        return any(
            domain == allowed or domain.endswith(f".{allowed}")
            for allowed in self.allowed_domains
        )

    def stop(self):
        """Stop the crawling process."""
        logger.info("Stopping crawl...")
        self.is_running = False

    def get_stats(self) -> Dict[str, Any]:
        """Get current crawling statistics."""
        return {
            "pages_crawled": self.pages_crawled,
            "pages_queued": self.queue_manager.size(),
            "pages_failed": len(self.failed_urls),
            "is_running": self.is_running,
        }
