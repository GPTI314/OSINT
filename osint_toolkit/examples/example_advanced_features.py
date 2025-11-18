"""
Example: Advanced Features
Demonstrates proxy rotation, User-Agent rotation, rate limiting, CAPTCHA solving, etc.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from osint_toolkit.scrapers.html_scraper import HTMLScraper
from osint_toolkit.utils.proxy_manager import ProxyManager, ProxyProtocol
from osint_toolkit.utils.user_agent_manager import UserAgentManager, BrowserType, DeviceType
from osint_toolkit.utils.rate_limiter import RateLimiter, AdaptiveRateLimiter, DomainRateLimiter
from osint_toolkit.utils.cookie_manager import CookieManager


def example_proxy_rotation():
    """Proxy rotation example"""
    print("=== Proxy Rotation ===\n")

    # Initialize proxy manager
    proxy_manager = ProxyManager()

    # Add proxies (these are example proxies - replace with real ones)
    proxy_manager.add_proxies_from_list([
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "http://proxy3.example.com:8080"
    ])

    print(f"Added {len(proxy_manager.proxies)} proxies\n")

    # Get next proxy (round-robin)
    proxy = proxy_manager.get_next_proxy()
    if proxy:
        print(f"Selected proxy: {proxy.to_url()}")

    # Get random proxy
    proxy = proxy_manager.get_random_proxy()
    if proxy:
        print(f"Random proxy: {proxy.to_url()}")

    # Get stats
    stats = proxy_manager.get_stats()
    print(f"\nProxy stats: {stats['working']}/{stats['total']} working\n")


def example_user_agent_rotation():
    """User-Agent rotation example"""
    print("=== User-Agent Rotation ===\n")

    # Initialize User-Agent manager
    ua_manager = UserAgentManager(
        browser_type=BrowserType.RANDOM,
        device_type=DeviceType.DESKTOP
    )

    # Get different User-Agents
    print("Random User-Agents:")
    for i in range(3):
        ua = ua_manager.get_user_agent()
        print(f"  {i+1}. {ua[:80]}...")

    # Get specific browser User-Agents
    print("\nChrome User-Agent:")
    print(f"  {ua_manager.get_chrome_user_agent()[:80]}...")

    print("\nFirefox User-Agent:")
    print(f"  {ua_manager.get_firefox_user_agent()[:80]}...")

    print("\nMobile User-Agent:")
    print(f"  {ua_manager.get_mobile_user_agent()[:80]}...")

    # Get realistic headers
    print("\nRealistic Headers:")
    headers = ua_manager.get_realistic_headers(referer="https://google.com")
    for key, value in list(headers.items())[:5]:
        print(f"  {key}: {value[:60]}...")

    print()


def example_rate_limiting():
    """Rate limiting example"""
    print("=== Rate Limiting ===\n")

    # Basic rate limiter
    limiter = RateLimiter(requests_per_second=2.0)

    print("Making 5 requests with rate limit (2 req/s):")
    import time
    for i in range(5):
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start
        print(f"  Request {i+1} - waited {elapsed:.2f}s")

    print()


def example_adaptive_rate_limiting():
    """Adaptive rate limiting example"""
    print("=== Adaptive Rate Limiting ===\n")

    limiter = AdaptiveRateLimiter(
        initial_rate=2.0,
        min_rate=0.5,
        max_rate=5.0
    )

    print(f"Initial rate: {limiter.get_current_rate():.2f} req/s")

    # Simulate successful requests
    for i in range(5):
        limiter.acquire()
        limiter.report_success()

    print(f"After 5 successes: {limiter.get_current_rate():.2f} req/s")

    # Simulate errors
    for i in range(2):
        limiter.acquire()
        limiter.report_error(status_code=429)

    print(f"After 2 errors: {limiter.get_current_rate():.2f} req/s\n")


def example_domain_rate_limiting():
    """Domain-specific rate limiting"""
    print("=== Domain Rate Limiting ===\n")

    limiter = DomainRateLimiter(
        default_requests_per_second=1.0
    )

    # Set custom limits for specific domains
    limiter.set_domain_limit("api.github.com", 5.0)
    limiter.set_domain_limit("twitter.com", 0.5)

    print("Domain limits:")
    print(f"  api.github.com: 5.0 req/s")
    print(f"  twitter.com: 0.5 req/s")
    print(f"  others: 1.0 req/s (default)\n")


def example_cookie_management():
    """Cookie management example"""
    print("=== Cookie Management ===\n")

    # Initialize cookie manager
    cookie_manager = CookieManager(
        cookie_file="./cookies.json",
        auto_save=True
    )

    # Add cookies
    cookie_manager.add_cookie(
        domain="example.com",
        name="session_id",
        value="abc123xyz"
    )

    cookie_manager.add_cookies_dict(
        domain="example.com",
        cookies={
            "user_id": "12345",
            "preferences": "dark_mode=true"
        }
    )

    print("Added cookies for example.com")

    # Get cookies
    cookies = cookie_manager.get_cookies("example.com")
    print(f"\nCookies for example.com: {cookies}")

    # Get cookie string
    cookie_string = cookie_manager.get_cookie_string("example.com")
    print(f"\nCookie header: {cookie_string}")

    # Stats
    stats = cookie_manager.get_stats()
    print(f"\nStats: {stats}\n")

    # Clean up
    import os
    if os.path.exists("./cookies.json"):
        os.remove("./cookies.json")


def example_combined_features():
    """Using multiple features together"""
    print("=== Combined Features ===\n")

    # Setup User-Agent rotation
    ua_manager = UserAgentManager()

    # Setup cookie management
    cookie_manager = CookieManager()
    cookie_manager.add_cookie("httpbin.org", "test", "value123")

    # Create scraper with all features
    scraper = HTMLScraper(
        user_agent=ua_manager.get_user_agent(),
        rate_limit_delay=1.0,
        max_retries=3,
        timeout=30
    )

    # Add cookies to scraper
    scraper.update_cookies(cookie_manager.get_cookies("httpbin.org"))

    # Make request
    url = "https://httpbin.org/cookies"
    print(f"Scraping {url}...")

    try:
        soup = scraper.scrape(url)
        print(f"Response: {soup.get_text()[:200]}...\n")
    except Exception as e:
        print(f"Error: {e}\n")

    scraper.close()


def example_custom_headers():
    """Custom headers example"""
    print("=== Custom Headers ===\n")

    custom_headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'X-Custom-Header': 'CustomValue'
    }

    scraper = HTMLScraper(headers=custom_headers)

    url = "https://httpbin.org/headers"
    print(f"Scraping {url} with custom headers...")

    try:
        soup = scraper.scrape(url)
        print(f"Response: {soup.get_text()[:200]}...\n")
    except Exception as e:
        print(f"Error: {e}\n")

    scraper.close()


if __name__ == "__main__":
    print("Advanced Features Examples\n" + "=" * 50 + "\n")

    try:
        example_proxy_rotation()
        example_user_agent_rotation()
        example_rate_limiting()
        example_adaptive_rate_limiting()
        example_domain_rate_limiting()
        example_cookie_management()
        example_combined_features()
        example_custom_headers()

        print("=" * 50)
        print("All examples completed successfully!")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
