"""Proxy rotation and management."""

from typing import Optional, List, Dict, Any
import random
from loguru import logger


class ProxyManager:
    """
    Proxy manager for rotating proxies.

    Features:
    - Multiple proxy support
    - Automatic rotation
    - Proxy health checking
    - Load from file or list
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize proxy manager.

        Args:
            config: Configuration dictionary
        """
        config = config or {}
        self.enabled = config.get("enabled", False)
        self.proxies: List[str] = []
        self.current_index = 0
        self.failed_proxies = set()

        # Load proxies
        proxy_list = config.get("proxy_list", [])
        if proxy_list:
            self.add_proxies(proxy_list)

        proxy_file = config.get("proxy_file")
        if proxy_file:
            self.load_proxies_from_file(proxy_file)

        logger.info(f"Proxy manager initialized with {len(self.proxies)} proxies")

    def add_proxies(self, proxies: List[str]):
        """Add proxies to the pool."""
        self.proxies.extend(proxies)

    def load_proxies_from_file(self, file_path: str):
        """Load proxies from a file."""
        try:
            with open(file_path, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
                self.add_proxies(proxies)
                logger.info(f"Loaded {len(proxies)} proxies from {file_path}")
        except Exception as e:
            logger.error(f"Error loading proxies from file: {e}")

    def get_proxy(self) -> Optional[str]:
        """Get next proxy from the pool."""
        if not self.enabled or not self.proxies:
            return None

        # Filter out failed proxies
        available_proxies = [
            p for p in self.proxies if p not in self.failed_proxies
        ]

        if not available_proxies:
            logger.warning("All proxies have failed, resetting failed list")
            self.failed_proxies.clear()
            available_proxies = self.proxies

        # Round-robin selection
        proxy = available_proxies[self.current_index % len(available_proxies)]
        self.current_index += 1

        return proxy

    def get_random_proxy(self) -> Optional[str]:
        """Get random proxy from the pool."""
        if not self.enabled or not self.proxies:
            return None

        available_proxies = [
            p for p in self.proxies if p not in self.failed_proxies
        ]

        if not available_proxies:
            self.failed_proxies.clear()
            available_proxies = self.proxies

        return random.choice(available_proxies)

    def mark_proxy_failed(self, proxy: str):
        """Mark a proxy as failed."""
        self.failed_proxies.add(proxy)
        logger.warning(f"Proxy marked as failed: {proxy}")

    def reset_failed_proxies(self):
        """Reset failed proxies list."""
        self.failed_proxies.clear()
        logger.info("Failed proxies list reset")

    def get_proxy_count(self) -> int:
        """Get total number of proxies."""
        return len(self.proxies)

    def get_available_proxy_count(self) -> int:
        """Get number of available (non-failed) proxies."""
        return len([p for p in self.proxies if p not in self.failed_proxies])
