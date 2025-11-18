"""
Main ETL Pipeline orchestrator
"""
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import logging
from .processor import DataProcessor
from .validators import DataValidator
from .enricher import DataEnricher
from ..storage.base import StorageBackend
from ..storage.file_storage import FileStorage


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """
    Main ETL Pipeline for OSINT data processing

    Orchestrates the complete data flow:
    1. Extraction - from various sources
    2. Transformation - normalize and transform data
    3. Validation - quality checks
    4. Enrichment - add context and analysis
    5. Storage - persist to database
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.processor = DataProcessor()
        self.validator = DataValidator()
        self.enricher = DataEnricher()
        self.storage: Optional[StorageBackend] = None
        self.extractors = {}
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }

    def set_storage(self, storage: StorageBackend):
        """
        Set storage backend

        Args:
            storage: StorageBackend instance
        """
        self.storage = storage
        self.storage.connect()

    def register_extractor(self, name: str, extractor: Any):
        """
        Register a data extractor

        Args:
            name: Extractor name
            extractor: Extractor instance
        """
        self.extractors[name] = extractor
        logger.info(f"Registered extractor: {name}")

    def register_enricher(self, name: str, enricher: Any):
        """
        Register an enricher

        Args:
            name: Enricher name
            enricher: Enricher instance
        """
        self.enricher.register_enricher(enricher, name)
        logger.info(f"Registered enricher: {name}")

    def extract(self, source: Any, extractor_name: str, **kwargs) -> Dict[str, Any]:
        """
        Extract data from source

        Args:
            source: Data source (file, URL, text, etc.)
            extractor_name: Name of registered extractor
            **kwargs: Additional arguments for extractor

        Returns:
            Extracted data
        """
        if extractor_name not in self.extractors:
            raise ValueError(f"Extractor '{extractor_name}' not registered")

        extractor = self.extractors[extractor_name]
        logger.info(f"Extracting data using {extractor_name}")

        try:
            extracted_data = extractor.extract(source, **kwargs)
            extracted_data['extraction'] = {
                'extractor': extractor_name,
                'timestamp': datetime.utcnow().isoformat(),
                'source': str(source)[:200]  # Truncate for logging
            }
            return extracted_data
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform and normalize data

        Args:
            data: Raw extracted data

        Returns:
            Transformed data
        """
        logger.info("Transforming data")

        # Apply custom transformations
        transformed = self.processor.transform(data)

        # Normalize data
        normalized = self.processor.normalize(transformed)

        # Extract metadata
        metadata = self.processor.extract_metadata(data)
        normalized['metadata'] = metadata

        return normalized

    def validate(self, data: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """
        Validate data quality

        Args:
            data: Data to validate

        Returns:
            Tuple of (is_valid, validation_report)
        """
        logger.info("Validating data")

        is_valid, errors = self.validator.validate(data)
        quality_report = self.validator.quality_check(data)

        validation_report = {
            'is_valid': is_valid,
            'errors': errors,
            'quality': quality_report,
            'timestamp': datetime.utcnow().isoformat()
        }

        return (is_valid, validation_report)

    def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich data with additional context

        Args:
            data: Data to enrich

        Returns:
            Enriched data
        """
        logger.info("Enriching data")
        return self.enricher.enrich(data)

    def store_data(self, data: Dict[str, Any], collection: str = 'default') -> str:
        """
        Store data to backend

        Args:
            data: Data to store
            collection: Collection/table name

        Returns:
            Stored data ID
        """
        if not self.storage:
            # Use default file storage
            self.storage = FileStorage(self.config.get('storage', {}).get('file', {}))
            self.storage.connect()

        logger.info(f"Storing data to collection: {collection}")
        return self.storage.store(data, collection)

    def process(self, source: Any, extractor_name: str, collection: str = 'default',
                validate_data: bool = True, enrich_data: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Process data through complete ETL pipeline

        Args:
            source: Data source
            extractor_name: Extractor to use
            collection: Storage collection
            validate_data: Whether to validate data
            enrich_data: Whether to enrich data
            **kwargs: Additional extractor arguments

        Returns:
            Processing result with metadata
        """
        self.stats['total_processed'] += 1

        try:
            # Extract
            data = self.extract(source, extractor_name, **kwargs)

            # Transform
            data = self.transform(data)

            # Validate
            if validate_data:
                is_valid, validation_report = self.validate(data.get('data', {}))
                data['validation'] = validation_report

                if not is_valid and self.config.get('strict_validation', False):
                    raise ValueError("Data validation failed")

            # Enrich
            if enrich_data:
                data = self.enrich(data)

            # Store
            data_id = self.store_data(data, collection)
            data['storage'] = {
                'id': data_id,
                'collection': collection,
                'timestamp': datetime.utcnow().isoformat()
            }

            self.stats['successful'] += 1
            logger.info(f"Successfully processed data with ID: {data_id}")

            return {
                'success': True,
                'data_id': data_id,
                'data': data
            }

        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"Processing failed: {str(e)}")

            return {
                'success': False,
                'error': str(e),
                'source': str(source)[:200]
            }

    def process_batch(self, sources: List[Any], extractor_name: str, collection: str = 'default',
                     validate_data: bool = True, enrich_data: bool = True, **kwargs) -> List[Dict[str, Any]]:
        """
        Process multiple sources in batch

        Args:
            sources: List of data sources
            extractor_name: Extractor to use
            collection: Storage collection
            validate_data: Whether to validate data
            enrich_data: Whether to enrich data
            **kwargs: Additional extractor arguments

        Returns:
            List of processing results
        """
        self.stats['start_time'] = datetime.utcnow().isoformat()

        results = []
        for source in sources:
            result = self.process(source, extractor_name, collection, validate_data, enrich_data, **kwargs)
            results.append(result)

        self.stats['end_time'] = datetime.utcnow().isoformat()

        return results

    def get_stats(self) -> Dict[str, Any]:
        """
        Get pipeline statistics

        Returns:
            Statistics dictionary
        """
        return self.stats.copy()

    def reset_stats(self):
        """Reset pipeline statistics"""
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }
