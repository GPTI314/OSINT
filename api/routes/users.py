"""User management routes - stub implementation."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_users():
    """List users."""
    return {"message": "Users endpoint - to be implemented"}
