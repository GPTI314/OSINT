"""
HTML Scraper
Static HTML scraping using BeautifulSoup and lxml
"""

from typing import Optional, Dict, List, Any, Union
from bs4 import BeautifulSoup
from lxml import html, etree
import requests
from loguru import logger

from .base_scraper import BaseScraper, AsyncBaseScraper


class HTMLScraper(BaseScraper):
    """
    Scraper for static HTML pages using BeautifulSoup and lxml
    """

    def __init__(
        self,
        parser: str = "lxml",
        **kwargs
    ):
        """
        Initialize HTML scraper.

        Args:
            parser: HTML parser to use ('lxml', 'html.parser', 'html5lib')
            **kwargs: Arguments for BaseScraper
        """
        super().__init__(**kwargs)
        self.parser = parser
        logger.info(f"Initialized HTMLScraper with parser={parser}")

    def scrape(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        **kwargs
    ) -> BeautifulSoup:
        """
        Scrape HTML content from URL.

        Args:
            url: URL to scrape
            method: HTTP method ('GET' or 'POST')
            data: POST data if method is POST
            **kwargs: Additional arguments for request

        Returns:
            BeautifulSoup object
        """
        try:
            if method.upper() == "GET":
                response = self.get(url, **kwargs)
            elif method.upper() == "POST":
                response = self.post(url, data=data, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()

            soup = BeautifulSoup(response.content, self.parser)
            logger.info(f"Successfully scraped {url}")
            return soup

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            raise

    def scrape_text(self, url: str, **kwargs) -> str:
        """
        Scrape and return text content only.

        Args:
            url: URL to scrape
            **kwargs: Additional arguments for scrape

        Returns:
            Text content
        """
        soup = self.scrape(url, **kwargs)
        return soup.get_text(strip=True)

    def scrape_links(
        self,
        url: str,
        absolute: bool = True,
        **kwargs
    ) -> List[str]:
        """
        Extract all links from page.

        Args:
            url: URL to scrape
            absolute: Convert relative URLs to absolute
            **kwargs: Additional arguments for scrape

        Returns:
            List of URLs
        """
        soup = self.scrape(url, **kwargs)
        links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            if absolute:
                from urllib.parse import urljoin
                href = urljoin(url, href)
            links.append(href)

        logger.info(f"Found {len(links)} links on {url}")
        return links

    def scrape_images(
        self,
        url: str,
        absolute: bool = True,
        **kwargs
    ) -> List[Dict[str, str]]:
        """
        Extract all images from page.

        Args:
            url: URL to scrape
            absolute: Convert relative URLs to absolute
            **kwargs: Additional arguments for scrape

        Returns:
            List of image dictionaries with 'src', 'alt', etc.
        """
        soup = self.scrape(url, **kwargs)
        images = []

        for img in soup.find_all('img'):
            image_data = {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
            }

            if absolute and image_data['src']:
                from urllib.parse import urljoin
                image_data['src'] = urljoin(url, image_data['src'])

            images.append(image_data)

        logger.info(f"Found {len(images)} images on {url}")
        return images

    def scrape_tables(self, url: str, **kwargs) -> List[List[List[str]]]:
        """
        Extract all tables from page.

        Args:
            url: URL to scrape
            **kwargs: Additional arguments for scrape

        Returns:
            List of tables, each table is a list of rows, each row is a list of cells
        """
        soup = self.scrape(url, **kwargs)
        tables = []

        for table in soup.find_all('table'):
            table_data = []
            for row in table.find_all('tr'):
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    row_data.append(cell.get_text(strip=True))
                table_data.append(row_data)
            tables.append(table_data)

        logger.info(f"Found {len(tables)} tables on {url}")
        return tables

    def select(
        self,
        url: str,
        selector: str,
        **kwargs
    ) -> List[Any]:
        """
        Select elements using CSS selector.

        Args:
            url: URL to scrape
            selector: CSS selector
            **kwargs: Additional arguments for scrape

        Returns:
            List of matching elements
        """
        soup = self.scrape(url, **kwargs)
        elements = soup.select(selector)
        logger.debug(f"Found {len(elements)} elements matching '{selector}'")
        return elements

    def find(
        self,
        url: str,
        tag: str,
        attrs: Optional[Dict] = None,
        **kwargs
    ) -> Optional[Any]:
        """
        Find first element matching criteria.

        Args:
            url: URL to scrape
            tag: HTML tag name
            attrs: Tag attributes to match
            **kwargs: Additional arguments for scrape

        Returns:
            First matching element or None
        """
        soup = self.scrape(url, **kwargs)
        return soup.find(tag, attrs=attrs)

    def find_all(
        self,
        url: str,
        tag: str,
        attrs: Optional[Dict] = None,
        limit: Optional[int] = None,
        **kwargs
    ) -> List[Any]:
        """
        Find all elements matching criteria.

        Args:
            url: URL to scrape
            tag: HTML tag name
            attrs: Tag attributes to match
            limit: Maximum number of elements to return
            **kwargs: Additional arguments for scrape

        Returns:
            List of matching elements
        """
        soup = self.scrape(url, **kwargs)
        return soup.find_all(tag, attrs=attrs, limit=limit)


class LXMLScraper(BaseScraper):
    """
    Scraper using lxml for faster parsing and XPath support
    """

    def __init__(self, **kwargs):
        """
        Initialize LXML scraper.

        Args:
            **kwargs: Arguments for BaseScraper
        """
        super().__init__(**kwargs)
        logger.info("Initialized LXMLScraper")

    def scrape(self, url: str, **kwargs) -> html.HtmlElement:
        """
        Scrape HTML content using lxml.

        Args:
            url: URL to scrape
            **kwargs: Additional arguments for request

        Returns:
            lxml HtmlElement
        """
        try:
            response = self.get(url, **kwargs)
            response.raise_for_status()

            tree = html.fromstring(response.content)
            logger.info(f"Successfully scraped {url} with lxml")
            return tree

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            raise

    def scrape_text(self, url: str, **kwargs) -> str:
        """Get text content"""
        tree = self.scrape(url, **kwargs)
        return tree.text_content()

    def xpath(
        self,
        url: str,
        xpath: str,
        **kwargs
    ) -> List[Any]:
        """
        Select elements using XPath.

        Args:
            url: URL to scrape
            xpath: XPath expression
            **kwargs: Additional arguments for scrape

        Returns:
            List of matching elements or values
        """
        tree = self.scrape(url, **kwargs)
        results = tree.xpath(xpath)
        logger.debug(f"XPath '{xpath}' matched {len(results) if isinstance(results, list) else 1} items")
        return results

    def css_select(
        self,
        url: str,
        selector: str,
        **kwargs
    ) -> List[html.HtmlElement]:
        """
        Select elements using CSS selector.

        Args:
            url: URL to scrape
            selector: CSS selector
            **kwargs: Additional arguments for scrape

        Returns:
            List of matching elements
        """
        tree = self.scrape(url, **kwargs)
        results = tree.cssselect(selector)
        logger.debug(f"CSS selector '{selector}' matched {len(results)} elements")
        return results

    def scrape_links(
        self,
        url: str,
        absolute: bool = True,
        **kwargs
    ) -> List[str]:
        """Extract all links"""
        tree = self.scrape(url, **kwargs)
        links = tree.xpath('//a/@href')

        if absolute:
            from urllib.parse import urljoin
            links = [urljoin(url, link) for link in links]

        logger.info(f"Found {len(links)} links")
        return links

    def scrape_images(
        self,
        url: str,
        absolute: bool = True,
        **kwargs
    ) -> List[str]:
        """Extract all image URLs"""
        tree = self.scrape(url, **kwargs)
        images = tree.xpath('//img/@src')

        if absolute:
            from urllib.parse import urljoin
            images = [urljoin(url, img) for img in images]

        logger.info(f"Found {len(images)} images")
        return images


class AsyncHTMLScraper(AsyncBaseScraper):
    """
    Async HTML scraper for concurrent scraping
    """

    def __init__(self, parser: str = "lxml", **kwargs):
        """
        Initialize async HTML scraper.

        Args:
            parser: HTML parser to use
            **kwargs: Arguments for AsyncBaseScraper
        """
        super().__init__(**kwargs)
        self.parser = parser
        logger.info(f"Initialized AsyncHTMLScraper with parser={parser}")

    async def scrape_async(
        self,
        url: str,
        **kwargs
    ) -> BeautifulSoup:
        """
        Async scrape HTML content.

        Args:
            url: URL to scrape
            **kwargs: Additional arguments

        Returns:
            BeautifulSoup object
        """
        try:
            response = await self.get_async(url, **kwargs)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, self.parser)
            logger.info(f"Successfully scraped {url} (async)")
            return soup

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            raise

    async def scrape_multiple_async(
        self,
        urls: List[str],
        **kwargs
    ) -> List[BeautifulSoup]:
        """
        Scrape multiple URLs concurrently.

        Args:
            urls: List of URLs to scrape
            **kwargs: Additional arguments

        Returns:
            List of BeautifulSoup objects
        """
        import asyncio

        tasks = [self.scrape_async(url, **kwargs) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        successful = []
        failed = 0
        for result in results:
            if isinstance(result, Exception):
                failed += 1
            else:
                successful.append(result)

        logger.info(f"Scraped {len(successful)}/{len(urls)} URLs successfully (async)")
        if failed:
            logger.warning(f"{failed} URLs failed")

        return successful
