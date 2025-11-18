"""Investigation model"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class InvestigationStatus(str, Enum):
    """Investigation status"""
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class InvestigationPriority(str, Enum):
    """Investigation priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Investigation(Base):
    """Investigation model for managing OSINT investigations"""
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(InvestigationStatus), default=InvestigationStatus.DRAFT, nullable=False)
    priority = Column(SQLEnum(InvestigationPriority), default=InvestigationPriority.MEDIUM, nullable=False)
    case_number = Column(String, unique=True, index=True, nullable=False)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    tags = Column(JSON, default=list, nullable=False)  # List of tags
    metadata = Column(JSON, default=dict, nullable=False)  # Additional metadata

    # Relationships
    created_by_user = relationship("User", back_populates="investigations", foreign_keys=[created_by])
    targets = relationship("Target", back_populates="investigation", cascade="all, delete-orphan")
    scraping_jobs = relationship("ScrapingJob", back_populates="investigation", cascade="all, delete-orphan")
    crawling_sessions = relationship("CrawlingSession", back_populates="investigation", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="investigation", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="investigation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Investigation {self.case_number}: {self.title}>"
