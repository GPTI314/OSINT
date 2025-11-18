"""Finding schemas"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.models.finding import FindingSeverity, FindingStatus


class FindingBase(BaseModel):
    """Base finding schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    severity: FindingSeverity
    category: Optional[str] = None
    source: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    evidence: Dict[str, Any] = {}
    artifacts: List[str] = []
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class FindingCreate(FindingBase):
    """Schema for creating a finding"""
    investigation_id: int
    target_id: Optional[int] = None


class FindingUpdate(BaseModel):
    """Schema for updating a finding"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    severity: Optional[FindingSeverity] = None
    status: Optional[FindingStatus] = None
    category: Optional[str] = None
    source: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    evidence: Optional[Dict[str, Any]] = None
    artifacts: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class FindingResponse(FindingBase):
    """Schema for finding response"""
    id: int
    investigation_id: int
    target_id: Optional[int] = None
    status: FindingStatus
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
