"""
Intelligent web crawler for mapping websites and discovering content.
"""
from typing import Dict, Any, List, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
from collections import deque
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WebCrawler:
    """Intelligent web crawler with configurable depth and domain filtering."""

    def __init__(
        self,
        max_depth: int = 2,
        max_pages: int = 100,
        respect_robots: bool = True,
        follow_external: bool = False,
        user_agent: str = None
    ):
        """
        Initialize web crawler.

        Args:
            max_depth: Maximum crawl depth
            max_pages: Maximum number of pages to crawl
            respect_robots: Whether to respect robots.txt
            follow_external: Whether to follow external links
            user_agent: User agent string
        """
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.respect_robots = respect_robots
        self.follow_external = follow_external
        self.user_agent = user_agent or "OSINT-Crawler/1.0"

        self.visited: Set[str] = set()
        self.queue: deque = deque()
        self.results: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, str]] = []

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    async def crawl(self, start_url: str, allowed_domains: List[str] = None) -> Dict[str, Any]:
        """
        Start crawling from the given URL.

        Args:
            start_url: Starting URL
            allowed_domains: List of allowed domains (None = same domain only)

        Returns:
            Dict containing crawl results
        """
        # Initialize
        start_domain = urlparse(start_url).netloc
        if allowed_domains is None:
            allowed_domains = [start_domain]

        # Add start URL to queue
        self.queue.append((start_url, 0))  # (url, depth)

        # Crawl
        while self.queue and len(self.visited) < self.max_pages:
            url, depth = self.queue.popleft()

            # Skip if already visited
            if url in self.visited:
                continue

            # Skip if max depth reached
            if depth > self.max_depth:
                continue

            # Mark as visited
            self.visited.add(url)

            # Crawl page
            try:
                page_data = await self._crawl_page(url, depth)
                self.results.append(page_data)

                # Extract and queue links if not at max depth
                if depth < self.max_depth:
                    links = page_data.get("links", [])
                    for link in links:
                        link_domain = urlparse(link).netloc

                        # Check if link is allowed
                        if self.follow_external or link_domain in allowed_domains:
                            if link not in self.visited:
                                self.queue.append((link, depth + 1))

            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                self.errors.append({
                    "url": url,
                    "error": str(e),
                    "depth": depth
                })

        return {
            "start_url": start_url,
            "pages_crawled": len(self.visited),
            "max_depth_reached": max(r.get("depth", 0) for r in self.results) if self.results else 0,
            "total_links_found": sum(len(r.get("links", [])) for r in self.results),
            "errors": len(self.errors),
            "results": self.results,
            "error_details": self.errors,
            "completed_at": datetime.utcnow().isoformat()
        }

    async def _crawl_page(self, url: str, depth: int) -> Dict[str, Any]:
        """
        Crawl a single page.

        Args:
            url: Page URL
            depth: Current depth

        Returns:
            Dict containing page data
        """
        response = self.session.get(url, timeout=30, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')

        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)

            # Only include HTTP(S) links
            if absolute_url.startswith(('http://', 'https://')):
                links.append(absolute_url)

        # Extract page info
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else None

        return {
            "url": url,
            "final_url": response.url,  # After redirects
            "status_code": response.status_code,
            "depth": depth,
            "title": title_text,
            "links": list(set(links)),  # Remove duplicates
            "link_count": len(set(links)),
            "content_length": len(response.content),
            "content_type": response.headers.get('Content-Type', ''),
            "crawled_at": datetime.utcnow().isoformat()
        }
