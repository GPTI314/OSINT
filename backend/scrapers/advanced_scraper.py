"""
Advanced web scraper using Playwright for JavaScript-heavy websites.
"""
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Page
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AdvancedScraper:
    """Advanced scraper for JavaScript-rendered websites using Playwright."""

    async def scrape(
        self,
        url: str,
        wait_time: int = 0,
        screenshot: bool = False,
        execute_js: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scrape a JavaScript-heavy website.

        Args:
            url: URL to scrape
            wait_time: Time to wait for page load (seconds)
            screenshot: Whether to take a screenshot
            execute_js: Optional JavaScript code to execute

        Returns:
            Dict containing scraped data
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()

                # Navigate to URL
                await page.goto(url, wait_until="networkidle")

                # Wait if specified
                if wait_time > 0:
                    await page.wait_for_timeout(wait_time * 1000)

                # Execute custom JavaScript if provided
                js_result = None
                if execute_js:
                    js_result = await page.evaluate(execute_js)

                # Get page content
                content = await page.content()
                title = await page.title()

                # Take screenshot if requested
                screenshot_data = None
                if screenshot:
                    screenshot_data = await page.screenshot(full_page=True)

                await browser.close()

                return {
                    "url": url,
                    "title": title,
                    "content": content,
                    "js_result": js_result,
                    "screenshot": screenshot_data,
                    "scraped_at": datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Error scraping {url} with Playwright: {e}")
            raise
