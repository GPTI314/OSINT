"""
Proxy Manager
Handles proxy rotation with support for multiple proxy providers
"""

import random
from typing import List, Optional, Dict
from dataclasses import dataclass
from enum import Enum
import requests
from loguru import logger


class ProxyProtocol(Enum):
    """Proxy protocol types"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


@dataclass
class Proxy:
    """Proxy configuration"""
    host: str
    port: int
    protocol: ProxyProtocol = ProxyProtocol.HTTP
    username: Optional[str] = None
    password: Optional[str] = None
    working: bool = True
    failures: int = 0

    def to_url(self) -> str:
        """Convert proxy to URL format"""
        if self.username and self.password:
            return f"{self.protocol.value}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol.value}://{self.host}:{self.port}"

    def to_dict(self) -> Dict[str, str]:
        """Convert proxy to dictionary format for requests library"""
        proxy_url = self.to_url()
        return {
            'http': proxy_url,
            'https': proxy_url
        }


class ProxyManager:
    """
    Manages proxy rotation and health checking
    """

    def __init__(
        self,
        proxies: Optional[List[Proxy]] = None,
        max_failures: int = 3,
        test_url: str = "http://httpbin.org/ip",
        test_timeout: int = 10
    ):
        """
        Initialize proxy manager.

        Args:
            proxies: List of proxy configurations
            max_failures: Maximum failures before marking proxy as bad
            test_url: URL to test proxy connectivity
            test_timeout: Timeout for proxy tests
        """
        self.proxies: List[Proxy] = proxies or []
        self.max_failures = max_failures
        self.test_url = test_url
        self.test_timeout = test_timeout
        self.current_index = 0

        logger.info(f"Initialized ProxyManager with {len(self.proxies)} proxies")

    def add_proxy(
        self,
        host: str,
        port: int,
        protocol: ProxyProtocol = ProxyProtocol.HTTP,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """Add a proxy to the pool"""
        proxy = Proxy(
            host=host,
            port=port,
            protocol=protocol,
            username=username,
            password=password
        )
        self.proxies.append(proxy)
        logger.info(f"Added proxy: {proxy.to_url()}")

    def add_proxies_from_list(self, proxy_list: List[str]):
        """
        Add proxies from a list of strings.
        Format: protocol://host:port or host:port (defaults to HTTP)

        Args:
            proxy_list: List of proxy strings
        """
        for proxy_str in proxy_list:
            try:
                # Parse proxy string
                if '://' in proxy_str:
                    protocol_str, rest = proxy_str.split('://', 1)
                    protocol = ProxyProtocol(protocol_str)
                else:
                    protocol = ProxyProtocol.HTTP
                    rest = proxy_str

                # Parse host:port
                if '@' in rest:
                    auth, host_port = rest.split('@', 1)
                    username, password = auth.split(':', 1)
                else:
                    host_port = rest
                    username, password = None, None

                host, port = host_port.split(':', 1)
                port = int(port)

                self.add_proxy(host, port, protocol, username, password)

            except Exception as e:
                logger.warning(f"Failed to parse proxy '{proxy_str}': {e}")

    def get_next_proxy(self) -> Optional[Proxy]:
        """Get next working proxy using round-robin"""
        if not self.proxies:
            return None

        working_proxies = [p for p in self.proxies if p.working]
        if not working_proxies:
            logger.warning("No working proxies available")
            return None

        self.current_index = (self.current_index + 1) % len(working_proxies)
        proxy = working_proxies[self.current_index]
        logger.debug(f"Selected proxy: {proxy.to_url()}")
        return proxy

    def get_random_proxy(self) -> Optional[Proxy]:
        """Get random working proxy"""
        working_proxies = [p for p in self.proxies if p.working]
        if not working_proxies:
            logger.warning("No working proxies available")
            return None

        proxy = random.choice(working_proxies)
        logger.debug(f"Selected random proxy: {proxy.to_url()}")
        return proxy

    def test_proxy(self, proxy: Proxy) -> bool:
        """
        Test if proxy is working.

        Args:
            proxy: Proxy to test

        Returns:
            True if proxy is working, False otherwise
        """
        try:
            response = requests.get(
                self.test_url,
                proxies=proxy.to_dict(),
                timeout=self.test_timeout
            )
            if response.status_code == 200:
                proxy.working = True
                proxy.failures = 0
                logger.info(f"Proxy {proxy.to_url()} is working")
                return True
        except Exception as e:
            logger.warning(f"Proxy {proxy.to_url()} failed test: {e}")

        proxy.failures += 1
        if proxy.failures >= self.max_failures:
            proxy.working = False
            logger.error(f"Proxy {proxy.to_url()} marked as not working after {proxy.failures} failures")

        return False

    def test_all_proxies(self):
        """Test all proxies in the pool"""
        logger.info(f"Testing {len(self.proxies)} proxies...")
        for proxy in self.proxies:
            self.test_proxy(proxy)

        working_count = sum(1 for p in self.proxies if p.working)
        logger.info(f"Proxy test complete: {working_count}/{len(self.proxies)} working")

    def mark_proxy_failed(self, proxy: Proxy):
        """Mark a proxy as failed"""
        proxy.failures += 1
        if proxy.failures >= self.max_failures:
            proxy.working = False
            logger.warning(f"Proxy {proxy.to_url()} marked as not working")

    def reset_proxies(self):
        """Reset all proxy failure counts"""
        for proxy in self.proxies:
            proxy.working = True
            proxy.failures = 0
        logger.info("Reset all proxy failure counts")

    def get_stats(self) -> Dict:
        """Get proxy pool statistics"""
        total = len(self.proxies)
        working = sum(1 for p in self.proxies if p.working)
        return {
            'total': total,
            'working': working,
            'failed': total - working,
            'proxies': [
                {
                    'url': p.to_url(),
                    'working': p.working,
                    'failures': p.failures
                }
                for p in self.proxies
            ]
        }

    def remove_failed_proxies(self):
        """Remove all failed proxies from the pool"""
        before = len(self.proxies)
        self.proxies = [p for p in self.proxies if p.working]
        removed = before - len(self.proxies)
        logger.info(f"Removed {removed} failed proxies")
