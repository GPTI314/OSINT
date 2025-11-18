"""Dynamic scraper using Playwright for JavaScript-heavy pages."""

from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
from loguru import logger


class DynamicScraper:
    """
    Dynamic scraper using Playwright for pages requiring JavaScript execution.

    Features:
    - Browser automation
    - JavaScript execution
    - Screenshot capture
    - Network monitoring
    - Cookie management
    """

    def __init__(self, proxy_manager=None, user_agent_rotator=None):
        """Initialize dynamic scraper."""
        self.proxy_manager = proxy_manager
        self.user_agent_rotator = user_agent_rotator
        self.playwright = None
        self.browser: Optional[Browser] = None

    async def _ensure_browser(self):
        """Ensure browser is initialized."""
        if self.browser is None:
            self.playwright = await async_playwright().start()
            launch_options = {
                "headless": True,
                "args": ["--no-sandbox", "--disable-setuid-sandbox"],
            }

            # Add proxy if available
            if self.proxy_manager:
                proxy = self.proxy_manager.get_proxy()
                if proxy:
                    launch_options["proxy"] = {"server": proxy}

            self.browser = await self.playwright.chromium.launch(**launch_options)

    async def scrape(
        self,
        url: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Scrape a dynamic page using browser automation.

        Args:
            url: URL to scrape
            config: Additional configuration

        Returns:
            Dictionary containing scraped data
        """
        config = config or {}

        try:
            await self._ensure_browser()

            # Create new page
            context_options = {}
            if self.user_agent_rotator:
                context_options["user_agent"] = self.user_agent_rotator.get_user_agent()

            context = await self.browser.new_context(**context_options)
            page: Page = await context.new_page()

            # Navigate to page
            timeout = config.get("timeout", 30000)
            await page.goto(url, timeout=timeout, wait_until="networkidle")

            # Wait for specific selectors if provided
            wait_for = config.get("wait_for")
            if wait_for:
                if isinstance(wait_for, str):
                    await page.wait_for_selector(wait_for, timeout=timeout)
                elif isinstance(wait_for, list):
                    for selector in wait_for:
                        await page.wait_for_selector(selector, timeout=timeout)

            # Execute custom JavaScript if provided
            if config.get("execute_js"):
                await page.evaluate(config["execute_js"])

            # Extract data using selectors
            extracted_data = {}
            selectors = config.get("selectors", {})

            for field, selector in selectors.items():
                if isinstance(selector, str):
                    elements = await page.query_selector_all(selector)
                    values = []
                    for elem in elements:
                        text = await elem.inner_text()
                        values.append(text.strip())
                    extracted_data[field] = values
                elif isinstance(selector, dict):
                    selector_str = selector.get("selector")
                    attr = selector.get("attr")
                    multiple = selector.get("multiple", True)

                    elements = await page.query_selector_all(selector_str)
                    values = []
                    for elem in elements:
                        if attr:
                            value = await elem.get_attribute(attr)
                        else:
                            value = await elem.inner_text()
                        if value:
                            values.append(value.strip() if isinstance(value, str) else value)

                    extracted_data[field] = values if multiple else (values[0] if values else None)

            # Get page content
            html = await page.content() if config.get("include_html") else None

            # Take screenshot if requested
            screenshot = None
            if config.get("screenshot"):
                screenshot = await page.screenshot(full_page=config.get("full_page_screenshot", False))

            await context.close()

            return {
                "success": True,
                "data": extracted_data,
                "html": html,
                "screenshot": screenshot,
            }

        except Exception as e:
            logger.error(f"Error scraping {url} with browser: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def close(self):
        """Close browser and cleanup."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
