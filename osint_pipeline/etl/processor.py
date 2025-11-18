"""
Data processor for transformation and normalization
"""
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import re
from ..utils.helpers import normalize_data, sanitize_text, extract_urls, extract_emails


class DataProcessor:
    """Data transformation and normalization processor"""

    def __init__(self):
        self.transformations: List[Callable] = []
        self.metadata = {}

    def add_transformation(self, transform_func: Callable):
        """
        Add a transformation function

        Args:
            transform_func: Function that takes data dict and returns transformed data dict
        """
        self.transformations.append(transform_func)

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all transformations to data

        Args:
            data: Input data

        Returns:
            Transformed data
        """
        transformed = data.copy()

        for transform_func in self.transformations:
            try:
                transformed = transform_func(transformed)
            except Exception as e:
                transformed['transformation_errors'] = transformed.get('transformation_errors', [])
                transformed['transformation_errors'].append({
                    'function': transform_func.__name__,
                    'error': str(e)
                })

        return transformed

    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize data structure and values

        Args:
            data: Input data

        Returns:
            Normalized data
        """
        normalized = {
            'normalized_at': datetime.utcnow().isoformat(),
            'data': {}
        }

        for key, value in data.items():
            # Skip metadata fields
            if key in ['normalized_at', 'extracted_at', 'enrichment']:
                normalized[key] = value
                continue

            # Normalize values
            if isinstance(value, str):
                normalized['data'][key] = sanitize_text(value, remove_html=False)
            elif isinstance(value, (list, dict)):
                normalized['data'][key] = normalize_data(value)
            else:
                normalized['data'][key] = value

        return normalized

    def extract_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from data

        Args:
            data: Input data

        Returns:
            Metadata dictionary
        """
        metadata = {
            'extracted_at': datetime.utcnow().isoformat(),
            'field_count': len(data),
            'data_types': {}
        }

        # Analyze data types
        for key, value in data.items():
            metadata['data_types'][key] = type(value).__name__

        # Extract text-based metadata
        text_fields = [v for v in data.values() if isinstance(v, str)]
        combined_text = ' '.join(text_fields)

        metadata['urls'] = extract_urls(combined_text)
        metadata['emails'] = extract_emails(combined_text)
        metadata['text_length'] = len(combined_text)

        return metadata

    def deduplicate(self, data_list: List[Dict[str, Any]], key: str = 'id') -> List[Dict[str, Any]]:
        """
        Remove duplicate entries from data list

        Args:
            data_list: List of data dictionaries
            key: Key to use for deduplication

        Returns:
            Deduplicated list
        """
        seen = set()
        deduped = []

        for data in data_list:
            data_key = data.get(key)
            if data_key and data_key not in seen:
                seen.add(data_key)
                deduped.append(data)
            elif not data_key:
                # If no key, always include
                deduped.append(data)

        return deduped

    def merge_data(self, *data_dicts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge multiple data dictionaries

        Args:
            *data_dicts: Variable number of data dictionaries

        Returns:
            Merged dictionary
        """
        merged = {}

        for data in data_dicts:
            for key, value in data.items():
                if key in merged:
                    # Handle conflicts
                    if isinstance(merged[key], list) and isinstance(value, list):
                        merged[key].extend(value)
                    elif isinstance(merged[key], dict) and isinstance(value, dict):
                        merged[key].update(value)
                    else:
                        # Keep newer value
                        merged[key] = value
                else:
                    merged[key] = value

        return merged

    def filter_data(self, data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Check if data matches filters

        Args:
            data: Data to filter
            filters: Filter criteria

        Returns:
            True if data matches all filters
        """
        for key, value in filters.items():
            if key not in data:
                return False

            data_value = data[key]

            # Handle different filter types
            if callable(value):
                if not value(data_value):
                    return False
            elif isinstance(value, (list, tuple)):
                if data_value not in value:
                    return False
            elif data_value != value:
                return False

        return True

    def aggregate_data(self, data_list: List[Dict[str, Any]], group_by: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Aggregate data by a specific field

        Args:
            data_list: List of data dictionaries
            group_by: Field to group by

        Returns:
            Dictionary of grouped data
        """
        aggregated = {}

        for data in data_list:
            group_key = data.get(group_by, 'unknown')

            if group_key not in aggregated:
                aggregated[group_key] = []

            aggregated[group_key].append(data)

        return aggregated
