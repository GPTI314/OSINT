"""Notion API Integration - Sync data with Notion databases."""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

import httpx
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class NotionIntegrator:
    """
    Notion API integration:
    - Connect to Notion API
    - Sync lists to Notion databases
    - Create Notion pages
    - Update Notion pages
    - Bidirectional sync
    - Property mapping
    - Error handling
    """

    def __init__(self, db: Session):
        self.db = db
        self.client = httpx.AsyncClient(timeout=30.0)
        self.base_url = "https://api.notion.com/v1"
        self.api_key = None
        self.notion_version = "2022-06-28"

    async def connect(self, api_key: str, database_id: Optional[str] = None) -> Dict[str, Any]:
        """Connect to Notion API."""
        logger.info("Connecting to Notion API")

        try:
            self.api_key = api_key

            # Test connection
            if database_id:
                test_response = await self._test_database_access(database_id)
            else:
                test_response = await self._test_connection()

            return {
                "status": "connected",
                "test_response": test_response
            }

        except Exception as e:
            logger.error(f"Error connecting to Notion: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _test_connection(self) -> Dict[str, Any]:
        """Test Notion API connection."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": self.notion_version
        }

        response = await self.client.get(
            f"{self.base_url}/users/me",
            headers=headers
        )

        response.raise_for_status()
        return response.json()

    async def _test_database_access(self, database_id: str) -> Dict[str, Any]:
        """Test database access."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": self.notion_version
        }

        response = await self.client.get(
            f"{self.base_url}/databases/{database_id}",
            headers=headers
        )

        response.raise_for_status()
        return response.json()

    async def sync_list_to_notion(
        self,
        list_id: int,
        notion_database_id: str,
        property_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Sync list to Notion database."""
        logger.info(f"Syncing list {list_id} to Notion database: {notion_database_id}")

        from lists.list_manager import ListManager

        list_manager = ListManager(self.db)

        # Get list data
        list_data = await list_manager.get_list(list_id, include_items=True)

        sync_results = {
            "list_id": list_id,
            "notion_database_id": notion_database_id,
            "total_items": len(list_data.get("items", [])),
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }

        # Sync each item
        for item in list_data.get("items", []):
            try:
                # Map properties
                notion_properties = self._map_properties(
                    item["item_data"],
                    property_mapping
                )

                # Create page in database
                result = await self.create_notion_page(
                    notion_database_id,
                    notion_properties
                )

                if result.get("id"):
                    sync_results["created"] += 1
                else:
                    sync_results["failed"] += 1
                    sync_results["errors"].append(result.get("error"))

            except Exception as e:
                logger.error(f"Error syncing item {item['id']}: {str(e)}")
                sync_results["failed"] += 1
                sync_results["errors"].append(str(e))

        return sync_results

    def _map_properties(
        self,
        source_data: Dict[str, Any],
        property_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Map source fields to Notion properties."""
        notion_properties = {}

        for source_field, notion_property in property_mapping.items():
            if source_field in source_data:
                value = source_data[source_field]

                # Convert value to Notion property format
                notion_properties[notion_property] = self._convert_to_notion_property(value)

        return notion_properties

    def _convert_to_notion_property(self, value: Any) -> Dict[str, Any]:
        """Convert value to Notion property format."""
        if isinstance(value, str):
            # Text property
            return {
                "rich_text": [
                    {
                        "text": {
                            "content": value
                        }
                    }
                ]
            }
        elif isinstance(value, (int, float)):
            # Number property
            return {
                "number": value
            }
        elif isinstance(value, bool):
            # Checkbox property
            return {
                "checkbox": value
            }
        elif isinstance(value, list):
            # Multi-select property
            return {
                "multi_select": [
                    {"name": str(item)} for item in value
                ]
            }
        else:
            # Default to text
            return {
                "rich_text": [
                    {
                        "text": {
                            "content": str(value)
                        }
                    }
                ]
            }

    async def create_notion_page(
        self,
        database_id: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create page in Notion database."""
        logger.info(f"Creating page in Notion database: {database_id}")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": self.notion_version,
                "Content-Type": "application/json"
            }

            payload = {
                "parent": {
                    "database_id": database_id
                },
                "properties": properties
            }

            response = await self.client.post(
                f"{self.base_url}/pages",
                headers=headers,
                json=payload
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error creating Notion page: {str(e)}")
            return {
                "error": str(e)
            }

    async def update_notion_page(
        self,
        page_id: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update Notion page."""
        logger.info(f"Updating Notion page: {page_id}")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": self.notion_version,
                "Content-Type": "application/json"
            }

            payload = {
                "properties": properties
            }

            response = await self.client.patch(
                f"{self.base_url}/pages/{page_id}",
                headers=headers,
                json=payload
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error updating Notion page: {str(e)}")
            return {
                "error": str(e)
            }

    async def get_notion_page(self, page_id: str) -> Dict[str, Any]:
        """Get Notion page."""
        logger.info(f"Getting Notion page: {page_id}")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": self.notion_version
            }

            response = await self.client.get(
                f"{self.base_url}/pages/{page_id}",
                headers=headers
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error getting Notion page: {str(e)}")
            return {
                "error": str(e)
            }

    async def query_notion_database(
        self,
        database_id: str,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query Notion database."""
        logger.info(f"Querying Notion database: {database_id}")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": self.notion_version,
                "Content-Type": "application/json"
            }

            payload = {}
            if filter_conditions:
                payload["filter"] = filter_conditions

            response = await self.client.post(
                f"{self.base_url}/databases/{database_id}/query",
                headers=headers,
                json=payload
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error querying Notion database: {str(e)}")
            return {
                "error": str(e)
            }

    async def sync_from_notion(
        self,
        database_id: str,
        list_id: int,
        property_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Sync data from Notion to list."""
        logger.info(f"Syncing from Notion database {database_id} to list {list_id}")

        from lists.list_manager import ListManager

        list_manager = ListManager(self.db)

        try:
            # Query database
            notion_data = await self.query_notion_database(database_id)

            pages = notion_data.get("results", [])

            # Map and add to list
            items_to_add = []
            for page in pages:
                # Extract properties
                item_data = self._extract_properties(
                    page.get("properties", {}),
                    property_mapping
                )
                items_to_add.append({"data": item_data})

            # Add to list
            result = await list_manager.add_items(list_id, items_to_add)

            return {
                "status": "success",
                "database_id": database_id,
                "list_id": list_id,
                "pages_synced": len(items_to_add),
                "result": result
            }

        except Exception as e:
            logger.error(f"Error syncing from Notion: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _extract_properties(
        self,
        notion_properties: Dict[str, Any],
        property_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Extract properties from Notion page."""
        list_data = {}

        # Reverse the mapping
        for list_field, notion_property in property_mapping.items():
            if notion_property in notion_properties:
                prop = notion_properties[notion_property]
                value = self._extract_notion_value(prop)
                if value is not None:
                    list_data[list_field] = value

        return list_data

    def _extract_notion_value(self, property_data: Dict[str, Any]) -> Any:
        """Extract value from Notion property."""
        prop_type = property_data.get("type")

        if prop_type == "title":
            title_content = property_data.get("title", [])
            if title_content:
                return title_content[0].get("text", {}).get("content")

        elif prop_type == "rich_text":
            rich_text_content = property_data.get("rich_text", [])
            if rich_text_content:
                return rich_text_content[0].get("text", {}).get("content")

        elif prop_type == "number":
            return property_data.get("number")

        elif prop_type == "checkbox":
            return property_data.get("checkbox")

        elif prop_type == "select":
            select_data = property_data.get("select")
            if select_data:
                return select_data.get("name")

        elif prop_type == "multi_select":
            multi_select_data = property_data.get("multi_select", [])
            return [item.get("name") for item in multi_select_data]

        elif prop_type == "date":
            date_data = property_data.get("date")
            if date_data:
                return date_data.get("start")

        elif prop_type == "url":
            return property_data.get("url")

        elif prop_type == "email":
            return property_data.get("email")

        elif prop_type == "phone_number":
            return property_data.get("phone_number")

        return None

    async def create_notion_database(
        self,
        parent_page_id: str,
        title: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new Notion database."""
        logger.info(f"Creating Notion database: {title}")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": self.notion_version,
                "Content-Type": "application/json"
            }

            payload = {
                "parent": {
                    "type": "page_id",
                    "page_id": parent_page_id
                },
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": title
                        }
                    }
                ],
                "properties": properties
            }

            response = await self.client.post(
                f"{self.base_url}/databases",
                headers=headers,
                json=payload
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error creating Notion database: {str(e)}")
            return {
                "error": str(e)
            }

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
