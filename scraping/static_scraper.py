"""Static HTML scraper using requests/httpx."""

from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential


class StaticScraper:
    """
    Static HTML scraper for pages that don't require JavaScript execution.

    Features:
    - Async HTTP requests
    - Automatic retries
    - Proxy support
    - User-Agent rotation
    - Rate limiting
    """

    def __init__(
        self,
        session_pool=None,
        proxy_manager=None,
        user_agent_rotator=None,
        rate_limiter=None,
    ):
        """Initialize static scraper."""
        self.session_pool = session_pool
        self.proxy_manager = proxy_manager
        self.user_agent_rotator = user_agent_rotator
        self.rate_limiter = rate_limiter

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def scrape(
        self,
        url: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Scrape a static HTML page.

        Args:
            url: URL to scrape
            config: Additional configuration

        Returns:
            Dictionary containing scraped data
        """
        config = config or {}

        try:
            # Apply rate limiting
            if self.rate_limiter:
                await self.rate_limiter.acquire()

            # Prepare headers
            headers = config.get("headers", {})
            if self.user_agent_rotator:
                headers["User-Agent"] = self.user_agent_rotator.get_user_agent()

            # Prepare proxy
            proxy = None
            if self.proxy_manager:
                proxy = self.proxy_manager.get_proxy()

            # Make request
            timeout = config.get("timeout", 30)
            async with httpx.AsyncClient(
                proxies=proxy,
                timeout=timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                # Parse HTML
                soup = BeautifulSoup(response.text, "lxml")

                # Extract data based on selectors
                extracted_data = {}
                selectors = config.get("selectors", {})

                for field, selector in selectors.items():
                    if isinstance(selector, str):
                        elements = soup.select(selector)
                        extracted_data[field] = [elem.get_text(strip=True) for elem in elements]
                    elif isinstance(selector, dict):
                        selector_str = selector.get("selector")
                        attr = selector.get("attr")
                        multiple = selector.get("multiple", True)

                        elements = soup.select(selector_str)
                        if attr:
                            values = [elem.get(attr) for elem in elements if elem.get(attr)]
                        else:
                            values = [elem.get_text(strip=True) for elem in elements]

                        extracted_data[field] = values if multiple else (values[0] if values else None)

                return {
                    "success": True,
                    "data": extracted_data,
                    "html": response.text if config.get("include_html") else None,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                }

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error scraping {url}: {e}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                "success": False,
                "error": str(e),
            }
