"""
JSON data extractor with JSONPath and schema validation
"""
from typing import Any, Dict, List, Optional, Union
from jsonpath_ng import parse
from jsonschema import validate, ValidationError, Draft7Validator
import json
from datetime import datetime


class JSONExtractor:
    """Extract and validate JSON data"""

    def __init__(self):
        """Initialize JSON extractor"""
        pass

    def extract(self, source: Union[str, dict, bytes], **kwargs) -> Dict[str, Any]:
        """
        Extract data from JSON source

        Args:
            source: JSON string, dict, or bytes
            **kwargs: Additional extraction options

        Returns:
            Extracted data dictionary
        """
        # Parse JSON if needed
        if isinstance(source, (str, bytes)):
            data = json.loads(source)
        else:
            data = source

        extracted_data = {
            'source_type': 'json',
            'extracted_at': datetime.utcnow().isoformat(),
            'data': data,
            'metadata': self.extract_metadata(data),
            'custom_data': {}
        }

        # Apply JSONPath queries if provided
        if 'jsonpath_queries' in kwargs:
            extracted_data['custom_data']['jsonpath'] = self.extract_with_jsonpath(
                data, kwargs['jsonpath_queries']
            )

        # Validate against schema if provided
        if 'schema' in kwargs:
            validation_result = self.validate_schema(data, kwargs['schema'])
            extracted_data['schema_validation'] = validation_result

        return extracted_data

    def extract_metadata(self, data: Union[Dict, List]) -> Dict[str, Any]:
        """
        Extract metadata from JSON data

        Args:
            data: JSON data

        Returns:
            Metadata dictionary
        """
        metadata = {
            'type': type(data).__name__,
            'size': self._get_size(data),
            'depth': self._get_depth(data)
        }

        if isinstance(data, dict):
            metadata['keys'] = list(data.keys())
            metadata['key_count'] = len(data.keys())
        elif isinstance(data, list):
            metadata['length'] = len(data)
            if data:
                metadata['item_type'] = type(data[0]).__name__

        return metadata

    def _get_size(self, data: Any) -> int:
        """Calculate size of JSON data in bytes"""
        return len(json.dumps(data))

    def _get_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate maximum depth of nested JSON structure"""
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(self._get_depth(v, current_depth + 1) for v in data.values())
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(self._get_depth(item, current_depth + 1) for item in data)
        else:
            return current_depth

    def extract_with_jsonpath(self, data: Union[Dict, List], queries: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract data using JSONPath queries

        Args:
            data: JSON data
            queries: Dictionary mapping field names to JSONPath queries

        Returns:
            Extracted data dictionary
        """
        results = {}

        for field_name, query in queries.items():
            try:
                jsonpath_expr = parse(query)
                matches = [match.value for match in jsonpath_expr.find(data)]

                if len(matches) == 1:
                    results[field_name] = matches[0]
                elif len(matches) > 1:
                    results[field_name] = matches
                else:
                    results[field_name] = None

            except Exception as e:
                results[field_name] = f"Error: {str(e)}"

        return results

    def validate_schema(self, data: Union[Dict, List], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate JSON data against JSON Schema

        Args:
            data: JSON data to validate
            schema: JSON Schema

        Returns:
            Validation result dictionary
        """
        result = {
            'valid': False,
            'errors': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            validate(instance=data, schema=schema)
            result['valid'] = True
        except ValidationError as e:
            result['valid'] = False
            result['errors'].append({
                'message': e.message,
                'path': list(e.path),
                'validator': e.validator
            })

        # Get all validation errors
        validator = Draft7Validator(schema)
        all_errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

        for error in all_errors:
            if not any(err['message'] == error.message for err in result['errors']):
                result['errors'].append({
                    'message': error.message,
                    'path': list(error.path),
                    'validator': error.validator
                })

        return result

    def flatten_json(self, data: Union[Dict, List], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """
        Flatten nested JSON structure

        Args:
            data: JSON data to flatten
            parent_key: Parent key for recursion
            sep: Separator for nested keys

        Returns:
            Flattened dictionary
        """
        items = []

        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}{sep}{key}" if parent_key else key

                if isinstance(value, (dict, list)):
                    items.extend(self.flatten_json(value, new_key, sep).items())
                else:
                    items.append((new_key, value))

        elif isinstance(data, list):
            for idx, value in enumerate(data):
                new_key = f"{parent_key}[{idx}]"

                if isinstance(value, (dict, list)):
                    items.extend(self.flatten_json(value, new_key, sep).items())
                else:
                    items.append((new_key, value))

        return dict(items)

    def extract_arrays(self, data: Union[Dict, List]) -> Dict[str, List]:
        """
        Extract all arrays from JSON data

        Args:
            data: JSON data

        Returns:
            Dictionary mapping paths to arrays
        """
        arrays = {}

        def extract_recursive(obj, path=''):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    extract_recursive(value, new_path)
            elif isinstance(obj, list):
                arrays[path] = obj
                for idx, item in enumerate(obj):
                    extract_recursive(item, f"{path}[{idx}]")

        extract_recursive(data)
        return arrays

    def transform_json(self, data: Union[Dict, List], transformations: Dict[str, Any]) -> Union[Dict, List]:
        """
        Transform JSON data based on transformation rules

        Args:
            data: JSON data to transform
            transformations: Transformation rules

        Returns:
            Transformed data
        """
        # Simple transformation implementation
        # Can be extended with more complex rules

        if 'rename_keys' in transformations:
            if isinstance(data, dict):
                for old_key, new_key in transformations['rename_keys'].items():
                    if old_key in data:
                        data[new_key] = data.pop(old_key)

        if 'remove_keys' in transformations:
            if isinstance(data, dict):
                for key in transformations['remove_keys']:
                    data.pop(key, None)

        if 'add_fields' in transformations:
            if isinstance(data, dict):
                data.update(transformations['add_fields'])

        return data
