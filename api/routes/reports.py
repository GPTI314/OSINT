"""Reports routes - stub implementation."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_reports():
    """List reports."""
    return {"message": "Reports endpoint - to be implemented"}
