"""
API Scraper
Handles REST and GraphQL API endpoints
"""

from typing import Optional, Dict, List, Any, Union
import json
import asyncio
from loguru import logger
import requests

try:
    from gql import gql, Client
    from gql.transport.requests import RequestsHTTPTransport
    from gql.transport.aiohttp import AIOHTTPTransport
    GQL_AVAILABLE = True
except ImportError:
    GQL_AVAILABLE = False
    logger.warning("gql library not installed")

from .base_scraper import BaseScraper, AsyncBaseScraper


class RESTScraper(BaseScraper):
    """
    Scraper for REST API endpoints
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        auth: Optional[tuple] = None,
        bearer_token: Optional[str] = None,
        api_key: Optional[str] = None,
        api_key_header: str = "X-API-Key",
        **kwargs
    ):
        """
        Initialize REST API scraper.

        Args:
            base_url: Base URL for API
            auth: Basic auth tuple (username, password)
            bearer_token: Bearer token for authorization
            api_key: API key for authorization
            api_key_header: Header name for API key
            **kwargs: Arguments for BaseScraper
        """
        super().__init__(**kwargs)
        self.base_url = base_url

        # Setup authentication
        if auth:
            self.session.auth = auth
            logger.info("Configured basic authentication")

        if bearer_token:
            self.session.headers['Authorization'] = f'Bearer {bearer_token}'
            logger.info("Configured bearer token authentication")

        if api_key:
            self.session.headers[api_key_header] = api_key
            logger.info(f"Configured API key authentication ({api_key_header})")

        logger.info(f"Initialized RESTScraper (base_url={base_url})")

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        if endpoint.startswith('http'):
            return endpoint
        if self.base_url:
            return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        return endpoint

    def scrape(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make API request.

        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters
            data: Form data
            json_data: JSON data
            **kwargs: Additional request arguments

        Returns:
            Response data as dictionary
        """
        url = self._build_url(endpoint)

        try:
            if method.upper() == "GET":
                response = self.get(url, params=params, **kwargs)
            elif method.upper() == "POST":
                response = self.post(url, params=params, data=data, json=json_data, **kwargs)
            elif method.upper() == "PUT":
                self._apply_rate_limit()
                response = self._retry_with_backoff(
                    lambda: self.session.put(url, params=params, data=data, json=json_data, timeout=self.timeout, **kwargs)
                )
            elif method.upper() == "DELETE":
                self._apply_rate_limit()
                response = self._retry_with_backoff(
                    lambda: self.session.delete(url, params=params, timeout=self.timeout, **kwargs)
                )
            elif method.upper() == "PATCH":
                self._apply_rate_limit()
                response = self._retry_with_backoff(
                    lambda: self.session.patch(url, params=params, data=data, json=json_data, timeout=self.timeout, **kwargs)
                )
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()

            # Try to parse as JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.warning(f"Response is not JSON, returning text")
                return {'text': response.text}

        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise

    def get_json(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict:
        """GET request returning JSON"""
        return self.scrape(endpoint, method="GET", params=params, **kwargs)

    def post_json(
        self,
        endpoint: str,
        json_data: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """POST request with JSON data"""
        return self.scrape(endpoint, method="POST", json_data=json_data, **kwargs)

    def put_json(
        self,
        endpoint: str,
        json_data: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """PUT request with JSON data"""
        return self.scrape(endpoint, method="PUT", json_data=json_data, **kwargs)

    def delete_json(self, endpoint: str, **kwargs) -> Dict:
        """DELETE request"""
        return self.scrape(endpoint, method="DELETE", **kwargs)

    def paginate(
        self,
        endpoint: str,
        page_param: str = "page",
        per_page_param: str = "per_page",
        per_page: int = 100,
        max_pages: Optional[int] = None,
        data_key: Optional[str] = None
    ) -> List[Dict]:
        """
        Paginate through API results.

        Args:
            endpoint: API endpoint
            page_param: Page parameter name
            per_page_param: Per-page parameter name
            per_page: Items per page
            max_pages: Maximum pages to fetch
            data_key: Key containing data in response (if nested)

        Returns:
            List of all results
        """
        all_results = []
        page = 1

        while True:
            if max_pages and page > max_pages:
                break

            params = {
                page_param: page,
                per_page_param: per_page
            }

            logger.info(f"Fetching page {page}")
            response = self.get_json(endpoint, params=params)

            # Extract data
            if data_key:
                data = response.get(data_key, [])
            else:
                data = response if isinstance(response, list) else []

            if not data:
                break

            all_results.extend(data)
            page += 1

            logger.debug(f"Fetched {len(data)} items (total: {len(all_results)})")

        logger.info(f"Pagination complete: {len(all_results)} total items")
        return all_results


class GraphQLScraper(BaseScraper):
    """
    Scraper for GraphQL API endpoints
    """

    def __init__(
        self,
        endpoint: str,
        bearer_token: Optional[str] = None,
        api_key: Optional[str] = None,
        api_key_header: str = "X-API-Key",
        **kwargs
    ):
        """
        Initialize GraphQL scraper.

        Args:
            endpoint: GraphQL endpoint URL
            bearer_token: Bearer token for authorization
            api_key: API key for authorization
            api_key_header: Header name for API key
            **kwargs: Arguments for BaseScraper
        """
        super().__init__(**kwargs)

        if not GQL_AVAILABLE:
            raise ImportError("gql library not installed. Install with: pip install gql")

        self.endpoint = endpoint

        # Setup headers
        headers = self.headers.copy()
        if bearer_token:
            headers['Authorization'] = f'Bearer {bearer_token}'
        if api_key:
            headers[api_key_header] = api_key

        # Create transport
        self.transport = RequestsHTTPTransport(
            url=endpoint,
            headers=headers,
            verify=self.verify_ssl,
            timeout=self.timeout
        )

        self.client = Client(
            transport=self.transport,
            fetch_schema_from_transport=True
        )

        logger.info(f"Initialized GraphQLScraper (endpoint={endpoint})")

    def scrape(
        self,
        query: str,
        variables: Optional[Dict] = None,
        operation_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute GraphQL query.

        Args:
            query: GraphQL query string
            variables: Query variables
            operation_name: Operation name

        Returns:
            Query result
        """
        try:
            self._apply_rate_limit()

            document = gql(query)
            result = self.client.execute(
                document,
                variable_values=variables,
                operation_name=operation_name
            )

            logger.info("GraphQL query executed successfully")
            return result

        except Exception as e:
            logger.error(f"GraphQL query failed: {e}")
            raise

    def query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute GraphQL query"""
        return self.scrape(query, variables=variables)

    def mutation(self, mutation: str, variables: Optional[Dict] = None) -> Dict:
        """Execute GraphQL mutation"""
        return self.scrape(mutation, variables=variables)


class AsyncRESTScraper(AsyncBaseScraper):
    """
    Async REST API scraper for concurrent requests
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        auth: Optional[tuple] = None,
        bearer_token: Optional[str] = None,
        api_key: Optional[str] = None,
        api_key_header: str = "X-API-Key",
        **kwargs
    ):
        """
        Initialize async REST scraper.

        Args:
            base_url: Base URL for API
            auth: Basic auth tuple
            bearer_token: Bearer token
            api_key: API key
            api_key_header: API key header name
            **kwargs: Arguments for AsyncBaseScraper
        """
        super().__init__(**kwargs)
        self.base_url = base_url

        if bearer_token:
            self.headers['Authorization'] = f'Bearer {bearer_token}'
        if api_key:
            self.headers[api_key_header] = api_key

        self.auth = auth

        logger.info(f"Initialized AsyncRESTScraper (base_url={base_url})")

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        if endpoint.startswith('http'):
            return endpoint
        if self.base_url:
            return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        return endpoint

    async def scrape_async(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Async API request.

        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters
            json_data: JSON data
            **kwargs: Additional arguments

        Returns:
            Response data
        """
        url = self._build_url(endpoint)

        try:
            if method.upper() == "GET":
                response = await self.get_async(url, params=params, **kwargs)
            elif method.upper() == "POST":
                response = await self.post_async(url, params=params, json=json_data, **kwargs)
            else:
                raise ValueError(f"Method {method} not supported in async mode")

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Async API request failed: {e}")
            raise

    async def scrape_multiple_async(
        self,
        endpoints: List[str],
        **kwargs
    ) -> List[Dict]:
        """
        Scrape multiple endpoints concurrently.

        Args:
            endpoints: List of endpoints
            **kwargs: Additional arguments

        Returns:
            List of responses
        """
        tasks = [self.scrape_async(endpoint, **kwargs) for endpoint in endpoints]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = []
        failed = 0
        for result in results:
            if isinstance(result, Exception):
                failed += 1
            else:
                successful.append(result)

        logger.info(f"Scraped {len(successful)}/{len(endpoints)} endpoints successfully")
        if failed:
            logger.warning(f"{failed} endpoints failed")

        return successful
