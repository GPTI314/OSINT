"""
Example: HTML Scraping
Demonstrates static HTML scraping with BeautifulSoup and lxml
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from osint_toolkit.scrapers.html_scraper import HTMLScraper, LXMLScraper
from osint_toolkit.utils.user_agent_manager import UserAgentManager
from osint_toolkit.utils.rate_limiter import RateLimiter


def example_basic_scraping():
    """Basic HTML scraping example"""
    print("=== Basic HTML Scraping ===\n")

    # Initialize scraper
    scraper = HTMLScraper(
        timeout=30,
        rate_limit_delay=1.0
    )

    # Example URL (using httpbin for testing)
    url = "https://httpbin.org/html"

    # Scrape the page
    soup = scraper.scrape(url)

    # Extract text
    text = soup.get_text(strip=True)
    print(f"Page text: {text[:200]}...\n")

    # Find specific elements
    h1 = soup.find('h1')
    if h1:
        print(f"H1 tag: {h1.get_text()}\n")

    scraper.close()


def example_link_extraction():
    """Extract all links from a page"""
    print("=== Link Extraction ===\n")

    scraper = HTMLScraper()

    # Example URL
    url = "https://example.com"

    # Extract all links
    links = scraper.scrape_links(url, absolute=True)

    print(f"Found {len(links)} links:")
    for link in links[:5]:  # Show first 5
        print(f"  - {link}")

    scraper.close()


def example_image_extraction():
    """Extract all images from a page"""
    print("\n=== Image Extraction ===\n")

    scraper = HTMLScraper()

    url = "https://example.com"

    # Extract images
    images = scraper.scrape_images(url, absolute=True)

    print(f"Found {len(images)} images:")
    for img in images[:3]:  # Show first 3
        print(f"  - {img['src']}")
        print(f"    Alt: {img.get('alt', 'N/A')}\n")

    scraper.close()


def example_css_selectors():
    """Using CSS selectors"""
    print("=== CSS Selectors ===\n")

    scraper = HTMLScraper()

    url = "https://example.com"

    # Select elements using CSS selectors
    soup = scraper.scrape(url)

    # Find all paragraph tags
    paragraphs = soup.select('p')
    print(f"Found {len(paragraphs)} paragraphs")

    # Find element by ID
    # element = soup.select_one('#some-id')

    scraper.close()


def example_lxml_xpath():
    """Using lxml with XPath"""
    print("=== LXML XPath ===\n")

    scraper = LXMLScraper()

    url = "https://example.com"

    # Use XPath to extract data
    links = scraper.xpath(url, '//a/@href')
    print(f"Found {len(links)} links using XPath")

    # Extract text from specific elements
    headings = scraper.xpath(url, '//h1/text()')
    if headings:
        print(f"H1 heading: {headings[0]}")

    scraper.close()


def example_with_user_agent():
    """Scraping with User-Agent rotation"""
    print("\n=== User-Agent Rotation ===\n")

    # Initialize User-Agent manager
    ua_manager = UserAgentManager()

    # Create scraper with custom User-Agent
    scraper = HTMLScraper(
        user_agent=ua_manager.get_user_agent()
    )

    url = "https://httpbin.org/user-agent"

    soup = scraper.scrape(url)
    print(f"Response: {soup.get_text()}\n")

    scraper.close()


def example_with_rate_limiting():
    """Scraping multiple pages with rate limiting"""
    print("=== Rate Limiting ===\n")

    scraper = HTMLScraper(
        rate_limit_delay=2.0  # 2 seconds between requests
    )

    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/robots.txt",
        "https://example.com"
    ]

    for url in urls:
        print(f"Scraping {url}...")
        try:
            soup = scraper.scrape(url)
            print(f"  Success! Title: {soup.title.string if soup.title else 'N/A'}\n")
        except Exception as e:
            print(f"  Error: {e}\n")

    scraper.close()


def example_error_handling():
    """Error handling and retries"""
    print("=== Error Handling ===\n")

    scraper = HTMLScraper(
        max_retries=3,
        retry_backoff_factor=2.0
    )

    # Try to scrape an invalid URL
    try:
        soup = scraper.scrape("https://invalid-domain-that-does-not-exist-12345.com")
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}\n")

    scraper.close()


if __name__ == "__main__":
    print("HTML Scraping Examples\n" + "=" * 50 + "\n")

    try:
        example_basic_scraping()
        example_link_extraction()
        example_image_extraction()
        example_css_selectors()
        example_lxml_xpath()
        example_with_user_agent()
        example_with_rate_limiting()
        example_error_handling()

        print("\n" + "=" * 50)
        print("All examples completed successfully!")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
