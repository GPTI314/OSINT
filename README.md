# OSINT Toolkit

Open-Source Intelligence (OSINT) toolkit with comprehensive scraping engine: modular collectors, enrichment pipeline, link analysis, risk scoring, and investigative workflow automation.

## Features

### Core Scraping Components

✅ **Static HTML Scraping** - BeautifulSoup & lxml support with CSS selectors and XPath
✅ **JavaScript-Rendered Pages** - Playwright & Selenium integration for dynamic content
✅ **API Endpoints** - REST and GraphQL support with authentication
✅ **File Downloads** - PDFs, images, documents with progress tracking
✅ **Image Processing** - Scraping with PIL/OpenCV processing capabilities

### Advanced Features

✅ **Proxy Rotation** - Multi-provider proxy support with health checking
✅ **User-Agent Rotation** - Realistic browser fingerprints for Chrome, Firefox, Safari, Edge
✅ **CAPTCHA Solving** - Integration with 2Captcha and Anti-Captcha services
✅ **Rate Limiting** - Multiple strategies: token bucket, sliding window, adaptive
✅ **Cookie Management** - Session persistence and browser cookie import
✅ **Header Customization** - Full HTTP header control with realistic defaults
✅ **SSL Certificate Handling** - Support for self-signed certificates
✅ **Timeout Management** - Configurable timeouts per request
✅ **Retry Logic** - Exponential backoff with configurable attempts
✅ **Concurrent Scraping** - Async/await support for high performance

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd OSINT
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright browsers (optional, for JavaScript scraping)

```bash
playwright install
```

### 4. Configure environment (optional)

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Quick Start

### Static HTML Scraping

```python
from osint_toolkit.scrapers.html_scraper import HTMLScraper

# Initialize scraper
scraper = HTMLScraper(
    timeout=30,
    rate_limit_delay=1.0
)

# Scrape a page
soup = scraper.scrape("https://example.com")

# Extract data
title = soup.find('title').text
links = scraper.scrape_links("https://example.com")
images = scraper.scrape_images("https://example.com")

scraper.close()
```

### JavaScript Scraping

```python
from osint_toolkit.scrapers.js_scraper import PlaywrightScraper

# Initialize scraper
with PlaywrightScraper(headless=True) as scraper:
    # Scrape JavaScript-rendered page
    soup = scraper.scrape("https://example.com")

    # Scrape with interactions
    soup = scraper.scrape_with_interaction(
        "https://example.com",
        interactions=[
            {'action': 'click', 'selector': '#button'},
            {'action': 'wait', 'time': 2},
            {'action': 'fill', 'selector': '#input', 'value': 'search query'}
        ]
    )
```

### API Scraping

```python
from osint_toolkit.scrapers.api_scraper import RESTScraper

# Initialize API scraper
scraper = RESTScraper(
    base_url="https://api.example.com",
    bearer_token="your-token-here"
)

# Make requests
data = scraper.get_json("/endpoint")
result = scraper.post_json("/endpoint", json_data={"key": "value"})

# Paginate through results
all_data = scraper.paginate("/items", max_pages=10)

scraper.close()
```

### File Downloads

```python
from osint_toolkit.scrapers.file_downloader import FileDownloader

# Initialize downloader
downloader = FileDownloader(download_dir="./downloads")

# Download files
filepath = downloader.scrape("https://example.com/file.pdf")

# Download multiple files
files = downloader.download_multiple([
    "https://example.com/file1.pdf",
    "https://example.com/file2.pdf"
])

downloader.close()
```

### Image Scraping with Processing

```python
from osint_toolkit.scrapers.image_scraper import ImageScraper

# Initialize image scraper
scraper = ImageScraper(download_dir="./images")

# Download and process image
filepath = scraper.scrape(
    "https://example.com/image.jpg",
    resize=(800, 600)
)

# Image processing
scraper.resize_image(filepath, width=400)
scraper.convert_to_grayscale(filepath)
scraper.adjust_brightness(filepath, factor=1.2)

scraper.close()
```

## Advanced Usage

### Proxy Rotation

```python
from osint_toolkit.utils.proxy_manager import ProxyManager
from osint_toolkit.scrapers.html_scraper import HTMLScraper

# Setup proxy manager
proxy_manager = ProxyManager()
proxy_manager.add_proxies_from_list([
    "http://proxy1:8080",
    "http://proxy2:8080"
])

# Test proxies
proxy_manager.test_all_proxies()

# Use with scraper
proxy = proxy_manager.get_next_proxy()
scraper = HTMLScraper(proxy=proxy.to_url())
```

### User-Agent Rotation

```python
from osint_toolkit.utils.user_agent_manager import UserAgentManager, BrowserType
from osint_toolkit.scrapers.html_scraper import HTMLScraper

# Setup User-Agent rotation
ua_manager = UserAgentManager(browser_type=BrowserType.RANDOM)

# Get realistic headers
headers = ua_manager.get_realistic_headers(referer="https://google.com")

# Use with scraper
scraper = HTMLScraper(
    user_agent=ua_manager.get_user_agent(),
    headers=headers
)
```

### Rate Limiting

```python
from osint_toolkit.utils.rate_limiter import AdaptiveRateLimiter
from osint_toolkit.scrapers.html_scraper import HTMLScraper

# Adaptive rate limiting
limiter = AdaptiveRateLimiter(
    initial_rate=2.0,
    min_rate=0.5,
    max_rate=5.0
)

scraper = HTMLScraper(rate_limit_delay=0.5)

# Use rate limiter
for url in urls:
    limiter.acquire()
    try:
        soup = scraper.scrape(url)
        limiter.report_success()
    except Exception as e:
        limiter.report_error()
```

### CAPTCHA Solving

```python
from osint_toolkit.utils.captcha_solver import CaptchaSolver, CaptchaService

# Initialize CAPTCHA solver
solver = CaptchaSolver(
    service=CaptchaService.TWO_CAPTCHA,
    api_key="your-api-key"
)

# Solve reCAPTCHA v2
solution = solver.solve_recaptcha_v2(
    site_key="site-key",
    page_url="https://example.com"
)

# Solve reCAPTCHA v3
solution = solver.solve_recaptcha_v3(
    site_key="site-key",
    page_url="https://example.com",
    action="verify"
)
```

### Cookie Management

```python
from osint_toolkit.utils.cookie_manager import CookieManager

# Initialize cookie manager
cookie_manager = CookieManager(cookie_file="cookies.json")

# Add cookies
cookie_manager.add_cookie("example.com", "session_id", "abc123")

# Import from browser
cookie_manager.import_from_browser("chrome", domain_filter="example.com")

# Use with scraper
scraper = HTMLScraper()
scraper.update_cookies(cookie_manager.get_cookies("example.com"))
```

### Async Scraping

```python
import asyncio
from osint_toolkit.scrapers.html_scraper import AsyncHTMLScraper

async def main():
    scraper = AsyncHTMLScraper(max_concurrent=10)

    urls = ["https://example1.com", "https://example2.com", "https://example3.com"]

    # Scrape multiple URLs concurrently
    results = await scraper.scrape_multiple_async(urls)

    for soup in results:
        print(soup.title.string)

asyncio.run(main())
```

## Configuration

### Using Environment Variables

Create a `.env` file:

```bash
# Rate Limiting
RATE_LIMIT__ENABLED=true
RATE_LIMIT__REQUESTS_PER_SECOND=1.0

# Proxy
PROXY__ENABLED=true
PROXY__ROTATION=true

# CAPTCHA
CAPTCHA__ENABLED=true
CAPTCHA__SERVICE=2captcha
CAPTCHA__API_KEY=your-key-here
```

### Using Configuration Files

```python
from osint_toolkit.config.settings import load_settings

# Load from YAML/JSON
settings = load_settings("config.yaml")

# Use settings
scraper = HTMLScraper(
    timeout=settings.html_scraper.timeout,
    max_retries=settings.html_scraper.max_retries
)
```

## Project Structure

```
OSINT/
├── osint_toolkit/
│   ├── scrapers/
│   │   ├── base_scraper.py      # Base scraper classes
│   │   ├── html_scraper.py      # HTML scraping
│   │   ├── js_scraper.py        # JavaScript scraping
│   │   ├── api_scraper.py       # API scraping
│   │   ├── file_downloader.py   # File downloads
│   │   └── image_scraper.py     # Image scraping
│   ├── utils/
│   │   ├── proxy_manager.py     # Proxy rotation
│   │   ├── user_agent_manager.py # User-Agent rotation
│   │   ├── rate_limiter.py      # Rate limiting
│   │   ├── captcha_solver.py    # CAPTCHA solving
│   │   └── cookie_manager.py    # Cookie management
│   ├── config/
│   │   └── settings.py          # Configuration management
│   └── examples/
│       ├── example_html_scraping.py
│       ├── example_advanced_features.py
│       └── example_file_download_api.py
├── requirements.txt
├── .env.example
└── README.md
```

## Examples

See the `osint_toolkit/examples/` directory for comprehensive examples:

- `example_html_scraping.py` - Static HTML scraping examples
- `example_advanced_features.py` - Proxy rotation, User-Agent rotation, rate limiting
- `example_file_download_api.py` - File downloads and API scraping

Run examples:

```bash
python osint_toolkit/examples/example_html_scraping.py
python osint_toolkit/examples/example_advanced_features.py
python osint_toolkit/examples/example_file_download_api.py
```

## API Reference

### HTMLScraper

```python
HTMLScraper(
    parser="lxml",           # HTML parser
    timeout=30,              # Request timeout
    max_retries=3,           # Max retry attempts
    verify_ssl=True,         # SSL verification
    proxy=None,              # Proxy URL
    headers=None,            # Custom headers
    rate_limit_delay=1.0     # Rate limit delay
)
```

### PlaywrightScraper

```python
PlaywrightScraper(
    browser_type="chromium", # Browser type
    headless=True,           # Headless mode
    proxy=None,              # Proxy URL
    timeout=30000            # Timeout (ms)
)
```

### RESTScraper

```python
RESTScraper(
    base_url=None,           # Base API URL
    bearer_token=None,       # Bearer token
    api_key=None,            # API key
    timeout=30               # Request timeout
)
```

### FileDownloader

```python
FileDownloader(
    download_dir="./downloads", # Download directory
    chunk_size=8192,            # Download chunk size
    verify_mime_type=True       # Verify MIME type
)
```

## Best Practices

### 1. Respect Rate Limits

Always use rate limiting to avoid overwhelming servers:

```python
scraper = HTMLScraper(rate_limit_delay=2.0)  # 2 seconds between requests
```

### 2. Use Realistic User-Agents

Rotate User-Agents to appear more legitimate:

```python
ua_manager = UserAgentManager()
scraper = HTMLScraper(user_agent=ua_manager.get_user_agent())
```

### 3. Handle Errors Gracefully

Always implement proper error handling:

```python
try:
    soup = scraper.scrape(url)
except Exception as e:
    logger.error(f"Failed to scrape {url}: {e}")
```

### 4. Use Proxies for Large-Scale Scraping

Rotate proxies to distribute requests:

```python
proxy_manager = ProxyManager()
proxy = proxy_manager.get_next_proxy()
```

### 5. Clean Up Resources

Always close scrapers when done:

```python
scraper = HTMLScraper()
try:
    # Your scraping code
    pass
finally:
    scraper.close()

# Or use context manager
with HTMLScraper() as scraper:
    # Your scraping code
    pass
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Disclaimer

This toolkit is for educational and authorized security testing purposes only. Always ensure you have permission to scrape websites and respect robots.txt files and terms of service.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.
