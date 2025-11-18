"""
MongoDB storage backend
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from .base import StorageBackend


class MongoStorage(StorageBackend):
    """MongoDB storage backend"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.host = self.config.get('host', 'localhost')
        self.port = self.config.get('port', 27017)
        self.database = self.config.get('database', 'osint')
        self.client = None
        self.db = None

    def connect(self):
        """Connect to MongoDB"""
        self.client = MongoClient(self.host, self.port)
        self.db = self.client[self.database]

    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

    def store(self, data: Dict[str, Any], collection: str = 'default') -> str:
        """Store data to MongoDB collection"""
        if not self.client:
            self.connect()

        coll = self.db[collection]
        data_with_timestamp = {
            **data,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        result = coll.insert_one(data_with_timestamp)
        return str(result.inserted_id)

    def store_batch(self, data_list: List[Dict[str, Any]], collection: str = 'default') -> List[str]:
        """Store multiple data items"""
        if not self.client:
            self.connect()

        coll = self.db[collection]
        now = datetime.utcnow()

        data_with_timestamps = [
            {**data, 'created_at': now, 'updated_at': now}
            for data in data_list
        ]

        result = coll.insert_many(data_with_timestamps)
        return [str(id) for id in result.inserted_ids]

    def retrieve(self, id: str, collection: str = 'default') -> Optional[Dict[str, Any]]:
        """Retrieve data by ID"""
        if not self.client:
            self.connect()

        coll = self.db[collection]
        result = coll.find_one({'_id': ObjectId(id)})

        if result:
            result['id'] = str(result.pop('_id'))
            return result

        return None

    def query(self, filters: Dict[str, Any], collection: str = 'default') -> List[Dict[str, Any]]:
        """Query data with filters"""
        if not self.client:
            self.connect()

        coll = self.db[collection]
        results = list(coll.find(filters))

        for result in results:
            result['id'] = str(result.pop('_id'))

        return results

    def delete(self, id: str, collection: str = 'default') -> bool:
        """Delete data by ID"""
        if not self.client:
            self.connect()

        coll = self.db[collection]
        result = coll.delete_one({'_id': ObjectId(id)})

        return result.deleted_count > 0

    def update(self, id: str, data: Dict[str, Any], collection: str = 'default') -> bool:
        """Update data by ID"""
        if not self.client:
            self.connect()

        coll = self.db[collection]
        data_with_timestamp = {
            **data,
            'updated_at': datetime.utcnow()
        }

        result = coll.update_one(
            {'_id': ObjectId(id)},
            {'$set': data_with_timestamp}
        )

        return result.modified_count > 0
