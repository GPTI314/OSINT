"""
SQL database storage backend
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import uuid
from sqlalchemy import create_engine, Column, String, Text, DateTime, Table, MetaData
from sqlalchemy.orm import sessionmaker
from .base import StorageBackend


class SQLStorage(StorageBackend):
    """SQL database storage using SQLAlchemy"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.connection_string = self.config.get('connection_string', 'sqlite:///osint_data.db')
        self.engine = None
        self.Session = None
        self.metadata = MetaData()

    def connect(self):
        """Connect to SQL database"""
        self.engine = create_engine(self.connection_string)
        self.Session = sessionmaker(bind=self.engine)
        self.metadata.create_all(self.engine)

    def disconnect(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()

    def _get_or_create_table(self, collection: str):
        """Get or create table for collection"""
        if collection not in self.metadata.tables:
            table = Table(
                collection,
                self.metadata,
                Column('id', String(36), primary_key=True),
                Column('data', Text),
                Column('created_at', DateTime),
                Column('updated_at', DateTime),
                extend_existing=True
            )
            self.metadata.create_all(self.engine)
            return table
        return self.metadata.tables[collection]

    def store(self, data: Dict[str, Any], collection: str = 'default') -> str:
        """Store data to SQL table"""
        if not self.engine:
            self.connect()

        table = self._get_or_create_table(collection)
        data_id = str(uuid.uuid4())
        now = datetime.utcnow()

        with self.engine.connect() as conn:
            conn.execute(
                table.insert().values(
                    id=data_id,
                    data=json.dumps(data),
                    created_at=now,
                    updated_at=now
                )
            )
            conn.commit()

        return data_id

    def store_batch(self, data_list: List[Dict[str, Any]], collection: str = 'default') -> List[str]:
        """Store multiple data items"""
        if not self.engine:
            self.connect()

        table = self._get_or_create_table(collection)
        ids = []
        now = datetime.utcnow()

        with self.engine.connect() as conn:
            for data in data_list:
                data_id = str(uuid.uuid4())
                ids.append(data_id)
                conn.execute(
                    table.insert().values(
                        id=data_id,
                        data=json.dumps(data),
                        created_at=now,
                        updated_at=now
                    )
                )
            conn.commit()

        return ids

    def retrieve(self, id: str, collection: str = 'default') -> Optional[Dict[str, Any]]:
        """Retrieve data by ID"""
        if not self.engine:
            self.connect()

        table = self._get_or_create_table(collection)

        with self.engine.connect() as conn:
            result = conn.execute(
                table.select().where(table.c.id == id)
            ).fetchone()

        if result:
            return json.loads(result.data)
        return None

    def query(self, filters: Dict[str, Any], collection: str = 'default') -> List[Dict[str, Any]]:
        """Query data with filters"""
        if not self.engine:
            self.connect()

        table = self._get_or_create_table(collection)

        with self.engine.connect() as conn:
            results = conn.execute(table.select()).fetchall()

        # Filter in memory (basic implementation)
        filtered = []
        for result in results:
            data = json.loads(result.data)
            match = all(data.get(k) == v for k, v in filters.items())
            if match:
                filtered.append(data)

        return filtered

    def delete(self, id: str, collection: str = 'default') -> bool:
        """Delete data by ID"""
        if not self.engine:
            self.connect()

        table = self._get_or_create_table(collection)

        with self.engine.connect() as conn:
            result = conn.execute(
                table.delete().where(table.c.id == id)
            )
            conn.commit()

        return result.rowcount > 0

    def update(self, id: str, data: Dict[str, Any], collection: str = 'default') -> bool:
        """Update data by ID"""
        if not self.engine:
            self.connect()

        table = self._get_or_create_table(collection)

        with self.engine.connect() as conn:
            result = conn.execute(
                table.update().where(table.c.id == id).values(
                    data=json.dumps(data),
                    updated_at=datetime.utcnow()
                )
            )
            conn.commit()

        return result.rowcount > 0
