"""Link extraction from HTML pages."""

from typing import List, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from loguru import logger


class LinkExtractor:
    """
    Extract links from HTML content.

    Features:
    - Absolute URL resolution
    - Link filtering
    - Duplicate removal
    - Multiple link types support
    """

    def __init__(self):
        """Initialize link extractor."""
        self.excluded_extensions = {
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg',
            '.zip', '.tar', '.gz', '.rar', '.7z',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv',
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
        }

    def extract_links(
        self,
        html: str,
        base_url: str,
        include_external: bool = False,
    ) -> List[str]:
        """
        Extract links from HTML content.

        Args:
            html: HTML content
            base_url: Base URL for resolving relative links
            include_external: Whether to include external links

        Returns:
            List of extracted URLs
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            links: Set[str] = set()

            # Extract from <a> tags
            for tag in soup.find_all('a', href=True):
                href = tag['href']
                absolute_url = self._make_absolute(href, base_url)
                if absolute_url:
                    links.add(absolute_url)

            # Extract from <link> tags
            for tag in soup.find_all('link', href=True):
                href = tag['href']
                absolute_url = self._make_absolute(href, base_url)
                if absolute_url:
                    links.add(absolute_url)

            # Extract from <img> tags (optional)
            # for tag in soup.find_all('img', src=True):
            #     src = tag['src']
            #     absolute_url = self._make_absolute(src, base_url)
            #     if absolute_url:
            #         links.add(absolute_url)

            # Filter links
            filtered_links = []
            base_domain = urlparse(base_url).netloc

            for link in links:
                if not self._is_valid_url(link):
                    continue

                if not include_external:
                    link_domain = urlparse(link).netloc
                    if link_domain != base_domain:
                        continue

                if self._has_excluded_extension(link):
                    continue

                filtered_links.append(link)

            logger.debug(f"Extracted {len(filtered_links)} links from {base_url}")
            return filtered_links

        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []

    def _make_absolute(self, url: str, base_url: str) -> str:
        """Convert relative URL to absolute."""
        try:
            # Skip anchors, javascript, mailto, etc.
            if url.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                return None

            absolute = urljoin(base_url, url)

            # Remove fragment
            if '#' in absolute:
                absolute = absolute.split('#')[0]

            return absolute

        except Exception:
            return None

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
        except Exception:
            return False

    def _has_excluded_extension(self, url: str) -> bool:
        """Check if URL has an excluded file extension."""
        parsed = urlparse(url)
        path = parsed.path.lower()

        return any(path.endswith(ext) for ext in self.excluded_extensions)
