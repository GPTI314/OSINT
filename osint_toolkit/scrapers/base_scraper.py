"""
Base Scraper Class
Provides common functionality for all scraper implementations including:
- Retry logic with exponential backoff
- Timeout management
- SSL certificate handling
- Header customization
- Cookie management
- Proxy support
- Rate limiting
- User-Agent rotation
"""

import time
import random
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
import ssl
import certifi
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.poolmanager import PoolManager
import httpx
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)


class SSLAdapter(HTTPAdapter):
    """Custom SSL adapter for handling self-signed certificates"""

    def __init__(self, ssl_verify: bool = True, *args, **kwargs):
        self.ssl_verify = ssl_verify
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        if not self.ssl_verify:
            kwargs['ssl_context'] = ssl._create_unverified_context()
        else:
            context = ssl.create_default_context(cafile=certifi.where())
            kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    Provides common functionality and enforces implementation of scrape method.
    """

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff_factor: float = 2.0,
        verify_ssl: bool = True,
        proxy: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        rate_limit_delay: float = 1.0,
        user_agent: Optional[str] = None
    ):
        """
        Initialize base scraper with common configuration.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff_factor: Multiplier for exponential backoff
            verify_ssl: Whether to verify SSL certificates
            proxy: Proxy server URL (e.g., 'http://proxy:port')
            headers: Custom HTTP headers
            cookies: Custom cookies
            rate_limit_delay: Delay between requests in seconds
            user_agent: Custom User-Agent string
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor
        self.verify_ssl = verify_ssl
        self.proxy = proxy
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.rate_limit_delay = rate_limit_delay
        self.user_agent = user_agent
        self.last_request_time: Optional[datetime] = None

        # Initialize session
        self.session = self._create_session()

        logger.info(f"Initialized {self.__class__.__name__} with timeout={timeout}s, max_retries={max_retries}")

    def _create_session(self) -> requests.Session:
        """Create a requests session with configured settings"""
        session = requests.Session()

        # Configure retries
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.retry_backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )

        # Mount adapter with SSL handling
        adapter = SSLAdapter(
            ssl_verify=self.verify_ssl,
            max_retries=retry_strategy
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set headers
        if self.user_agent:
            self.headers['User-Agent'] = self.user_agent
        session.headers.update(self.headers)

        # Set cookies
        if self.cookies:
            session.cookies.update(self.cookies)

        # Set proxy
        if self.proxy:
            session.proxies = {
                'http': self.proxy,
                'https': self.proxy
            }

        # SSL verification
        session.verify = self.verify_ssl

        return session

    def _apply_rate_limit(self):
        """Apply rate limiting between requests"""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
        self.last_request_time = datetime.now()

    def _retry_with_backoff(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic and exponential backoff.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Result of function execution
        """
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Max retries ({self.max_retries}) reached. Last error: {e}")
                    raise

                wait_time = self.retry_backoff_factor ** attempt
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)

    def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> requests.Response:
        """
        Perform GET request with rate limiting and retry logic.

        Args:
            url: URL to request
            params: Query parameters
            timeout: Override default timeout
            **kwargs: Additional arguments for requests.get

        Returns:
            Response object
        """
        self._apply_rate_limit()

        timeout = timeout or self.timeout

        def _make_request():
            logger.debug(f"GET {url}")
            return self.session.get(url, params=params, timeout=timeout, **kwargs)

        return self._retry_with_backoff(_make_request)

    def post(
        self,
        url: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> requests.Response:
        """
        Perform POST request with rate limiting and retry logic.

        Args:
            url: URL to request
            data: Form data
            json: JSON data
            timeout: Override default timeout
            **kwargs: Additional arguments for requests.post

        Returns:
            Response object
        """
        self._apply_rate_limit()

        timeout = timeout or self.timeout

        def _make_request():
            logger.debug(f"POST {url}")
            return self.session.post(url, data=data, json=json, timeout=timeout, **kwargs)

        return self._retry_with_backoff(_make_request)

    def update_headers(self, headers: Dict[str, str]):
        """Update session headers"""
        self.headers.update(headers)
        self.session.headers.update(headers)
        logger.debug(f"Updated headers: {headers}")

    def update_cookies(self, cookies: Dict[str, str]):
        """Update session cookies"""
        self.cookies.update(cookies)
        self.session.cookies.update(cookies)
        logger.debug(f"Updated cookies: {list(cookies.keys())}")

    def update_proxy(self, proxy: str):
        """Update proxy configuration"""
        self.proxy = proxy
        self.session.proxies = {
            'http': proxy,
            'https': proxy
        }
        logger.info(f"Updated proxy to: {proxy}")

    def clear_cookies(self):
        """Clear all cookies"""
        self.session.cookies.clear()
        self.cookies.clear()
        logger.debug("Cleared all cookies")

    def get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def close(self):
        """Close the session and cleanup resources"""
        self.session.close()
        logger.info(f"Closed {self.__class__.__name__} session")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    @abstractmethod
    def scrape(self, url: str, **kwargs) -> Any:
        """
        Abstract method to be implemented by subclasses.

        Args:
            url: URL to scrape
            **kwargs: Additional scraper-specific arguments

        Returns:
            Scraped data in appropriate format
        """
        pass


class AsyncBaseScraper(ABC):
    """
    Async version of base scraper for concurrent scraping operations.
    """

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff_factor: float = 2.0,
        verify_ssl: bool = True,
        proxy: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        rate_limit_delay: float = 1.0,
        user_agent: Optional[str] = None,
        max_concurrent: int = 10
    ):
        """
        Initialize async base scraper.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff_factor: Multiplier for exponential backoff
            verify_ssl: Whether to verify SSL certificates
            proxy: Proxy server URL
            headers: Custom HTTP headers
            cookies: Custom cookies
            rate_limit_delay: Delay between requests in seconds
            user_agent: Custom User-Agent string
            max_concurrent: Maximum concurrent requests
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor
        self.verify_ssl = verify_ssl
        self.proxy = proxy
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.rate_limit_delay = rate_limit_delay
        self.user_agent = user_agent
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

        if self.user_agent:
            self.headers['User-Agent'] = self.user_agent

        logger.info(f"Initialized {self.__class__.__name__} with max_concurrent={max_concurrent}")

    async def _get_client(self) -> httpx.AsyncClient:
        """Create async HTTP client"""
        return httpx.AsyncClient(
            timeout=self.timeout,
            verify=self.verify_ssl,
            proxies=self.proxy,
            headers=self.headers,
            cookies=self.cookies
        )

    async def _retry_with_backoff_async(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Async retry with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Max retries ({self.max_retries}) reached. Last error: {e}")
                    raise

                wait_time = self.retry_backoff_factor ** attempt
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

    async def get_async(
        self,
        url: str,
        params: Optional[Dict] = None,
        **kwargs
    ) -> httpx.Response:
        """Async GET request with rate limiting and retry logic"""
        async with self.semaphore:
            await asyncio.sleep(self.rate_limit_delay)

            async def _make_request():
                async with await self._get_client() as client:
                    logger.debug(f"Async GET {url}")
                    return await client.get(url, params=params, **kwargs)

            return await self._retry_with_backoff_async(_make_request)

    async def post_async(
        self,
        url: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        **kwargs
    ) -> httpx.Response:
        """Async POST request with rate limiting and retry logic"""
        async with self.semaphore:
            await asyncio.sleep(self.rate_limit_delay)

            async def _make_request():
                async with await self._get_client() as client:
                    logger.debug(f"Async POST {url}")
                    return await client.post(url, data=data, json=json, **kwargs)

            return await self._retry_with_backoff_async(_make_request)

    @abstractmethod
    async def scrape_async(self, url: str, **kwargs) -> Any:
        """
        Abstract async scrape method.

        Args:
            url: URL to scrape
            **kwargs: Additional scraper-specific arguments

        Returns:
            Scraped data
        """
        pass
