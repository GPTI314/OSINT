"""Celery tasks for scraping operations."""

from celery import Task
from loguru import logger
from typing import Dict, Any

from .celery_app import celery_app
from scraping.engine import ScrapingEngine


class ScrapingTask(Task):
    """Base scraping task with engine initialization."""

    def __init__(self):
        self._engine = None

    @property
    def engine(self):
        if self._engine is None:
            self._engine = ScrapingEngine()
        return self._engine


@celery_app.task(bind=True, base=ScrapingTask, name="tasks.scraping_tasks.scrape_url")
def scrape_url(
    self,
    url: str,
    scraper_type: str = "static",
    config: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Scrape a URL using specified scraper type.

    Args:
        url: URL to scrape
        scraper_type: Type of scraper (static, dynamic, api)
        config: Scraper configuration

    Returns:
        Scraping results
    """
    try:
        logger.info(f"Starting scraping task: {url}")

        # Run scraping
        import asyncio
        result = asyncio.run(
            self.engine.scrape(url, scraper_type, config or {})
        )

        logger.info(f"Scraping task completed: {url}")
        return result

    except Exception as e:
        logger.error(f"Scraping task failed: {url} - {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "url": url,
        }


@celery_app.task(bind=True, base=ScrapingTask, name="tasks.scraping_tasks.scrape_batch")
def scrape_batch(
    self,
    urls: list,
    scraper_type: str = "static",
    config: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Scrape multiple URLs in batch.

    Args:
        urls: List of URLs to scrape
        scraper_type: Type of scraper
        config: Scraper configuration

    Returns:
        Batch scraping results
    """
    try:
        logger.info(f"Starting batch scraping task: {len(urls)} URLs")

        # Run batch scraping
        import asyncio
        results = asyncio.run(
            self.engine.scrape_batch(urls, scraper_type, config or {})
        )

        logger.info(f"Batch scraping completed: {len(urls)} URLs")
        return {
            "success": True,
            "results": results,
            "total": len(urls),
        }

    except Exception as e:
        logger.error(f"Batch scraping failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "urls": urls,
        }


@celery_app.task(name="tasks.scraping_tasks.cleanup_old_jobs")
def cleanup_old_jobs():
    """Clean up old scraping jobs (periodic task)."""
    try:
        logger.info("Running cleanup of old scraping jobs")
        # Implementation would clean up old database records
        # This is a placeholder for the periodic task
        return {"success": True, "cleaned": 0}
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        return {"success": False, "error": str(e)}
