"""
OSINT Result model for storing investigation results.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey, JSON, Float
from sqlalchemy.sql import func
import enum

from core.database import Base


class ResultType(str, enum.Enum):
    """Result type enumeration."""
    WHOIS = "whois"
    DNS = "dns"
    SUBDOMAIN = "subdomain"
    PORT_SCAN = "port_scan"
    GEOLOCATION = "geolocation"
    SOCIAL_MEDIA = "social_media"
    EMAIL_BREACH = "email_breach"
    PHONE_LOOKUP = "phone_lookup"
    THREAT_INTEL = "threat_intel"
    WEB_SCRAPE = "web_scrape"
    IMAGE_METADATA = "image_metadata"
    DOCUMENT_METADATA = "document_metadata"
    BREACH_DATA = "breach_data"
    REPUTATION = "reputation"
    OTHER = "other"


class OSINTResult(Base):
    """OSINT Result model."""

    __tablename__ = "osint_results"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    result_type = Column(SQLEnum(ResultType), nullable=False)
    source = Column(String(100), nullable=False)  # e.g., "Shodan", "WhoisXML", "Manual"
    data = Column(JSON, nullable=False)
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0
    severity = Column(Integer, default=0)  # 0=Info, 1=Low, 2=Medium, 3=High, 4=Critical
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<OSINTResult(id={self.id}, type='{self.result_type}', source='{self.source}')>"
