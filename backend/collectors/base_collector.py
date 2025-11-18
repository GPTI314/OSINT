"""
Base collector class for OSINT operations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """
    Abstract base class for OSINT collectors.

    All collectors should inherit from this class and implement the collect method.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the collector.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.results = []
        self.errors = []

    @abstractmethod
    async def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect OSINT data for the given target.

        Args:
            target: Target identifier (domain, IP, email, etc.)
            **kwargs: Additional collector-specific parameters

        Returns:
            Dict containing collected data
        """
        pass

    def add_result(self, source: str, data: Dict[str, Any], confidence: float = 1.0):
        """
        Add a result to the collection.

        Args:
            source: Data source name
            data: Collected data
            confidence: Confidence score (0.0 to 1.0)
        """
        self.results.append({
            "source": source,
            "data": data,
            "confidence": confidence,
            "collected_at": datetime.utcnow().isoformat()
        })

    def add_error(self, source: str, error: str):
        """
        Add an error to the collection.

        Args:
            source: Data source name
            error: Error message
        """
        logger.error(f"Error in {source}: {error}")
        self.errors.append({
            "source": source,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of collection results.

        Returns:
            Dict containing collection summary
        """
        return {
            "total_results": len(self.results),
            "total_errors": len(self.errors),
            "sources": list(set(r["source"] for r in self.results)),
            "average_confidence": sum(r["confidence"] for r in self.results) / len(self.results) if self.results else 0.0
        }
