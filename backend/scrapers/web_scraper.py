"""
Basic web scraper using BeautifulSoup and requests.
"""
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WebScraper:
    """Basic web scraper for HTML content extraction."""

    def __init__(self, user_agent: str = None):
        """
        Initialize web scraper.

        Args:
            user_agent: User agent string for requests
        """
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    async def scrape(
        self,
        url: str,
        selectors: Optional[Dict[str, str]] = None,
        extract_links: bool = True,
        extract_images: bool = True,
        extract_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Scrape a webpage and extract data.

        Args:
            url: URL to scrape
            selectors: CSS selectors for specific data extraction
            extract_links: Whether to extract all links
            extract_images: Whether to extract all images
            extract_metadata: Whether to extract metadata

        Returns:
            Dict containing scraped data
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            result = {
                "url": url,
                "status_code": response.status_code,
                "title": self._extract_title(soup),
                "content": {},
                "links": [],
                "images": [],
                "metadata": {},
                "scraped_at": datetime.utcnow().isoformat()
            }

            # Extract custom selectors
            if selectors:
                result["content"] = self._extract_selectors(soup, selectors)

            # Extract text content
            result["content"]["text"] = self._extract_text(soup)
            result["content"]["headings"] = self._extract_headings(soup)

            # Extract links
            if extract_links:
                result["links"] = self._extract_links(soup, url)

            # Extract images
            if extract_images:
                result["images"] = self._extract_images(soup, url)

            # Extract metadata
            if extract_metadata:
                result["metadata"] = self._extract_metadata(soup)

            return result

        except requests.RequestException as e:
            logger.error(f"Error scraping {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            raise

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title."""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else None

    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract main text content."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text(separator=' ', strip=True)
        return ' '.join(text.split())  # Clean up whitespace

    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all headings."""
        headings = []
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                headings.append({
                    "level": level,
                    "text": heading.get_text(strip=True)
                })
        return headings

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from the page."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            if absolute_url not in links:
                links.append(absolute_url)
        return links

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all images from the page."""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                absolute_url = urljoin(base_url, src)
                images.append({
                    "url": absolute_url,
                    "alt": img.get('alt', ''),
                    "title": img.get('title', '')
                })
        return images

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract page metadata."""
        metadata = {
            "description": None,
            "keywords": None,
            "author": None,
            "og_tags": {},
            "twitter_tags": {}
        }

        # Standard meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')

            if name == 'description':
                metadata["description"] = content
            elif name == 'keywords':
                metadata["keywords"] = content
            elif name == 'author':
                metadata["author"] = content

            # Open Graph tags
            property_attr = meta.get('property', '').lower()
            if property_attr.startswith('og:'):
                metadata["og_tags"][property_attr] = content

            # Twitter tags
            if property_attr.startswith('twitter:') or name.startswith('twitter:'):
                key = property_attr if property_attr.startswith('twitter:') else name
                metadata["twitter_tags"][key] = content

        return metadata

    def _extract_selectors(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using CSS selectors."""
        result = {}
        for key, selector in selectors.items():
            elements = soup.select(selector)
            if elements:
                if len(elements) == 1:
                    result[key] = elements[0].get_text(strip=True)
                else:
                    result[key] = [el.get_text(strip=True) for el in elements]
            else:
                result[key] = None
        return result
