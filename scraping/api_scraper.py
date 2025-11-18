"""API scraper for REST and GraphQL endpoints."""

from typing import Dict, Any, Optional
import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential


class APIScraper:
    """
    API scraper for REST and GraphQL endpoints.

    Features:
    - REST API support
    - GraphQL support
    - Authentication handling
    - Rate limiting
    - Pagination support
    """

    def __init__(self, session_pool=None, proxy_manager=None, rate_limiter=None):
        """Initialize API scraper."""
        self.session_pool = session_pool
        self.proxy_manager = proxy_manager
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
        Scrape an API endpoint.

        Args:
            url: API URL to scrape
            config: Additional configuration

        Returns:
            Dictionary containing API response data
        """
        config = config or {}

        try:
            # Apply rate limiting
            if self.rate_limiter:
                await self.rate_limiter.acquire()

            # Prepare request
            method = config.get("method", "GET").upper()
            headers = config.get("headers", {})
            params = config.get("params", {})
            data = config.get("data")
            json_data = config.get("json")
            auth = config.get("auth")

            # Add authentication
            if auth:
                if auth.get("type") == "bearer":
                    headers["Authorization"] = f"Bearer {auth.get('token')}"
                elif auth.get("type") == "basic":
                    auth = (auth.get("username"), auth.get("password"))
                elif auth.get("type") == "api_key":
                    key_name = auth.get("key_name", "X-API-Key")
                    headers[key_name] = auth.get("key")

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
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    data=data,
                    json=json_data,
                    auth=auth if isinstance(auth, tuple) else None,
                )
                response.raise_for_status()

                # Parse response
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    data = response.json()
                else:
                    data = response.text

                return {
                    "success": True,
                    "data": data,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                }

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error scraping API {url}: {e}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {str(e)}",
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Error scraping API {url}: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def scrape_paginated(
        self,
        url: str,
        config: Optional[Dict[str, Any]] = None,
        max_pages: int = 10,
    ) -> Dict[str, Any]:
        """
        Scrape paginated API endpoint.

        Args:
            url: API URL to scrape
            config: Additional configuration
            max_pages: Maximum number of pages to scrape

        Returns:
            Dictionary containing all pages data
        """
        config = config or {}
        pagination = config.get("pagination", {})
        pagination_type = pagination.get("type", "offset")

        all_data = []
        page = 1

        while page <= max_pages:
            # Update pagination parameters
            if pagination_type == "offset":
                limit = pagination.get("limit", 100)
                offset = (page - 1) * limit
                config.setdefault("params", {})["offset"] = offset
                config["params"]["limit"] = limit
            elif pagination_type == "page":
                config.setdefault("params", {})["page"] = page
                config["params"]["per_page"] = pagination.get("per_page", 100)
            elif pagination_type == "cursor":
                if page > 1 and "next_cursor" in locals():
                    config.setdefault("params", {})["cursor"] = next_cursor
                else:
                    page += 1
                    continue

            # Scrape page
            result = await self.scrape(url, config)

            if not result.get("success"):
                break

            page_data = result.get("data", [])

            # Extract data from response
            data_key = pagination.get("data_key", "data")
            if isinstance(page_data, dict) and data_key in page_data:
                page_data = page_data[data_key]

            if not page_data:
                break

            all_data.extend(page_data if isinstance(page_data, list) else [page_data])

            # Check for next page
            if pagination_type == "cursor":
                cursor_key = pagination.get("cursor_key", "next_cursor")
                if isinstance(result.get("data"), dict):
                    next_cursor = result["data"].get(cursor_key)
                    if not next_cursor:
                        break

            page += 1

        return {
            "success": True,
            "data": all_data,
            "total_pages": page - 1,
        }
