"""Zoho CRM/API Integration - Sync data with Zoho CRM."""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

import httpx
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ZohoIntegrator:
    """
    Zoho CRM/API integration:
    - Connect to Zoho API
    - Sync lists to Zoho modules
    - Create records in Zoho
    - Update records in Zoho
    - Bidirectional sync
    - Field mapping
    - Error handling
    """

    def __init__(self, db: Session):
        self.db = db
        self.client = httpx.AsyncClient(timeout=30.0)
        self.base_url = "https://www.zohoapis.com/crm/v2"
        self.access_token = None

    async def connect(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Connect to Zoho API."""
        logger.info("Connecting to Zoho API")

        try:
            # In production, implement OAuth2 flow
            # For now, assume credentials contain access_token
            self.access_token = credentials.get("access_token")

            if not self.access_token:
                # Refresh token flow
                refresh_token = credentials.get("refresh_token")
                client_id = credentials.get("client_id")
                client_secret = credentials.get("client_secret")

                if not all([refresh_token, client_id, client_secret]):
                    raise ValueError("Missing Zoho credentials")

                # Request new access token
                token_response = await self._refresh_access_token(
                    refresh_token, client_id, client_secret
                )

                self.access_token = token_response.get("access_token")

            # Test connection
            test_response = await self._test_connection()

            return {
                "status": "connected",
                "test_response": test_response
            }

        except Exception as e:
            logger.error(f"Error connecting to Zoho: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _refresh_access_token(
        self,
        refresh_token: str,
        client_id: str,
        client_secret: str
    ) -> Dict[str, Any]:
        """Refresh Zoho access token."""
        token_url = "https://accounts.zoho.com/oauth/v2/token"

        data = {
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token"
        }

        response = await self.client.post(token_url, data=data)
        response.raise_for_status()

        return response.json()

    async def _test_connection(self) -> Dict[str, Any]:
        """Test Zoho API connection."""
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}"
        }

        response = await self.client.get(
            f"{self.base_url}/org",
            headers=headers
        )

        response.raise_for_status()
        return response.json()

    async def sync_list_to_zoho(
        self,
        list_id: int,
        zoho_module: str,
        field_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Sync list to Zoho module."""
        logger.info(f"Syncing list {list_id} to Zoho module: {zoho_module}")

        from lists.list_manager import ListManager

        list_manager = ListManager(self.db)

        # Get list data
        list_data = await list_manager.get_list(list_id, include_items=True)

        sync_results = {
            "list_id": list_id,
            "zoho_module": zoho_module,
            "total_items": len(list_data.get("items", [])),
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }

        # Sync each item
        for item in list_data.get("items", []):
            try:
                # Map fields
                zoho_record = self._map_fields(item["item_data"], field_mapping)

                # Create or update record
                result = await self.create_zoho_record(zoho_module, zoho_record)

                if result.get("status") == "success":
                    sync_results["created"] += 1
                else:
                    sync_results["failed"] += 1
                    sync_results["errors"].append(result.get("error"))

            except Exception as e:
                logger.error(f"Error syncing item {item['id']}: {str(e)}")
                sync_results["failed"] += 1
                sync_results["errors"].append(str(e))

        return sync_results

    def _map_fields(
        self,
        source_data: Dict[str, Any],
        field_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Map source fields to Zoho fields."""
        zoho_data = {}

        for source_field, zoho_field in field_mapping.items():
            if source_field in source_data:
                zoho_data[zoho_field] = source_data[source_field]

        return zoho_data

    async def create_zoho_record(
        self,
        module: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create record in Zoho."""
        logger.info(f"Creating record in Zoho module: {module}")

        try:
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "data": [data]
            }

            response = await self.client.post(
                f"{self.base_url}/{module}",
                headers=headers,
                json=payload
            )

            response.raise_for_status()
            result = response.json()

            return {
                "status": "success",
                "result": result
            }

        except Exception as e:
            logger.error(f"Error creating Zoho record: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def update_zoho_record(
        self,
        module: str,
        record_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update record in Zoho."""
        logger.info(f"Updating record {record_id} in Zoho module: {module}")

        try:
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "data": [{"id": record_id, **data}]
            }

            response = await self.client.put(
                f"{self.base_url}/{module}",
                headers=headers,
                json=payload
            )

            response.raise_for_status()
            result = response.json()

            return {
                "status": "success",
                "result": result
            }

        except Exception as e:
            logger.error(f"Error updating Zoho record: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def get_zoho_record(
        self,
        module: str,
        record_id: str
    ) -> Dict[str, Any]:
        """Get record from Zoho."""
        logger.info(f"Getting record {record_id} from Zoho module: {module}")

        try:
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}"
            }

            response = await self.client.get(
                f"{self.base_url}/{module}/{record_id}",
                headers=headers
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error getting Zoho record: {str(e)}")
            return {
                "error": str(e)
            }

    async def sync_from_zoho(
        self,
        zoho_module: str,
        list_id: int,
        field_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Sync data from Zoho to list."""
        logger.info(f"Syncing from Zoho module {zoho_module} to list {list_id}")

        from lists.list_manager import ListManager

        list_manager = ListManager(self.db)

        try:
            # Get records from Zoho
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}"
            }

            response = await self.client.get(
                f"{self.base_url}/{zoho_module}",
                headers=headers,
                params={"per_page": 200}
            )

            response.raise_for_status()
            zoho_data = response.json()

            records = zoho_data.get("data", [])

            # Map and add to list
            items_to_add = []
            for record in records:
                # Reverse map fields
                item_data = self._reverse_map_fields(record, field_mapping)
                items_to_add.append({"data": item_data})

            # Add to list
            result = await list_manager.add_items(list_id, items_to_add)

            return {
                "status": "success",
                "zoho_module": zoho_module,
                "list_id": list_id,
                "records_synced": len(items_to_add),
                "result": result
            }

        except Exception as e:
            logger.error(f"Error syncing from Zoho: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _reverse_map_fields(
        self,
        zoho_data: Dict[str, Any],
        field_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Reverse map Zoho fields to list fields."""
        list_data = {}

        # Reverse the mapping
        for list_field, zoho_field in field_mapping.items():
            if zoho_field in zoho_data:
                list_data[list_field] = zoho_data[zoho_field]

        return list_data

    async def search_zoho_records(
        self,
        module: str,
        search_criteria: str
    ) -> Dict[str, Any]:
        """Search Zoho records."""
        logger.info(f"Searching Zoho module {module} with criteria: {search_criteria}")

        try:
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.access_token}"
            }

            response = await self.client.get(
                f"{self.base_url}/{module}/search",
                headers=headers,
                params={"criteria": search_criteria}
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error searching Zoho records: {str(e)}")
            return {
                "error": str(e)
            }

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
