"""
Target model for OSINT investigation targets.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.sql import func
import enum

from core.database import Base


class TargetType(str, enum.Enum):
    """Target type enumeration."""
    DOMAIN = "domain"
    IP_ADDRESS = "ip_address"
    EMAIL = "email"
    PHONE = "phone"
    USERNAME = "username"
    PERSON = "person"
    ORGANIZATION = "organization"
    URL = "url"
    FILE_HASH = "file_hash"
    CRYPTO_ADDRESS = "crypto_address"
    OTHER = "other"


class Target(Base):
    """Target model."""

    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=False)
    target_type = Column(SQLEnum(TargetType), nullable=False)
    value = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    metadata = Column(JSON, default=dict)
    enrichment_data = Column(JSON, default=dict)
    risk_score = Column(Integer, default=0)  # 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Target(id={self.id}, type='{self.target_type}', value='{self.value}')>"
