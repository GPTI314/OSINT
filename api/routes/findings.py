"""Findings routes - stub implementation."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_findings():
    """List findings."""
    return {"message": "Findings endpoint - to be implemented"}
