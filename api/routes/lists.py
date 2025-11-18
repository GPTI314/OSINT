"""Configurable Lists API Routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.connection import get_db
from lists.list_manager import ListManager
from auth.dependencies import get_current_user
from database.models import User

router = APIRouter()


class ListCreationRequest(BaseModel):
    name: str = Field(..., description="List name")
    type: str = Field(default="custom", description="List type")
    description: Optional[str] = None
    columns: Optional[dict] = None
    investigation_id: Optional[int] = None


class AddItemsRequest(BaseModel):
    items: List[dict] = Field(..., description="Items to add")


class RemoveItemsRequest(BaseModel):
    item_ids: List[int] = Field(..., description="Item IDs to remove")


class SortListRequest(BaseModel):
    field: str = Field(..., description="Field to sort by")
    order: str = Field(default="asc", description="Sort order (asc/desc)")


class FilterListRequest(BaseModel):
    filters: dict = Field(..., description="Filters to apply")


class ZohoSyncRequest(BaseModel):
    module: str = Field(default="Leads", description="Zoho module")
    field_mapping: dict = Field(..., description="Field mapping")
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class NotionSyncRequest(BaseModel):
    database_id: str = Field(..., description="Notion database ID")
    property_mapping: dict = Field(..., description="Property mapping")
    api_key: str = Field(..., description="Notion API key")


@router.post("/create")
async def create_list(
    request: ListCreationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new configurable list."""
    manager = ListManager(db)

    try:
        list_config = {
            "name": request.name,
            "type": request.type,
            "description": request.description,
            "columns": request.columns or {}
        }

        result = await manager.create_list(list_config, request.investigation_id)

        return {
            "success": True,
            "list": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{list_id}")
async def get_list(
    list_id: int,
    include_items: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list details."""
    manager = ListManager(db)

    try:
        result = await manager.get_list(list_id, include_items)

        return {
            "success": True,
            "list": result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{list_id}/items")
async def add_items_to_list(
    list_id: int,
    request: AddItemsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add items to list."""
    manager = ListManager(db)

    try:
        result = await manager.add_items(list_id, request.items)

        return {
            "success": True,
            "result": result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{list_id}/items")
async def remove_items_from_list(
    list_id: int,
    request: RemoveItemsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove items from list."""
    manager = ListManager(db)

    try:
        result = await manager.remove_items(list_id, request.item_ids)

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{list_id}/sort")
async def sort_list(
    list_id: int,
    request: SortListRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sort list items."""
    manager = ListManager(db)

    try:
        sort_config = {
            "field": request.field,
            "order": request.order
        }

        result = await manager.sort_list(list_id, sort_config)

        return {
            "success": True,
            "result": result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{list_id}/filter")
async def filter_list(
    list_id: int,
    request: FilterListRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Filter list items."""
    manager = ListManager(db)

    try:
        result = await manager.filter_list(list_id, request.filters)

        return {
            "success": True,
            "result": result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{list_id}/export")
async def export_list(
    list_id: int,
    format: str = Query(default="json", regex="^(json|csv|excel)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export list data."""
    manager = ListManager(db)

    try:
        result = await manager.export_list(list_id, format)

        return {
            "success": True,
            "export": result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{list_id}/sync/zoho")
async def sync_to_zoho(
    list_id: int,
    request: ZohoSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sync list to Zoho CRM."""
    manager = ListManager(db)

    try:
        zoho_config = {
            "module": request.module,
            "field_mapping": request.field_mapping,
            "access_token": request.access_token,
            "refresh_token": request.refresh_token
        }

        result = await manager.sync_to_zoho(list_id, zoho_config)

        return {
            "success": True,
            "result": result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{list_id}/sync/notion")
async def sync_to_notion(
    list_id: int,
    request: NotionSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sync list to Notion."""
    manager = ListManager(db)

    try:
        notion_config = {
            "database_id": request.database_id,
            "property_mapping": request.property_mapping,
            "api_key": request.api_key
        }

        result = await manager.sync_to_notion(list_id, notion_config)

        return {
            "success": True,
            "result": result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
