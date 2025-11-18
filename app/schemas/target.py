"""Target schemas"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.target import TargetType, TargetStatus


class TargetBase(BaseModel):
    """Base target schema"""
    name: str = Field(..., min_length=1, max_length=200)
    type: TargetType
    value: str = Field(..., min_length=1)
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}


class TargetCreate(TargetBase):
    """Schema for creating a target"""
    investigation_id: int


class TargetUpdate(BaseModel):
    """Schema for updating a target"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[TargetType] = None
    value: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TargetStatus] = None
    metadata: Optional[Dict[str, Any]] = None
    enrichment_data: Optional[Dict[str, Any]] = None


class TargetResponse(TargetBase):
    """Schema for target response"""
    id: int
    investigation_id: int
    status: TargetStatus
    enrichment_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
