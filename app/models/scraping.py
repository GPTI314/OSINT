"""Scraping Job model"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class ScrapingJobStatus(str, Enum):
    """Scraping job status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScrapingJobType(str, Enum):
    """Scraping job type"""
    WEB_PAGE = "web_page"
    SOCIAL_MEDIA = "social_media"
    NEWS = "news"
    FORUM = "forum"
    MARKETPLACE = "marketplace"
    DOCUMENT = "document"
    CUSTOM = "custom"


class ScrapingJob(Base):
    """Scraping Job model for web scraping tasks"""
    __tablename__ = "scraping_jobs"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False, index=True)
    type = Column(SQLEnum(ScrapingJobType), nullable=False)
    status = Column(SQLEnum(ScrapingJobStatus), default=ScrapingJobStatus.PENDING, nullable=False)

    url = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    config = Column(JSON, default=dict, nullable=False)  # Scraping configuration
    results = Column(JSON, default=dict, nullable=False)  # Scraped results
    errors = Column(JSON, default=list, nullable=False)  # Error log

    items_scraped = Column(Integer, default=0, nullable=False)
    pages_processed = Column(Integer, default=0, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)

    scheduled = Column(Boolean, default=False, nullable=False)
    schedule_cron = Column(String, nullable=True)

    # Relationships
    investigation = relationship("Investigation", back_populates="scraping_jobs")

    def __repr__(self):
        return f"<ScrapingJob {self.name}: {self.status}>"
