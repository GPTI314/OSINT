"""Report model"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class ReportFormat(str, Enum):
    """Report format"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    EXCEL = "excel"
    CSV = "csv"
    MARKDOWN = "markdown"


class ReportStatus(str, Enum):
    """Report status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(Base):
    """Report model for investigation reports"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)

    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    format = Column(SQLEnum(ReportFormat), nullable=False)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING, nullable=False)

    template = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes

    config = Column(JSON, default=dict, nullable=False)  # Report configuration
    sections = Column(JSON, default=list, nullable=False)  # Report sections to include

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    generated_at = Column(DateTime, nullable=True)

    metadata = Column(JSON, default=dict, nullable=False)

    # Relationships
    investigation = relationship("Investigation", back_populates="reports")
    created_by_user = relationship("User", back_populates="reports", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Report {self.title}: {self.format}>"
