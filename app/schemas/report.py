"""Report schemas"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.models.report import ReportFormat, ReportStatus


class ReportBase(BaseModel):
    """Base report schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    format: ReportFormat
    template: Optional[str] = None
    config: Dict[str, Any] = {}
    sections: List[str] = []
    metadata: Dict[str, Any] = {}


class ReportCreate(ReportBase):
    """Schema for creating a report"""
    investigation_id: int


class ReportUpdate(BaseModel):
    """Schema for updating a report"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ReportStatus] = None
    config: Optional[Dict[str, Any]] = None
    sections: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ReportResponse(ReportBase):
    """Schema for report response"""
    id: int
    investigation_id: int
    status: ReportStatus
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    generated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReportExportRequest(BaseModel):
    """Schema for report export request"""
    format: ReportFormat
    sections: Optional[List[str]] = None
