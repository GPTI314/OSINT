"""Crawling Session model"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class CrawlingSessionStatus(str, Enum):
    """Crawling session status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CrawlingSession(Base):
    """Crawling Session model for web crawling tasks"""
    __tablename__ = "crawling_sessions"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False, index=True)
    status = Column(SQLEnum(CrawlingSessionStatus), default=CrawlingSessionStatus.PENDING, nullable=False)

    seed_url = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    config = Column(JSON, default=dict, nullable=False)  # Crawling configuration (depth, filters, etc.)
    visited_urls = Column(JSON, default=list, nullable=False)  # List of visited URLs
    queued_urls = Column(JSON, default=list, nullable=False)  # URLs to crawl

    pages_crawled = Column(Integer, default=0, nullable=False)
    links_discovered = Column(Integer, default=0, nullable=False)
    max_depth = Column(Integer, default=3, nullable=False)
    current_depth = Column(Integer, default=0, nullable=False)

    rate_limit = Column(Float, default=1.0, nullable=False)  # Requests per second
    respect_robots_txt = Column(Integer, default=1, nullable=False)  # Boolean as int

    errors = Column(JSON, default=list, nullable=False)  # Error log

    # Relationships
    investigation = relationship("Investigation", back_populates="crawling_sessions")

    def __repr__(self):
        return f"<CrawlingSession {self.name}: {self.status}>"
