"""
Base storage backend interface
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class StorageBackend(ABC):
    """Abstract base class for storage backends"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    def connect(self):
        """Establish connection to storage backend"""
        pass

    @abstractmethod
    def disconnect(self):
        """Close connection to storage backend"""
        pass

    @abstractmethod
    def store(self, data: Dict[str, Any], collection: str = 'default') -> str:
        """
        Store data

        Args:
            data: Data to store
            collection: Collection/table name

        Returns:
            ID of stored data
        """
        pass

    @abstractmethod
    def store_batch(self, data_list: List[Dict[str, Any]], collection: str = 'default') -> List[str]:
        """
        Store multiple data items

        Args:
            data_list: List of data to store
            collection: Collection/table name

        Returns:
            List of IDs of stored data
        """
        pass

    @abstractmethod
    def retrieve(self, id: str, collection: str = 'default') -> Optional[Dict[str, Any]]:
        """
        Retrieve data by ID

        Args:
            id: Data ID
            collection: Collection/table name

        Returns:
            Retrieved data or None
        """
        pass

    @abstractmethod
    def query(self, filters: Dict[str, Any], collection: str = 'default') -> List[Dict[str, Any]]:
        """
        Query data with filters

        Args:
            filters: Query filters
            collection: Collection/table name

        Returns:
            List of matching data
        """
        pass

    @abstractmethod
    def delete(self, id: str, collection: str = 'default') -> bool:
        """
        Delete data by ID

        Args:
            id: Data ID
            collection: Collection/table name

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def update(self, id: str, data: Dict[str, Any], collection: str = 'default') -> bool:
        """
        Update data by ID

        Args:
            id: Data ID
            data: Updated data
            collection: Collection/table name

        Returns:
            True if successful
        """
        pass
