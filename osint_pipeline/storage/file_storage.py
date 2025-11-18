"""
File-based storage backend
"""
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid
from .base import StorageBackend


class FileStorage(StorageBackend):
    """File-based storage using JSON files"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.output_dir = self.config.get('output_dir', './output')
        self.connected = False

    def connect(self):
        """Create output directory if it doesn't exist"""
        os.makedirs(self.output_dir, exist_ok=True)
        self.connected = True

    def disconnect(self):
        """No-op for file storage"""
        self.connected = False

    def store(self, data: Dict[str, Any], collection: str = 'default') -> str:
        """Store data to JSON file"""
        if not self.connected:
            self.connect()

        # Generate unique ID
        data_id = str(uuid.uuid4())
        data_with_id = {
            'id': data_id,
            'collection': collection,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }

        # Create collection directory
        collection_dir = os.path.join(self.output_dir, collection)
        os.makedirs(collection_dir, exist_ok=True)

        # Write to file
        file_path = os.path.join(collection_dir, f"{data_id}.json")
        with open(file_path, 'w') as f:
            json.dump(data_with_id, f, indent=2)

        return data_id

    def store_batch(self, data_list: List[Dict[str, Any]], collection: str = 'default') -> List[str]:
        """Store multiple data items"""
        return [self.store(data, collection) for data in data_list]

    def retrieve(self, id: str, collection: str = 'default') -> Optional[Dict[str, Any]]:
        """Retrieve data by ID"""
        file_path = os.path.join(self.output_dir, collection, f"{id}.json")

        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r') as f:
            data_with_id = json.load(f)

        return data_with_id.get('data')

    def query(self, filters: Dict[str, Any], collection: str = 'default') -> List[Dict[str, Any]]:
        """Query data with filters"""
        collection_dir = os.path.join(self.output_dir, collection)

        if not os.path.exists(collection_dir):
            return []

        results = []
        for filename in os.listdir(collection_dir):
            if not filename.endswith('.json'):
                continue

            file_path = os.path.join(collection_dir, filename)
            with open(file_path, 'r') as f:
                data_with_id = json.load(f)

            data = data_with_id.get('data', {})

            # Simple filter matching
            match = all(data.get(k) == v for k, v in filters.items())
            if match:
                results.append(data)

        return results

    def delete(self, id: str, collection: str = 'default') -> bool:
        """Delete data by ID"""
        file_path = os.path.join(self.output_dir, collection, f"{id}.json")

        if not os.path.exists(file_path):
            return False

        os.remove(file_path)
        return True

    def update(self, id: str, data: Dict[str, Any], collection: str = 'default') -> bool:
        """Update data by ID"""
        file_path = os.path.join(self.output_dir, collection, f"{id}.json")

        if not os.path.exists(file_path):
            return False

        with open(file_path, 'r') as f:
            data_with_id = json.load(f)

        data_with_id['data'] = data
        data_with_id['updated_at'] = datetime.utcnow().isoformat()

        with open(file_path, 'w') as f:
            json.dump(data_with_id, f, indent=2)

        return True
