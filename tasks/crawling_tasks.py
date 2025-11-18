"""Celery tasks for crawling operations."""

from loguru import logger
from typing import Dict, Any

from .celery_app import celery_app
from crawling.engine import CrawlingEngine


@celery_app.task(name="tasks.crawling_tasks.crawl_website")
def crawl_website(
    start_url: str,
    config: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Crawl a website starting from a seed URL.

    Args:
        start_url: Starting URL for crawl
        config: Crawler configuration

    Returns:
        Crawling results
    """
    try:
        logger.info(f"Starting crawling task: {start_url}")

        # Initialize crawler
        crawler = CrawlingEngine(config or {})

        # Run crawl
        import asyncio
        result = asyncio.run(crawler.crawl(start_url))

        logger.info(f"Crawling task completed: {start_url}")
        return result

    except Exception as e:
        logger.error(f"Crawling task failed: {start_url} - {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "start_url": start_url,
        }
