"""API Key schemas"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class APIKeyBase(BaseModel):
    """Base API key schema"""
    name: str = Field(..., min_length=1, max_length=100)
    scopes: Optional[List[str]] = None


class APIKeyCreate(APIKeyBase):
    """Schema for creating an API key"""
    expires_in_days: Optional[int] = Field(365, ge=1, le=3650)


class APIKeyUpdate(BaseModel):
    """Schema for updating an API key"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    scopes: Optional[List[str]] = None


class APIKeyResponse(APIKeyBase):
    """Schema for API key response"""
    id: int
    prefix: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    user_id: int

    class Config:
        from_attributes = True


class APIKeyCreateResponse(APIKeyResponse):
    """Schema for API key creation response (includes full key)"""
    key: str  # Full API key - only returned once during creation
