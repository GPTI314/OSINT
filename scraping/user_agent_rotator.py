"""User-Agent rotation for web scraping."""

from typing import List
import random
from fake_useragent import UserAgent


class UserAgentRotator:
    """
    User-Agent rotator for avoiding detection.

    Features:
    - Realistic user agents
    - Multiple browser types
    - Random rotation
    - Custom user agent support
    """

    def __init__(self, custom_user_agents: List[str] = None):
        """
        Initialize User-Agent rotator.

        Args:
            custom_user_agents: List of custom user agents to use
        """
        self.ua = UserAgent()
        self.custom_user_agents = custom_user_agents or []

    def get_user_agent(self, browser: str = None) -> str:
        """
        Get a user agent string.

        Args:
            browser: Specific browser type (chrome, firefox, safari, edge)

        Returns:
            User-Agent string
        """
        # Use custom user agents if provided
        if self.custom_user_agents:
            return random.choice(self.custom_user_agents)

        # Get user agent based on browser type
        try:
            if browser == "chrome":
                return self.ua.chrome
            elif browser == "firefox":
                return self.ua.firefox
            elif browser == "safari":
                return self.ua.safari
            elif browser == "edge":
                return self.ua.edge
            else:
                return self.ua.random
        except Exception:
            # Fallback to a static user agent if fake_useragent fails
            return (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

    def add_custom_user_agent(self, user_agent: str):
        """Add a custom user agent to the pool."""
        self.custom_user_agents.append(user_agent)

    def get_random_mobile_user_agent(self) -> str:
        """Get a random mobile user agent."""
        mobile_user_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; Samsung SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        ]
        return random.choice(mobile_user_agents)
