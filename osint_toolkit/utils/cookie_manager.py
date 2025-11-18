"""
Cookie Manager
Handles cookie persistence, loading from browsers, and management
"""

import json
import pickle
from typing import Optional, Dict, List
from pathlib import Path
from http.cookiejar import CookieJar
import requests
from loguru import logger

try:
    import browser_cookie3
    BROWSER_COOKIE_AVAILABLE = True
except ImportError:
    BROWSER_COOKIE_AVAILABLE = False
    logger.warning("browser-cookie3 not installed")


class CookieManager:
    """
    Manages cookies with persistence and browser import support
    """

    def __init__(
        self,
        cookie_file: Optional[str] = None,
        auto_save: bool = True
    ):
        """
        Initialize cookie manager.

        Args:
            cookie_file: Path to file for cookie persistence
            auto_save: Automatically save cookies on updates
        """
        self.cookie_file = cookie_file
        self.auto_save = auto_save
        self.cookies: Dict[str, Dict[str, str]] = {}  # domain -> {name: value}

        if cookie_file and Path(cookie_file).exists():
            self.load_from_file(cookie_file)

        logger.info(f"Initialized CookieManager (file={cookie_file}, auto_save={auto_save})")

    def add_cookie(
        self,
        domain: str,
        name: str,
        value: str,
        path: str = "/",
        **kwargs
    ):
        """
        Add a cookie.

        Args:
            domain: Cookie domain
            name: Cookie name
            value: Cookie value
            path: Cookie path
            **kwargs: Additional cookie attributes
        """
        if domain not in self.cookies:
            self.cookies[domain] = {}

        self.cookies[domain][name] = value
        logger.debug(f"Added cookie: {name} for {domain}")

        if self.auto_save and self.cookie_file:
            self.save_to_file(self.cookie_file)

    def add_cookies_dict(self, domain: str, cookies: Dict[str, str]):
        """
        Add multiple cookies for a domain.

        Args:
            domain: Cookie domain
            cookies: Dictionary of cookie name-value pairs
        """
        if domain not in self.cookies:
            self.cookies[domain] = {}

        self.cookies[domain].update(cookies)
        logger.info(f"Added {len(cookies)} cookies for {domain}")

        if self.auto_save and self.cookie_file:
            self.save_to_file(self.cookie_file)

    def get_cookies(self, domain: Optional[str] = None) -> Dict[str, str]:
        """
        Get cookies for a domain or all cookies.

        Args:
            domain: Domain to get cookies for (None for all)

        Returns:
            Dictionary of cookies
        """
        if domain:
            return self.cookies.get(domain, {})
        else:
            # Flatten all cookies
            all_cookies = {}
            for domain_cookies in self.cookies.values():
                all_cookies.update(domain_cookies)
            return all_cookies

    def get_cookies_for_url(self, url: str) -> Dict[str, str]:
        """
        Get cookies applicable to a URL.

        Args:
            url: URL to get cookies for

        Returns:
            Dictionary of applicable cookies
        """
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc

        # Get exact domain cookies
        cookies = self.get_cookies(domain).copy()

        # Also check for parent domain cookies
        parts = domain.split('.')
        for i in range(len(parts)):
            parent_domain = '.'.join(parts[i:])
            cookies.update(self.get_cookies(parent_domain))

        return cookies

    def remove_cookie(self, domain: str, name: str):
        """Remove a specific cookie"""
        if domain in self.cookies and name in self.cookies[domain]:
            del self.cookies[domain][name]
            logger.debug(f"Removed cookie: {name} for {domain}")

            if self.auto_save and self.cookie_file:
                self.save_to_file(self.cookie_file)

    def clear_domain_cookies(self, domain: str):
        """Clear all cookies for a domain"""
        if domain in self.cookies:
            count = len(self.cookies[domain])
            del self.cookies[domain]
            logger.info(f"Cleared {count} cookies for {domain}")

            if self.auto_save and self.cookie_file:
                self.save_to_file(self.cookie_file)

    def clear_all_cookies(self):
        """Clear all cookies"""
        count = sum(len(cookies) for cookies in self.cookies.values())
        self.cookies.clear()
        logger.info(f"Cleared all {count} cookies")

        if self.auto_save and self.cookie_file:
            self.save_to_file(self.cookie_file)

    def save_to_file(self, file_path: str, format: str = "json"):
        """
        Save cookies to file.

        Args:
            file_path: Path to save cookies
            format: Format to use ('json' or 'pickle')
        """
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            if format == "json":
                with open(file_path, 'w') as f:
                    json.dump(self.cookies, f, indent=2)
            elif format == "pickle":
                with open(file_path, 'wb') as f:
                    pickle.dump(self.cookies, f)
            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Saved cookies to {file_path}")

        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")

    def load_from_file(self, file_path: str, format: str = "json"):
        """
        Load cookies from file.

        Args:
            file_path: Path to load cookies from
            format: Format to use ('json' or 'pickle')
        """
        try:
            if not Path(file_path).exists():
                logger.warning(f"Cookie file not found: {file_path}")
                return

            if format == "json":
                with open(file_path, 'r') as f:
                    self.cookies = json.load(f)
            elif format == "pickle":
                with open(file_path, 'rb') as f:
                    self.cookies = pickle.load(f)
            else:
                raise ValueError(f"Unsupported format: {format}")

            count = sum(len(cookies) for cookies in self.cookies.values())
            logger.info(f"Loaded {count} cookies from {file_path}")

        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")

    def import_from_browser(
        self,
        browser: str = "chrome",
        domain_filter: Optional[str] = None
    ):
        """
        Import cookies from browser.

        Args:
            browser: Browser to import from ('chrome', 'firefox', 'edge', 'safari')
            domain_filter: Only import cookies for this domain
        """
        if not BROWSER_COOKIE_AVAILABLE:
            logger.error("browser-cookie3 is not installed. Install with: pip install browser-cookie3")
            return

        try:
            logger.info(f"Importing cookies from {browser}")

            # Get browser cookies
            if browser.lower() == "chrome":
                cj = browser_cookie3.chrome(domain_name=domain_filter)
            elif browser.lower() == "firefox":
                cj = browser_cookie3.firefox(domain_name=domain_filter)
            elif browser.lower() == "edge":
                cj = browser_cookie3.edge(domain_name=domain_filter)
            elif browser.lower() == "safari":
                cj = browser_cookie3.safari(domain_name=domain_filter)
            else:
                logger.error(f"Unsupported browser: {browser}")
                return

            # Convert to our format
            for cookie in cj:
                domain = cookie.domain
                if domain.startswith('.'):
                    domain = domain[1:]  # Remove leading dot

                if domain not in self.cookies:
                    self.cookies[domain] = {}

                self.cookies[domain][cookie.name] = cookie.value

            count = sum(len(cookies) for cookies in self.cookies.values())
            logger.info(f"Imported {count} cookies from {browser}")

            if self.auto_save and self.cookie_file:
                self.save_to_file(self.cookie_file)

        except Exception as e:
            logger.error(f"Failed to import cookies from {browser}: {e}")

    def to_requests_cookies(self, domain: Optional[str] = None) -> requests.cookies.RequestsCookieJar:
        """
        Convert cookies to requests.cookies.RequestsCookieJar.

        Args:
            domain: Domain to get cookies for (None for all)

        Returns:
            RequestsCookieJar object
        """
        jar = requests.cookies.RequestsCookieJar()
        cookies = self.get_cookies(domain)

        for name, value in cookies.items():
            jar.set(name, value)

        return jar

    def from_requests_cookies(
        self,
        domain: str,
        cookies: requests.cookies.RequestsCookieJar
    ):
        """
        Import cookies from requests.cookies.RequestsCookieJar.

        Args:
            domain: Domain for the cookies
            cookies: RequestsCookieJar object
        """
        cookie_dict = requests.utils.dict_from_cookiejar(cookies)
        self.add_cookies_dict(domain, cookie_dict)

    def get_cookie_string(self, domain: Optional[str] = None) -> str:
        """
        Get cookies as a cookie header string.

        Args:
            domain: Domain to get cookies for (None for all)

        Returns:
            Cookie header string
        """
        cookies = self.get_cookies(domain)
        return '; '.join([f"{name}={value}" for name, value in cookies.items()])

    def from_cookie_string(
        self,
        domain: str,
        cookie_string: str
    ):
        """
        Parse and add cookies from cookie header string.

        Args:
            domain: Domain for the cookies
            cookie_string: Cookie header string (e.g., "name1=value1; name2=value2")
        """
        cookies = {}
        for pair in cookie_string.split(';'):
            pair = pair.strip()
            if '=' in pair:
                name, value = pair.split('=', 1)
                cookies[name.strip()] = value.strip()

        self.add_cookies_dict(domain, cookies)

    def get_stats(self) -> Dict:
        """Get cookie statistics"""
        return {
            'total_domains': len(self.cookies),
            'total_cookies': sum(len(cookies) for cookies in self.cookies.values()),
            'domains': list(self.cookies.keys())
        }
