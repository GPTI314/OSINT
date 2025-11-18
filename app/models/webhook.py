"""Webhook models"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, JSON, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class WebhookEventType(str, Enum):
    """Webhook event types"""
    INVESTIGATION_CREATED = "investigation.created"
    INVESTIGATION_UPDATED = "investigation.updated"
    INVESTIGATION_COMPLETED = "investigation.completed"
    TARGET_ADDED = "target.added"
    FINDING_CREATED = "finding.created"
    FINDING_UPDATED = "finding.updated"
    SCRAPING_JOB_COMPLETED = "scraping_job.completed"
    CRAWLING_SESSION_COMPLETED = "crawling_session.completed"
    REPORT_GENERATED = "report.generated"


class WebhookEventStatus(str, Enum):
    """Webhook event delivery status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class Webhook(Base):
    """Webhook model for event notifications"""
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    secret = Column(String, nullable=False)  # For HMAC signature

    events = Column(JSON, default=list, nullable=False)  # List of event types to subscribe
    is_active = Column(Integer, default=1, nullable=False)  # Boolean as int

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    metadata = Column(JSON, default=dict, nullable=False)

    # Relationships
    events_sent = relationship("WebhookEvent", back_populates="webhook", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Webhook {self.name}>"


class WebhookEvent(Base):
    """Webhook Event model for tracking event deliveries"""
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False)

    event_type = Column(SQLEnum(WebhookEventType), nullable=False)
    status = Column(SQLEnum(WebhookEventStatus), default=WebhookEventStatus.PENDING, nullable=False)

    payload = Column(JSON, nullable=False)
    response_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)

    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    delivered_at = Column(DateTime, nullable=True)
    next_retry_at = Column(DateTime, nullable=True)

    error = Column(Text, nullable=True)

    # Relationships
    webhook = relationship("Webhook", back_populates="events_sent")

    def __repr__(self):
        return f"<WebhookEvent {self.event_type}: {self.status}>"
