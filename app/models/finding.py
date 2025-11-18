"""Finding model"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class FindingSeverity(str, Enum):
    """Finding severity"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingStatus(str, Enum):
    """Finding status"""
    NEW = "new"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


class Finding(Base):
    """Finding model for investigation discoveries"""
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    target_id = Column(Integer, ForeignKey("targets.id", ondelete="SET NULL"), nullable=True)

    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    severity = Column(SQLEnum(FindingSeverity), nullable=False)
    status = Column(SQLEnum(FindingStatus), default=FindingStatus.NEW, nullable=False)

    category = Column(String, nullable=True)
    source = Column(String, nullable=True)  # Source of the finding

    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    risk_score = Column(Float, nullable=True)  # 0.0 to 100.0

    evidence = Column(JSON, default=dict, nullable=False)  # Evidence data
    artifacts = Column(JSON, default=list, nullable=False)  # URLs, screenshots, etc.

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tags = Column(JSON, default=list, nullable=False)
    metadata = Column(JSON, default=dict, nullable=False)

    # Relationships
    investigation = relationship("Investigation", back_populates="findings")
    target = relationship("Target", back_populates="findings")
    created_by_user = relationship("User", back_populates="findings", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Finding {self.title}: {self.severity}>"
