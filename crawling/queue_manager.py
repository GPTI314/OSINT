"""URL queue management for crawling."""

from typing import Dict, Any, Optional
from collections import deque
from loguru import logger


class QueueManager:
    """
    URL queue manager for crawling.

    Features:
    - Priority queue support
    - FIFO/LIFO ordering
    - URL deduplication
    - Queue persistence
    """

    def __init__(self, queue_type: str = "fifo"):
        """
        Initialize queue manager.

        Args:
            queue_type: Type of queue (fifo, lifo, priority)
        """
        self.queue_type = queue_type
        self.queue = deque()
        self.seen_urls = set()

        logger.info(f"Queue manager initialized (type: {queue_type})")

    def add_url(self, url: str, depth: int = 0, priority: int = 0):
        """
        Add URL to the queue.

        Args:
            url: URL to add
            depth: Crawl depth
            priority: Priority level (higher = more important)
        """
        if url in self.seen_urls:
            return

        self.seen_urls.add(url)
        url_info = {
            "url": url,
            "depth": depth,
            "priority": priority,
        }

        if self.queue_type == "priority":
            # Insert based on priority
            inserted = False
            for i, item in enumerate(self.queue):
                if priority > item.get("priority", 0):
                    self.queue.insert(i, url_info)
                    inserted = True
                    break
            if not inserted:
                self.queue.append(url_info)
        else:
            self.queue.append(url_info)

    def get_next_url(self) -> Optional[Dict[str, Any]]:
        """
        Get next URL from the queue.

        Returns:
            URL info dictionary or None
        """
        if not self.queue:
            return None

        if self.queue_type == "lifo":
            return self.queue.pop()
        else:  # fifo or priority
            return self.queue.popleft()

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self.queue) == 0

    def size(self) -> int:
        """Get queue size."""
        return len(self.queue)

    def clear(self):
        """Clear the queue."""
        self.queue.clear()
        self.seen_urls.clear()
        logger.info("Queue cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "queue_size": len(self.queue),
            "seen_urls": len(self.seen_urls),
            "queue_type": self.queue_type,
        }
