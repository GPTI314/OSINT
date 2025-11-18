"""Target model"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class TargetType(str, Enum):
    """Target type"""
    PERSON = "person"
    ORGANIZATION = "organization"
    DOMAIN = "domain"
    IP_ADDRESS = "ip_address"
    EMAIL = "email"
    PHONE = "phone"
    SOCIAL_MEDIA = "social_media"
    USERNAME = "username"
    OTHER = "other"


class TargetStatus(str, Enum):
    """Target status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Target(Base):
    """Target model for investigation subjects"""
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False, index=True)
    type = Column(SQLEnum(TargetType), nullable=False)
    status = Column(SQLEnum(TargetStatus), default=TargetStatus.PENDING, nullable=False)
    value = Column(String, nullable=False)  # The actual target value (email, IP, etc.)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    metadata = Column(JSON, default=dict, nullable=False)
    enrichment_data = Column(JSON, default=dict, nullable=False)  # Enriched data from OSINT sources

    # Relationships
    investigation = relationship("Investigation", back_populates="targets")
    findings = relationship("Finding", back_populates="target", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Target {self.type}: {self.value}>"
