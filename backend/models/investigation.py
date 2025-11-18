"""
Investigation model for tracking OSINT investigations.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from core.database import Base


class InvestigationStatus(str, enum.Enum):
    """Investigation status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Investigation(Base):
    """Investigation model."""

    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(InvestigationStatus), default=InvestigationStatus.DRAFT, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    priority = Column(Integer, default=3)  # 1=Critical, 2=High, 3=Medium, 4=Low, 5=Info
    tags = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Investigation(id={self.id}, title='{self.title}', status='{self.status}')>"
