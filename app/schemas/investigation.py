"""Investigation schemas"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.models.investigation import InvestigationStatus, InvestigationPriority


class InvestigationBase(BaseModel):
    """Base investigation schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: InvestigationPriority = InvestigationPriority.MEDIUM
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class InvestigationCreate(InvestigationBase):
    """Schema for creating an investigation"""
    pass


class InvestigationUpdate(BaseModel):
    """Schema for updating an investigation"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[InvestigationStatus] = None
    priority: Optional[InvestigationPriority] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class InvestigationResponse(InvestigationBase):
    """Schema for investigation response"""
    id: int
    status: InvestigationStatus
    case_number: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvestigationStats(BaseModel):
    """Investigation statistics"""
    total_targets: int = 0
    total_findings: int = 0
    total_scraping_jobs: int = 0
    total_crawling_sessions: int = 0
    total_reports: int = 0
    critical_findings: int = 0
    high_findings: int = 0
