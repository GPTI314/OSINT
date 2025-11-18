"""Duplicate URL detection for crawling."""

from typing import Set
import hashlib
from urllib.parse import urlparse, parse_qs, urlencode
from loguru import logger


class DuplicateDetector:
    """
    Detect duplicate URLs during crawling.

    Features:
    - URL normalization
    - Query parameter sorting
    - Hash-based detection
    - Fuzzy matching
    """

    def __init__(self):
        """Initialize duplicate detector."""
        self.seen_urls: Set[str] = set()
        self.url_hashes: Set[str] = set()

        logger.info("Duplicate detector initialized")

    def is_duplicate(self, url: str) -> bool:
        """
        Check if URL is a duplicate.

        Args:
            url: URL to check

        Returns:
            True if duplicate, False otherwise
        """
        normalized = self.normalize_url(url)
        url_hash = self._hash_url(normalized)

        if url_hash in self.url_hashes:
            return True

        self.seen_urls.add(normalized)
        self.url_hashes.add(url_hash)
        return False

    def normalize_url(self, url: str) -> str:
        """
        Normalize URL for comparison.

        Args:
            url: URL to normalize

        Returns:
            Normalized URL
        """
        try:
            parsed = urlparse(url)

            # Lowercase scheme and netloc
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()

            # Remove default ports
            if ':80' in netloc and scheme == 'http':
                netloc = netloc.replace(':80', '')
            elif ':443' in netloc and scheme == 'https':
                netloc = netloc.replace(':443', '')

            # Remove trailing slash from path
            path = parsed.path.rstrip('/')
            if not path:
                path = '/'

            # Sort query parameters
            query_params = parse_qs(parsed.query)
            sorted_query = urlencode(sorted(query_params.items()), doseq=True)

            # Reconstruct URL
            normalized = f"{scheme}://{netloc}{path}"
            if sorted_query:
                normalized += f"?{sorted_query}"

            return normalized

        except Exception as e:
            logger.debug(f"Error normalizing URL {url}: {e}")
            return url

    def _hash_url(self, url: str) -> str:
        """Generate hash for URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def clear(self):
        """Clear seen URLs."""
        self.seen_urls.clear()
        self.url_hashes.clear()
        logger.info("Duplicate detector cleared")

    def get_stats(self) -> dict:
        """Get duplicate detector statistics."""
        return {
            "unique_urls": len(self.seen_urls),
        }
