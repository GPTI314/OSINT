"""
Base classes for OSINT modules
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging


class BaseModule(ABC):
    """Base class for all OSINT modules"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the module

        Args:
            config: Configuration dictionary for the module
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    @abstractmethod
    def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect intelligence on the target

        Args:
            target: The target to investigate
            **kwargs: Additional parameters

        Returns:
            Dictionary containing collected intelligence
        """
        pass

    def _create_result(self,
                      target: str,
                      data: Dict[str, Any],
                      success: bool = True,
                      error: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a standardized result dictionary

        Args:
            target: The target that was investigated
            data: The collected data
            success: Whether the collection was successful
            error: Error message if any

        Returns:
            Standardized result dictionary
        """
        return {
            "target": target,
            "timestamp": datetime.utcnow().isoformat(),
            "module": self.__class__.__name__,
            "success": success,
            "data": data,
            "error": error
        }

    def _handle_error(self, target: str, error: Exception) -> Dict[str, Any]:
        """
        Handle errors and create error result

        Args:
            target: The target that was being investigated
            error: The exception that occurred

        Returns:
            Error result dictionary
        """
        self.logger.error(f"Error processing {target}: {str(error)}")
        return self._create_result(
            target=target,
            data={},
            success=False,
            error=str(error)
        )


class DataEnricher(ABC):
    """Base class for data enrichment"""

    @abstractmethod
    def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich the provided data

        Args:
            data: Raw data to enrich

        Returns:
            Enriched data
        """
        pass


class ThreatIntelligence(ABC):
    """Base class for threat intelligence providers"""

    @abstractmethod
    def check_reputation(self, indicator: str) -> Dict[str, Any]:
        """
        Check the reputation of an indicator

        Args:
            indicator: The indicator to check (domain, IP, hash, etc.)

        Returns:
            Reputation data
        """
        pass
