"""
Example: File Downloading and API Scraping
Demonstrates file downloads, image scraping, and API interactions
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from osint_toolkit.scrapers.file_downloader import FileDownloader
from osint_toolkit.scrapers.image_scraper import ImageScraper
from osint_toolkit.scrapers.api_scraper import RESTScraper


def example_file_download():
    """Basic file download example"""
    print("=== File Download ===\n")

    downloader = FileDownloader(
        download_dir="./downloads_example",
        chunk_size=8192
    )

    # Download a file
    url = "https://httpbin.org/image/png"
    print(f"Downloading {url}...")

    try:
        filepath = downloader.scrape(url, filename="test_image.png", progress=False)
        print(f"Downloaded to: {filepath}")

        # Get file info
        info = downloader.get_file_info(filepath)
        print(f"File info: {info}\n")

        # Cleanup
        import shutil
        shutil.rmtree("./downloads_example", ignore_errors=True)

    except Exception as e:
        print(f"Error: {e}\n")

    downloader.close()


def example_multiple_downloads():
    """Download multiple files"""
    print("=== Multiple Downloads ===\n")

    downloader = FileDownloader(download_dir="./downloads_example")

    urls = [
        "https://httpbin.org/image/png",
        "https://httpbin.org/image/jpeg",
        "https://httpbin.org/image/webp"
    ]

    filenames = ["image1.png", "image2.jpg", "image3.webp"]

    print(f"Downloading {len(urls)} files...")

    try:
        downloaded = downloader.download_multiple(urls, filenames=filenames, progress=False)
        print(f"Successfully downloaded {len(downloaded)} files\n")

        # Cleanup
        import shutil
        shutil.rmtree("./downloads_example", ignore_errors=True)

    except Exception as e:
        print(f"Error: {e}\n")

    downloader.close()


def example_image_scraping():
    """Image scraping with processing"""
    print("=== Image Scraping ===\n")

    scraper = ImageScraper(
        download_dir="./images_example",
        auto_convert=False
    )

    url = "https://httpbin.org/image/png"
    print(f"Downloading image from {url}...")

    try:
        filepath = scraper.scrape(url, filename="test.png")
        print(f"Downloaded to: {filepath}")

        # Get image metadata
        try:
            metadata = scraper.get_image_metadata(filepath)
            print(f"Image metadata: {metadata}\n")
        except Exception as e:
            print(f"Could not get metadata: {e}\n")

        # Cleanup
        import shutil
        shutil.rmtree("./images_example", ignore_errors=True)

    except Exception as e:
        print(f"Error: {e}\n")

    scraper.close()


def example_rest_api():
    """REST API scraping example"""
    print("=== REST API Scraping ===\n")

    # Using httpbin as example API
    scraper = RESTScraper(
        base_url="https://httpbin.org"
    )

    # GET request
    print("Making GET request to /get...")
    try:
        data = scraper.get_json("/get", params={"key": "value"})
        print(f"Response: {data.get('url')}")
        print(f"Args: {data.get('args')}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # POST request
    print("Making POST request to /post...")
    try:
        data = scraper.post_json(
            "/post",
            json_data={"name": "test", "value": 123}
        )
        print(f"Response URL: {data.get('url')}")
        print(f"JSON data: {data.get('json')}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    scraper.close()


def example_api_with_auth():
    """API scraping with authentication"""
    print("=== API with Authentication ===\n")

    # Example with API key (using httpbin)
    scraper = RESTScraper(
        base_url="https://httpbin.org",
        headers={
            'X-API-Key': 'your-api-key-here'
        }
    )

    print("Making request with API key header...")
    try:
        data = scraper.get_json("/headers")
        headers = data.get('headers', {})
        print(f"Request headers included: {list(headers.keys())[:5]}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    scraper.close()


def example_api_pagination():
    """API pagination example"""
    print("=== API Pagination ===\n")

    scraper = RESTScraper(
        base_url="https://jsonplaceholder.typicode.com"
    )

    print("Fetching paginated data...")

    # Note: This is a demo - jsonplaceholder doesn't actually support pagination
    # In real usage, this would fetch multiple pages
    try:
        # Single page example
        data = scraper.get_json("/posts", params={"_limit": 5})
        print(f"Fetched {len(data)} items")

        if data:
            print(f"First item: {data[0].get('title', 'N/A')[:50]}...\n")

    except Exception as e:
        print(f"Error: {e}\n")

    scraper.close()


def example_api_error_handling():
    """API error handling example"""
    print("=== API Error Handling ===\n")

    scraper = RESTScraper(
        base_url="https://httpbin.org",
        max_retries=3,
        retry_backoff_factor=2.0
    )

    # Test 404 error
    print("Testing 404 error handling...")
    try:
        data = scraper.get_json("/status/404")
        print(f"Data: {data}")
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}\n")

    # Test timeout
    print("Testing timeout (30 second delay - will timeout)...")
    try:
        scraper.timeout = 5  # Set short timeout
        data = scraper.get_json("/delay/30")
        print(f"Data: {data}")
    except Exception as e:
        print(f"Expected timeout error: {type(e).__name__}\n")

    scraper.close()


def example_download_with_custom_settings():
    """File download with custom settings"""
    print("=== Custom Download Settings ===\n")

    downloader = FileDownloader(
        download_dir="./custom_downloads",
        chunk_size=4096,
        verify_mime_type=False,
        timeout=60,
        max_retries=5
    )

    url = "https://httpbin.org/image/png"
    print(f"Downloading with custom settings...")

    try:
        filepath = downloader.scrape(url, progress=False)
        print(f"Downloaded to: {filepath}\n")

        # Cleanup
        import shutil
        shutil.rmtree("./custom_downloads", ignore_errors=True)

    except Exception as e:
        print(f"Error: {e}\n")

    downloader.close()


if __name__ == "__main__":
    print("File Download & API Examples\n" + "=" * 50 + "\n")

    try:
        example_file_download()
        example_multiple_downloads()
        example_image_scraping()
        example_rest_api()
        example_api_with_auth()
        example_api_pagination()
        example_api_error_handling()
        example_download_with_custom_settings()

        print("=" * 50)
        print("All examples completed successfully!")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
