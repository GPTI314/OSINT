"""Webhook schemas"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from app.models.webhook import WebhookEventType, WebhookEventStatus


class WebhookBase(BaseModel):
    """Base webhook schema"""
    name: str = Field(..., min_length=1, max_length=100)
    url: str
    events: List[WebhookEventType]
    metadata: Dict[str, Any] = {}


class WebhookCreate(WebhookBase):
    """Schema for creating a webhook"""
    pass


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = None
    events: Optional[List[WebhookEventType]] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class WebhookResponse(WebhookBase):
    """Schema for webhook response"""
    id: int
    user_id: int
    secret: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookEventResponse(BaseModel):
    """Schema for webhook event response"""
    id: int
    webhook_id: int
    event_type: WebhookEventType
    status: WebhookEventStatus
    payload: Dict[str, Any]
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    retry_count: int
    max_retries: int
    created_at: datetime
    delivered_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True
