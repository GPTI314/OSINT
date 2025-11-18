"""
JavaScript Scraper
Handles JavaScript-rendered pages using Playwright and Selenium
"""

from typing import Optional, Dict, List, Any, Callable
import time
import asyncio
from pathlib import Path
from bs4 import BeautifulSoup
from loguru import logger

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed")

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not installed")


class PlaywrightScraper:
    """
    Scraper using Playwright for JavaScript-rendered pages
    """

    def __init__(
        self,
        browser_type: str = "chromium",
        headless: bool = True,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None,
        timeout: int = 30000,
        viewport: Optional[Dict[str, int]] = None,
        ignore_https_errors: bool = False
    ):
        """
        Initialize Playwright scraper.

        Args:
            browser_type: Browser to use ('chromium', 'firefox', 'webkit')
            headless: Run browser in headless mode
            proxy: Proxy server URL
            user_agent: Custom User-Agent
            timeout: Default timeout in milliseconds
            viewport: Browser viewport size {'width': 1920, 'height': 1080}
            ignore_https_errors: Ignore HTTPS errors
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is not installed. Install with: pip install playwright && playwright install")

        self.browser_type = browser_type
        self.headless = headless
        self.proxy = proxy
        self.user_agent = user_agent
        self.timeout = timeout
        self.viewport = viewport or {'width': 1920, 'height': 1080}
        self.ignore_https_errors = ignore_https_errors

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

        logger.info(f"Initialized PlaywrightScraper (browser={browser_type}, headless={headless})")

    def start(self):
        """Start browser"""
        if self.browser:
            logger.warning("Browser already started")
            return

        self.playwright = sync_playwright().start()

        # Browser launch options
        launch_options = {
            'headless': self.headless
        }

        # Get browser
        if self.browser_type == "chromium":
            self.browser = self.playwright.chromium.launch(**launch_options)
        elif self.browser_type == "firefox":
            self.browser = self.playwright.firefox.launch(**launch_options)
        elif self.browser_type == "webkit":
            self.browser = self.playwright.webkit.launch(**launch_options)
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")

        # Context options
        context_options = {
            'viewport': self.viewport,
            'ignore_https_errors': self.ignore_https_errors
        }

        if self.proxy:
            context_options['proxy'] = {'server': self.proxy}

        if self.user_agent:
            context_options['user_agent'] = self.user_agent

        self.context = self.browser.new_context(**context_options)
        self.context.set_default_timeout(self.timeout)

        logger.info("Browser started")

    def stop(self):
        """Stop browser"""
        if self.context:
            self.context.close()
            self.context = None

        if self.browser:
            self.browser.close()
            self.browser = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None

        logger.info("Browser stopped")

    def scrape(
        self,
        url: str,
        wait_for: Optional[str] = None,
        wait_time: Optional[int] = None,
        screenshot: Optional[str] = None,
        execute_script: Optional[str] = None
    ) -> BeautifulSoup:
        """
        Scrape a URL with JavaScript rendering.

        Args:
            url: URL to scrape
            wait_for: CSS selector to wait for before returning
            wait_time: Additional wait time in seconds
            screenshot: Path to save screenshot
            execute_script: JavaScript to execute before scraping

        Returns:
            BeautifulSoup object of rendered page
        """
        if not self.browser:
            self.start()

        try:
            page = self.context.new_page()
            logger.info(f"Navigating to {url}")
            page.goto(url)

            # Wait for selector if specified
            if wait_for:
                logger.debug(f"Waiting for selector: {wait_for}")
                page.wait_for_selector(wait_for)

            # Additional wait time
            if wait_time:
                logger.debug(f"Waiting {wait_time}s")
                time.sleep(wait_time)

            # Execute custom JavaScript
            if execute_script:
                logger.debug("Executing custom JavaScript")
                page.evaluate(execute_script)

            # Take screenshot if requested
            if screenshot:
                page.screenshot(path=screenshot)
                logger.info(f"Screenshot saved to {screenshot}")

            # Get rendered HTML
            content = page.content()
            page.close()

            soup = BeautifulSoup(content, 'lxml')
            logger.info(f"Successfully scraped {url}")
            return soup

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            raise

    def scrape_with_interaction(
        self,
        url: str,
        interactions: List[Dict[str, Any]]
    ) -> BeautifulSoup:
        """
        Scrape with user interactions (clicks, typing, etc.).

        Args:
            url: URL to scrape
            interactions: List of interaction dictionaries
                [
                    {'action': 'click', 'selector': '#button'},
                    {'action': 'fill', 'selector': '#input', 'value': 'text'},
                    {'action': 'wait', 'time': 2}
                ]

        Returns:
            BeautifulSoup object
        """
        if not self.browser:
            self.start()

        try:
            page = self.context.new_page()
            page.goto(url)

            # Perform interactions
            for interaction in interactions:
                action = interaction.get('action')

                if action == 'click':
                    selector = interaction['selector']
                    logger.debug(f"Clicking {selector}")
                    page.click(selector)

                elif action == 'fill':
                    selector = interaction['selector']
                    value = interaction['value']
                    logger.debug(f"Filling {selector} with '{value}'")
                    page.fill(selector, value)

                elif action == 'wait':
                    wait_time = interaction.get('time', 1)
                    logger.debug(f"Waiting {wait_time}s")
                    time.sleep(wait_time)

                elif action == 'wait_for_selector':
                    selector = interaction['selector']
                    logger.debug(f"Waiting for {selector}")
                    page.wait_for_selector(selector)

                elif action == 'scroll':
                    logger.debug("Scrolling page")
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                elif action == 'execute':
                    script = interaction['script']
                    logger.debug("Executing custom script")
                    page.evaluate(script)

            # Get final content
            content = page.content()
            page.close()

            soup = BeautifulSoup(content, 'lxml')
            return soup

        except Exception as e:
            logger.error(f"Failed to scrape with interactions: {e}")
            raise

    def scrape_infinite_scroll(
        self,
        url: str,
        scroll_pause_time: float = 2.0,
        max_scrolls: int = 10
    ) -> BeautifulSoup:
        """
        Scrape infinite scroll pages.

        Args:
            url: URL to scrape
            scroll_pause_time: Time to wait between scrolls
            max_scrolls: Maximum number of scrolls

        Returns:
            BeautifulSoup object
        """
        if not self.browser:
            self.start()

        try:
            page = self.context.new_page()
            page.goto(url)

            last_height = page.evaluate("document.body.scrollHeight")

            for i in range(max_scrolls):
                # Scroll down
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(scroll_pause_time)

                # Calculate new height
                new_height = page.evaluate("document.body.scrollHeight")

                # Break if no more content
                if new_height == last_height:
                    logger.info(f"Reached end of infinite scroll after {i+1} scrolls")
                    break

                last_height = new_height
                logger.debug(f"Scroll {i+1}/{max_scrolls}")

            content = page.content()
            page.close()

            soup = BeautifulSoup(content, 'lxml')
            return soup

        except Exception as e:
            logger.error(f"Failed to scrape infinite scroll: {e}")
            raise

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


class SeleniumScraper:
    """
    Scraper using Selenium for JavaScript-rendered pages
    """

    def __init__(
        self,
        browser: str = "chrome",
        headless: bool = True,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize Selenium scraper.

        Args:
            browser: Browser to use ('chrome', 'firefox')
            headless: Run browser in headless mode
            proxy: Proxy server URL
            user_agent: Custom User-Agent
            timeout: Default timeout in seconds
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is not installed. Install with: pip install selenium")

        self.browser_name = browser
        self.headless = headless
        self.proxy = proxy
        self.user_agent = user_agent
        self.timeout = timeout
        self.driver = None

        logger.info(f"Initialized SeleniumScraper (browser={browser}, headless={headless})")

    def start(self):
        """Start browser"""
        if self.driver:
            logger.warning("Browser already started")
            return

        if self.browser_name == "chrome":
            options = ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            if self.user_agent:
                options.add_argument(f'user-agent={self.user_agent}')
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')

            self.driver = webdriver.Chrome(options=options)

        elif self.browser_name == "firefox":
            options = FirefoxOptions()
            if self.headless:
                options.add_argument('--headless')
            if self.user_agent:
                options.set_preference("general.useragent.override", self.user_agent)

            self.driver = webdriver.Firefox(options=options)

        else:
            raise ValueError(f"Unsupported browser: {self.browser_name}")

        self.driver.set_page_load_timeout(self.timeout)
        logger.info("Selenium browser started")

    def stop(self):
        """Stop browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Selenium browser stopped")

    def scrape(
        self,
        url: str,
        wait_for: Optional[str] = None,
        wait_time: Optional[int] = None,
        screenshot: Optional[str] = None
    ) -> BeautifulSoup:
        """
        Scrape a URL.

        Args:
            url: URL to scrape
            wait_for: CSS selector to wait for
            wait_time: Additional wait time in seconds
            screenshot: Path to save screenshot

        Returns:
            BeautifulSoup object
        """
        if not self.driver:
            self.start()

        try:
            logger.info(f"Navigating to {url}")
            self.driver.get(url)

            # Wait for element if specified
            if wait_for:
                wait = WebDriverWait(self.driver, self.timeout)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for)))

            # Additional wait
            if wait_time:
                time.sleep(wait_time)

            # Screenshot
            if screenshot:
                self.driver.save_screenshot(screenshot)
                logger.info(f"Screenshot saved to {screenshot}")

            # Get page source
            content = self.driver.page_source

            soup = BeautifulSoup(content, 'lxml')
            logger.info(f"Successfully scraped {url}")
            return soup

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            raise

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
