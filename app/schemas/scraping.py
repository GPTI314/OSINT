"""Scraping schemas"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, HttpUrl
from app.models.scraping import ScrapingJobStatus, ScrapingJobType


class ScrapingJobBase(BaseModel):
    """Base scraping job schema"""
    name: str = Field(..., min_length=1, max_length=200)
    type: ScrapingJobType
    url: str
    description: Optional[str] = None
    config: Dict[str, Any] = {}
    scheduled: bool = False
    schedule_cron: Optional[str] = None


class ScrapingJobCreate(ScrapingJobBase):
    """Schema for creating a scraping job"""
    investigation_id: int


class ScrapingJobUpdate(BaseModel):
    """Schema for updating a scraping job"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ScrapingJobStatus] = None
    config: Optional[Dict[str, Any]] = None
    scheduled: Optional[bool] = None
    schedule_cron: Optional[str] = None


class ScrapingJobResponse(ScrapingJobBase):
    """Schema for scraping job response"""
    id: int
    investigation_id: int
    status: ScrapingJobStatus
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    items_scraped: int
    pages_processed: int
    retry_count: int
    results: Dict[str, Any]
    errors: List[str]

    class Config:
        from_attributes = True
