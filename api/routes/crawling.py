"""Crawling session routes - stub implementation."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_crawling_sessions():
    """List crawling sessions."""
    return {"message": "Crawling sessions endpoint - to be implemented"}


@router.post("/")
async def create_crawling_session():
    """Create crawling session."""
    return {"message": "Create crawling session - to be implemented"}
