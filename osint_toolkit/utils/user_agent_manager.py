"""
User-Agent Manager
Handles User-Agent rotation with realistic browser fingerprints
"""

import random
from typing import List, Optional
from enum import Enum
from fake_useragent import UserAgent
from loguru import logger


class BrowserType(Enum):
    """Browser types for User-Agent generation"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"
    OPERA = "opera"
    RANDOM = "random"


class DeviceType(Enum):
    """Device types for User-Agent generation"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


class UserAgentManager:
    """
    Manages User-Agent rotation with realistic browser fingerprints
    """

    # Pre-defined realistic User-Agents for different browsers and devices
    DESKTOP_USER_AGENTS = {
        BrowserType.CHROME: [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ],
        BrowserType.FIREFOX: [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ],
        BrowserType.SAFARI: [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        ],
        BrowserType.EDGE: [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        ],
    }

    MOBILE_USER_AGENTS = {
        BrowserType.CHROME: [
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
        ],
        BrowserType.SAFARI: [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        ],
        BrowserType.FIREFOX: [
            "Mozilla/5.0 (Android 10; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
        ],
    }

    def __init__(
        self,
        browser_type: BrowserType = BrowserType.RANDOM,
        device_type: DeviceType = DeviceType.DESKTOP,
        custom_user_agents: Optional[List[str]] = None,
        use_fake_useragent: bool = True
    ):
        """
        Initialize User-Agent manager.

        Args:
            browser_type: Preferred browser type
            device_type: Device type (desktop/mobile/tablet)
            custom_user_agents: Custom list of User-Agents
            use_fake_useragent: Use fake-useragent library as fallback
        """
        self.browser_type = browser_type
        self.device_type = device_type
        self.custom_user_agents = custom_user_agents or []
        self.use_fake_useragent = use_fake_useragent

        if self.use_fake_useragent:
            try:
                self.ua_generator = UserAgent()
            except Exception as e:
                logger.warning(f"Failed to initialize fake-useragent: {e}")
                self.ua_generator = None
        else:
            self.ua_generator = None

        logger.info(f"Initialized UserAgentManager (browser={browser_type.value}, device={device_type.value})")

    def get_user_agent(
        self,
        browser_type: Optional[BrowserType] = None,
        device_type: Optional[DeviceType] = None
    ) -> str:
        """
        Get a User-Agent string.

        Args:
            browser_type: Override default browser type
            device_type: Override default device type

        Returns:
            User-Agent string
        """
        browser = browser_type or self.browser_type
        device = device_type or self.device_type

        # Use custom User-Agents if provided
        if self.custom_user_agents:
            return random.choice(self.custom_user_agents)

        # Get User-Agent from predefined list
        user_agent = self._get_predefined_user_agent(browser, device)
        if user_agent:
            return user_agent

        # Fallback to fake-useragent library
        if self.ua_generator:
            try:
                if browser == BrowserType.RANDOM:
                    return self.ua_generator.random
                else:
                    return getattr(self.ua_generator, browser.value, self.ua_generator.random)
            except Exception as e:
                logger.warning(f"Failed to get User-Agent from fake-useragent: {e}")

        # Final fallback to a default User-Agent
        return self._get_default_user_agent()

    def _get_predefined_user_agent(
        self,
        browser_type: BrowserType,
        device_type: DeviceType
    ) -> Optional[str]:
        """Get predefined User-Agent from internal lists"""
        if device_type == DeviceType.DESKTOP:
            user_agents_dict = self.DESKTOP_USER_AGENTS
        else:
            user_agents_dict = self.MOBILE_USER_AGENTS

        if browser_type == BrowserType.RANDOM:
            # Get random User-Agent from any browser
            all_user_agents = [ua for uas in user_agents_dict.values() for ua in uas]
            if all_user_agents:
                return random.choice(all_user_agents)
        else:
            # Get User-Agent for specific browser
            user_agents = user_agents_dict.get(browser_type, [])
            if user_agents:
                return random.choice(user_agents)

        return None

    def _get_default_user_agent(self) -> str:
        """Get default fallback User-Agent"""
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def get_random_user_agent(self) -> str:
        """Get a completely random User-Agent"""
        return self.get_user_agent(
            browser_type=BrowserType.RANDOM,
            device_type=random.choice([DeviceType.DESKTOP, DeviceType.MOBILE])
        )

    def get_chrome_user_agent(self) -> str:
        """Get Chrome User-Agent"""
        return self.get_user_agent(browser_type=BrowserType.CHROME)

    def get_firefox_user_agent(self) -> str:
        """Get Firefox User-Agent"""
        return self.get_user_agent(browser_type=BrowserType.FIREFOX)

    def get_safari_user_agent(self) -> str:
        """Get Safari User-Agent"""
        return self.get_user_agent(browser_type=BrowserType.SAFARI)

    def get_mobile_user_agent(self) -> str:
        """Get mobile User-Agent"""
        return self.get_user_agent(device_type=DeviceType.MOBILE)

    def add_custom_user_agent(self, user_agent: str):
        """Add a custom User-Agent to the pool"""
        self.custom_user_agents.append(user_agent)
        logger.debug(f"Added custom User-Agent: {user_agent[:50]}...")

    def add_custom_user_agents(self, user_agents: List[str]):
        """Add multiple custom User-Agents"""
        self.custom_user_agents.extend(user_agents)
        logger.info(f"Added {len(user_agents)} custom User-Agents")

    def get_realistic_headers(
        self,
        referer: Optional[str] = None,
        accept_language: str = "en-US,en;q=0.9"
    ) -> dict:
        """
        Get realistic HTTP headers with User-Agent.

        Args:
            referer: Referer URL
            accept_language: Accept-Language header value

        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            'User-Agent': self.get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': accept_language,
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

        if referer:
            headers['Referer'] = referer

        return headers
