"""Crawling schemas"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from app.models.crawling import CrawlingSessionStatus


class CrawlingSessionBase(BaseModel):
    """Base crawling session schema"""
    name: str = Field(..., min_length=1, max_length=200)
    seed_url: str
    description: Optional[str] = None
    max_depth: int = Field(3, ge=1, le=10)
    rate_limit: float = Field(1.0, ge=0.1, le=10.0)
    respect_robots_txt: bool = True
    config: Dict[str, Any] = {}


class CrawlingSessionCreate(CrawlingSessionBase):
    """Schema for creating a crawling session"""
    investigation_id: int


class CrawlingSessionUpdate(BaseModel):
    """Schema for updating a crawling session"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[CrawlingSessionStatus] = None
    max_depth: Optional[int] = Field(None, ge=1, le=10)
    rate_limit: Optional[float] = Field(None, ge=0.1, le=10.0)
    config: Optional[Dict[str, Any]] = None


class CrawlingSessionResponse(CrawlingSessionBase):
    """Schema for crawling session response"""
    id: int
    investigation_id: int
    status: CrawlingSessionStatus
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    pages_crawled: int
    links_discovered: int
    current_depth: int
    visited_urls: List[str]
    queued_urls: List[str]
    errors: List[str]

    class Config:
        from_attributes = True
