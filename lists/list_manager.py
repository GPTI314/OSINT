"""Configurable List Management System - Create and manage custom lists."""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database.models import ConfigurableList, ListItem, ListIntegration

logger = logging.getLogger(__name__)


class ListManager:
    """
    Configurable list management:
    - Create custom lists
    - Add/remove items
    - Sort and filter
    - Group and categorize
    - Export to various formats
    - API integration (Zoho, Notion)
    - Real-time synchronization
    - List templates
    - Bulk operations
    """

    def __init__(self, db: Session):
        self.db = db

    async def create_list(
        self,
        list_config: Dict[str, Any],
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new configurable list."""
        logger.info(f"Creating new list: {list_config.get('name')}")

        list_obj = ConfigurableList(
            investigation_id=investigation_id,
            list_name=list_config.get("name", "Unnamed List"),
            list_type=list_config.get("type", "custom"),
            description=list_config.get("description"),
            columns=list_config.get("columns", {}),
            sort_config=list_config.get("sort_config", {}),
            filter_config=list_config.get("filter_config", {}),
            view_config=list_config.get("view_config", {}),
            metadata=list_config.get("metadata", {})
        )

        self.db.add(list_obj)
        self.db.commit()
        self.db.refresh(list_obj)

        return self._list_to_dict(list_obj)

    def _list_to_dict(self, list_obj: ConfigurableList) -> Dict[str, Any]:
        """Convert list model to dictionary."""
        # Get items count
        items_count = self.db.query(ListItem).filter(
            ListItem.list_id == list_obj.id
        ).count()

        return {
            "id": list_obj.id,
            "investigation_id": list_obj.investigation_id,
            "list_name": list_obj.list_name,
            "list_type": list_obj.list_type,
            "description": list_obj.description,
            "columns": list_obj.columns,
            "sort_config": list_obj.sort_config,
            "filter_config": list_obj.filter_config,
            "view_config": list_obj.view_config,
            "items_count": items_count,
            "created_at": list_obj.created_at.isoformat(),
            "updated_at": list_obj.updated_at.isoformat(),
            "metadata": list_obj.metadata
        }

    async def add_items(
        self,
        list_id: int,
        items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Add items to list."""
        logger.info(f"Adding {len(items)} items to list {list_id}")

        list_obj = self.db.query(ConfigurableList).filter(
            ConfigurableList.id == list_id
        ).first()

        if not list_obj:
            raise ValueError(f"List {list_id} not found")

        # Get current max position
        max_position_query = self.db.query(ListItem).filter(
            ListItem.list_id == list_id
        ).order_by(ListItem.position.desc()).first()

        current_position = max_position_query.position if max_position_query else 0

        # Add items
        added_items = []
        for item_data in items:
            current_position += 1

            item = ListItem(
                list_id=list_id,
                item_data=item_data.get("data", item_data),
                position=current_position,
                tags=item_data.get("tags", []),
                metadata=item_data.get("metadata", {})
            )

            self.db.add(item)
            added_items.append(item)

        self.db.commit()

        # Update list updated_at
        list_obj.updated_at = datetime.now()
        self.db.commit()

        return {
            "list_id": list_id,
            "items_added": len(added_items),
            "items": [self._item_to_dict(item) for item in added_items]
        }

    def _item_to_dict(self, item: ListItem) -> Dict[str, Any]:
        """Convert item model to dictionary."""
        return {
            "id": item.id,
            "list_id": item.list_id,
            "item_data": item.item_data,
            "position": item.position,
            "tags": item.tags,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
            "metadata": item.metadata
        }

    async def remove_items(
        self,
        list_id: int,
        item_ids: List[int]
    ) -> Dict[str, Any]:
        """Remove items from list."""
        logger.info(f"Removing {len(item_ids)} items from list {list_id}")

        deleted_count = self.db.query(ListItem).filter(
            and_(
                ListItem.list_id == list_id,
                ListItem.id.in_(item_ids)
            )
        ).delete(synchronize_session=False)

        self.db.commit()

        # Update list updated_at
        list_obj = self.db.query(ConfigurableList).filter(
            ConfigurableList.id == list_id
        ).first()

        if list_obj:
            list_obj.updated_at = datetime.now()
            self.db.commit()

        return {
            "list_id": list_id,
            "items_removed": deleted_count
        }

    async def get_list(
        self,
        list_id: int,
        include_items: bool = True
    ) -> Dict[str, Any]:
        """Get list with optional items."""
        logger.info(f"Getting list {list_id}")

        list_obj = self.db.query(ConfigurableList).filter(
            ConfigurableList.id == list_id
        ).first()

        if not list_obj:
            raise ValueError(f"List {list_id} not found")

        result = self._list_to_dict(list_obj)

        if include_items:
            items = self.db.query(ListItem).filter(
                ListItem.list_id == list_id
            ).order_by(ListItem.position).all()

            result["items"] = [self._item_to_dict(item) for item in items]

        return result

    async def sort_list(
        self,
        list_id: int,
        sort_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sort list by various criteria."""
        logger.info(f"Sorting list {list_id} with config: {sort_config}")

        list_obj = self.db.query(ConfigurableList).filter(
            ConfigurableList.id == list_id
        ).first()

        if not list_obj:
            raise ValueError(f"List {list_id} not found")

        # Update sort config
        list_obj.sort_config = sort_config
        list_obj.updated_at = datetime.now()

        # Get items and sort
        items = self.db.query(ListItem).filter(
            ListItem.list_id == list_id
        ).all()

        # Sort items based on config
        sort_field = sort_config.get("field", "position")
        sort_order = sort_config.get("order", "asc")  # asc or desc
        reverse = sort_order == "desc"

        if sort_field == "position":
            sorted_items = sorted(items, key=lambda x: x.position, reverse=reverse)
        elif sort_field in ["created_at", "updated_at"]:
            sorted_items = sorted(
                items,
                key=lambda x: getattr(x, sort_field),
                reverse=reverse
            )
        else:
            # Sort by custom field in item_data
            sorted_items = sorted(
                items,
                key=lambda x: x.item_data.get(sort_field, ""),
                reverse=reverse
            )

        # Update positions
        for idx, item in enumerate(sorted_items, start=1):
            item.position = idx

        self.db.commit()

        return {
            "list_id": list_id,
            "sort_config": sort_config,
            "items_sorted": len(sorted_items)
        }

    async def filter_list(
        self,
        list_id: int,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Filter list items."""
        logger.info(f"Filtering list {list_id} with filters: {filters}")

        list_obj = self.db.query(ConfigurableList).filter(
            ConfigurableList.id == list_id
        ).first()

        if not list_obj:
            raise ValueError(f"List {list_id} not found")

        # Update filter config
        list_obj.filter_config = filters
        list_obj.updated_at = datetime.now()
        self.db.commit()

        # Get items
        items_query = self.db.query(ListItem).filter(
            ListItem.list_id == list_id
        )

        # Apply filters
        filtered_items = []
        for item in items_query.all():
            if self._item_matches_filters(item, filters):
                filtered_items.append(item)

        return {
            "list_id": list_id,
            "filters": filters,
            "total_items": items_query.count(),
            "filtered_items": len(filtered_items),
            "items": [self._item_to_dict(item) for item in filtered_items]
        }

    def _item_matches_filters(
        self,
        item: ListItem,
        filters: Dict[str, Any]
    ) -> bool:
        """Check if item matches filters."""
        for field, filter_value in filters.items():
            if field == "tags":
                # Check if item has any of the specified tags
                if not any(tag in item.tags for tag in filter_value):
                    return False
            else:
                # Check item_data fields
                item_value = item.item_data.get(field)
                if item_value != filter_value:
                    return False

        return True

    async def export_list(
        self,
        list_id: int,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """Export list in various formats."""
        logger.info(f"Exporting list {list_id} as {format}")

        list_data = await self.get_list(list_id, include_items=True)

        if format == 'csv':
            csv_data = self._export_to_csv(list_data)
            return {
                "list_id": list_id,
                "format": "csv",
                "data": csv_data
            }
        elif format == 'excel':
            # Would generate Excel file
            return {
                "list_id": list_id,
                "format": "excel",
                "message": "Excel export not yet implemented"
            }
        else:
            # JSON format (default)
            return {
                "list_id": list_id,
                "format": "json",
                "data": list_data
            }

    def _export_to_csv(self, list_data: Dict[str, Any]) -> str:
        """Export list to CSV format."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Get all unique fields from items
        all_fields = set()
        for item in list_data.get("items", []):
            all_fields.update(item.get("item_data", {}).keys())

        # Write header
        header = ["id", "position"] + sorted(list(all_fields))
        writer.writerow(header)

        # Write data
        for item in list_data.get("items", []):
            row = [item["id"], item["position"]]
            for field in sorted(list(all_fields)):
                row.append(item.get("item_data", {}).get(field, ""))
            writer.writerow(row)

        return output.getvalue()

    async def sync_to_zoho(
        self,
        list_id: int,
        zoho_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sync list to Zoho."""
        logger.info(f"Syncing list {list_id} to Zoho")

        from integrations.zoho_integrator import ZohoIntegrator

        zoho = ZohoIntegrator(self.db)

        # Get or create integration record
        integration = self.db.query(ListIntegration).filter(
            and_(
                ListIntegration.list_id == list_id,
                ListIntegration.integration_type == "zoho"
            )
        ).first()

        if not integration:
            integration = ListIntegration(
                list_id=list_id,
                integration_type="zoho",
                integration_config=zoho_config,
                sync_status="pending"
            )
            self.db.add(integration)
            self.db.commit()

        # Perform sync
        try:
            result = await zoho.sync_list_to_zoho(
                list_id,
                zoho_config.get("module", "Leads"),
                zoho_config.get("field_mapping", {})
            )

            # Update integration status
            integration.sync_status = "completed"
            integration.last_synced_at = datetime.now()
            self.db.commit()

            return result

        except Exception as e:
            logger.error(f"Error syncing to Zoho: {str(e)}")
            integration.sync_status = "failed"
            integration.metadata = {"error": str(e)}
            self.db.commit()

            return {
                "list_id": list_id,
                "error": str(e),
                "sync_status": "failed"
            }

    async def sync_to_notion(
        self,
        list_id: int,
        notion_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sync list to Notion."""
        logger.info(f"Syncing list {list_id} to Notion")

        from integrations.notion_integrator import NotionIntegrator

        notion = NotionIntegrator(self.db)

        # Get or create integration record
        integration = self.db.query(ListIntegration).filter(
            and_(
                ListIntegration.list_id == list_id,
                ListIntegration.integration_type == "notion"
            )
        ).first()

        if not integration:
            integration = ListIntegration(
                list_id=list_id,
                integration_type="notion",
                integration_config=notion_config,
                sync_status="pending"
            )
            self.db.add(integration)
            self.db.commit()

        # Perform sync
        try:
            result = await notion.sync_list_to_notion(
                list_id,
                notion_config.get("database_id"),
                notion_config.get("property_mapping", {})
            )

            # Update integration status
            integration.sync_status = "completed"
            integration.last_synced_at = datetime.now()
            self.db.commit()

            return result

        except Exception as e:
            logger.error(f"Error syncing to Notion: {str(e)}")
            integration.sync_status = "failed"
            integration.metadata = {"error": str(e)}
            self.db.commit()

            return {
                "list_id": list_id,
                "error": str(e),
                "sync_status": "failed"
            }

    async def bulk_operations(
        self,
        list_id: int,
        operation: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform bulk operations on list items."""
        logger.info(f"Performing bulk {operation} on list {list_id}")

        if operation == "update_tags":
            return await self._bulk_update_tags(list_id, data)
        elif operation == "delete":
            return await self.remove_items(list_id, data.get("item_ids", []))
        elif operation == "move":
            return await self._bulk_move_items(list_id, data)
        else:
            raise ValueError(f"Unknown bulk operation: {operation}")

    async def _bulk_update_tags(
        self,
        list_id: int,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Bulk update tags for items."""
        item_ids = data.get("item_ids", [])
        tags_to_add = data.get("add_tags", [])
        tags_to_remove = data.get("remove_tags", [])

        items = self.db.query(ListItem).filter(
            and_(
                ListItem.list_id == list_id,
                ListItem.id.in_(item_ids)
            )
        ).all()

        updated_count = 0
        for item in items:
            current_tags = set(item.tags or [])

            # Add tags
            current_tags.update(tags_to_add)

            # Remove tags
            current_tags.difference_update(tags_to_remove)

            item.tags = list(current_tags)
            item.updated_at = datetime.now()
            updated_count += 1

        self.db.commit()

        return {
            "list_id": list_id,
            "operation": "update_tags",
            "items_updated": updated_count
        }

    async def _bulk_move_items(
        self,
        list_id: int,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Bulk move items to different positions."""
        item_ids = data.get("item_ids", [])
        target_position = data.get("target_position", 1)

        # This is a simplified implementation
        # In production, would handle complex reordering logic

        items = self.db.query(ListItem).filter(
            and_(
                ListItem.list_id == list_id,
                ListItem.id.in_(item_ids)
            )
        ).all()

        for idx, item in enumerate(items):
            item.position = target_position + idx
            item.updated_at = datetime.now()

        self.db.commit()

        return {
            "list_id": list_id,
            "operation": "move",
            "items_moved": len(items)
        }
