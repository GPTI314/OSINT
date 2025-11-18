"""Web technology detection module."""

from typing import Dict, Any, List
import re
import httpx
from bs4 import BeautifulSoup
from loguru import logger


class TechnologyDetector:
    """
    Detect web technologies used on websites.

    Features:
    - Framework detection
    - CMS detection
    - Server detection
    - Analytics detection
    - Library detection
    """

    def __init__(self):
        """Initialize technology detector."""
        # Technology signatures
        self.signatures = {
            # CMS
            "WordPress": [
                r"/wp-content/",
                r"/wp-includes/",
                r"wordpress",
            ],
            "Drupal": [
                r"/sites/default/",
                r"Drupal",
            ],
            "Joomla": [
                r"/components/com_",
                r"Joomla",
            ],
            "Magento": [
                r"/skin/frontend/",
                r"Mage.Cookies",
            ],
            "Shopify": [
                r"cdn.shopify.com",
                r"myshopify.com",
            ],
            # Frameworks
            "React": [
                r"react",
                r"__REACT",
            ],
            "Vue.js": [
                r"vue",
                r"__VUE__",
            ],
            "Angular": [
                r"ng-",
                r"angular",
            ],
            "jQuery": [
                r"jquery",
            ],
            "Bootstrap": [
                r"bootstrap",
            ],
            # Analytics
            "Google Analytics": [
                r"google-analytics.com",
                r"ga\(",
            ],
            "Hotjar": [
                r"hotjar",
            ],
            # Servers
            "Apache": [],
            "Nginx": [],
            "IIS": [],
        }

        logger.info("Technology detector initialized")

    async def detect(self, url: str) -> Dict[str, Any]:
        """
        Detect technologies used on a website.

        Args:
            url: Website URL

        Returns:
            Detected technologies
        """
        try:
            logger.debug(f"Detecting technologies for: {url}")

            async with httpx.AsyncClient() as client:
                response = await client.get(url, follow_redirects=True, timeout=15)
                response.raise_for_status()

                html = response.text
                headers = dict(response.headers)

                # Detect technologies
                technologies = {
                    "cms": self._detect_cms(html, headers),
                    "frameworks": self._detect_frameworks(html),
                    "analytics": self._detect_analytics(html),
                    "server": self._detect_server(headers),
                    "languages": self._detect_languages(headers),
                }

                logger.info(f"Technologies detected for: {url}")
                return technologies

        except Exception as e:
            logger.error(f"Error detecting technologies for {url}: {e}")
            return {"error": str(e)}

    def _detect_cms(self, html: str, headers: Dict[str, str]) -> List[str]:
        """Detect Content Management Systems."""
        detected = []

        cms_signatures = {
            "WordPress": self.signatures["WordPress"],
            "Drupal": self.signatures["Drupal"],
            "Joomla": self.signatures["Joomla"],
            "Magento": self.signatures["Magento"],
            "Shopify": self.signatures["Shopify"],
        }

        for cms, patterns in cms_signatures.items():
            if self._check_patterns(html, patterns):
                detected.append(cms)

        return detected

    def _detect_frameworks(self, html: str) -> List[str]:
        """Detect JavaScript frameworks."""
        detected = []

        framework_signatures = {
            "React": self.signatures["React"],
            "Vue.js": self.signatures["Vue.js"],
            "Angular": self.signatures["Angular"],
            "jQuery": self.signatures["jQuery"],
            "Bootstrap": self.signatures["Bootstrap"],
        }

        for framework, patterns in framework_signatures.items():
            if self._check_patterns(html, patterns):
                detected.append(framework)

        return detected

    def _detect_analytics(self, html: str) -> List[str]:
        """Detect analytics platforms."""
        detected = []

        analytics_signatures = {
            "Google Analytics": self.signatures["Google Analytics"],
            "Hotjar": self.signatures["Hotjar"],
        }

        for analytics, patterns in analytics_signatures.items():
            if self._check_patterns(html, patterns):
                detected.append(analytics)

        return detected

    def _detect_server(self, headers: Dict[str, str]) -> Optional[str]:
        """Detect web server from headers."""
        server_header = headers.get("server", "").lower()

        if "apache" in server_header:
            return "Apache"
        elif "nginx" in server_header:
            return "Nginx"
        elif "iis" in server_header or "microsoft" in server_header:
            return "IIS"
        elif "cloudflare" in server_header:
            return "Cloudflare"

        return server_header if server_header else None

    def _detect_languages(self, headers: Dict[str, str]) -> List[str]:
        """Detect programming languages from headers."""
        detected = []

        # Check X-Powered-By header
        powered_by = headers.get("x-powered-by", "").lower()

        if "php" in powered_by:
            detected.append("PHP")
        if "asp.net" in powered_by:
            detected.append("ASP.NET")
        if "express" in powered_by:
            detected.append("Node.js")

        return detected

    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if any pattern matches in text."""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
