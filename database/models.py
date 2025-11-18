"""SQLAlchemy ORM models for PostgreSQL."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    JSON, Enum as SQLEnum, Float, BigInteger, Table
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum


Base = declarative_base()


# Association tables for many-to-many relationships
investigation_targets = Table(
    'investigation_targets',
    Base.metadata,
    Column('investigation_id', Integer, ForeignKey('investigations.id', ondelete='CASCADE')),
    Column('target_id', Integer, ForeignKey('targets.id', ondelete='CASCADE'))
)

investigation_users = Table(
    'investigation_users',
    Base.metadata,
    Column('investigation_id', Integer, ForeignKey('investigations.id', ondelete='CASCADE')),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'))
)


class InvestigationStatus(enum.Enum):
    """Investigation status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TargetType(enum.Enum):
    """Target type enumeration."""
    DOMAIN = "domain"
    IP = "ip"
    EMAIL = "email"
    PHONE = "phone"
    PERSON = "person"
    ORGANIZATION = "organization"
    URL = "url"
    USERNAME = "username"
    CRYPTOCURRENCY = "cryptocurrency"


class JobStatus(enum.Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SeverityLevel(enum.Enum):
    """Severity level enumeration."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserRole(enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.ANALYST, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    investigations = relationship("Investigation", secondary=investigation_users, back_populates="users")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class APIKey(Base):
    """API Key model."""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class Investigation(Base):
    """Investigation model."""
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(SQLEnum(InvestigationStatus), default=InvestigationStatus.DRAFT, nullable=False, index=True)
    priority = Column(Integer, default=0)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(JSON, default={})
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    targets = relationship("Target", secondary=investigation_targets, back_populates="investigations")
    users = relationship("User", secondary=investigation_users, back_populates="investigations")
    findings = relationship("Finding", back_populates="investigation", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="investigation", cascade="all, delete-orphan")


class Target(Base):
    """Target model."""
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(TargetType), nullable=False, index=True)
    value = Column(String(500), nullable=False, index=True)
    name = Column(String(255))
    description = Column(Text)
    metadata = Column(JSON, default={})
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    investigations = relationship("Investigation", secondary=investigation_targets, back_populates="targets")
    scraping_jobs = relationship("ScrapingJob", back_populates="target", cascade="all, delete-orphan")
    crawling_sessions = relationship("CrawlingSession", back_populates="target", cascade="all, delete-orphan")
    intelligence_data = relationship("IntelligenceData", back_populates="target", cascade="all, delete-orphan")


class ScrapingJob(Base):
    """Scraping job model."""
    __tablename__ = "scraping_jobs"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id", ondelete="CASCADE"), nullable=False)
    url = Column(Text, nullable=False)
    scraper_type = Column(String(50), nullable=False)  # static, dynamic, api
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    progress = Column(Float, default=0.0)
    items_scraped = Column(Integer, default=0)
    error_message = Column(Text)
    config = Column(JSON, default={})
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    target = relationship("Target", back_populates="scraping_jobs")


class CrawlingSession(Base):
    """Crawling session model."""
    __tablename__ = "crawling_sessions"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id", ondelete="CASCADE"), nullable=False)
    start_url = Column(Text, nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    pages_crawled = Column(Integer, default=0)
    pages_queued = Column(Integer, default=0)
    max_depth = Column(Integer, default=3)
    error_message = Column(Text)
    config = Column(JSON, default={})
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    target = relationship("Target", back_populates="crawling_sessions")


class IntelligenceData(Base):
    """Intelligence data model."""
    __tablename__ = "intelligence_data"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id", ondelete="CASCADE"), nullable=False)
    source = Column(String(100), nullable=False, index=True)  # whois, dns, shodan, etc.
    data_type = Column(String(50), nullable=False)
    data = Column(JSON, nullable=False)
    confidence = Column(Float, default=0.0)
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    target = relationship("Target", back_populates="intelligence_data")


class Finding(Base):
    """Finding model."""
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(SQLEnum(SeverityLevel), default=SeverityLevel.INFO, nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    evidence = Column(JSON, default={})
    source_url = Column(Text)
    confidence = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    investigation = relationship("Investigation", back_populates="findings")


class Report(Base):
    """Report model."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    format = Column(String(20), nullable=False)  # pdf, html, json, markdown
    content = Column(Text)
    file_path = Column(String(500))
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    investigation = relationship("Investigation", back_populates="reports")


class AuditLog(Base):
    """Audit log model."""
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer)
    details = Column(JSON, default={})
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")


# SEO/SEM Models
class SEOAnalysis(Base):
    """SEO Analysis model."""
    __tablename__ = "seo_analysis"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True)
    target_url = Column(Text, nullable=False, index=True)
    analysis_type = Column(String(50), nullable=False, index=True)  # on_page, technical, backlink, etc.
    score = Column(Float)
    issues = Column(JSON, default={})
    recommendations = Column(JSON, default={})
    raw_data = Column(JSON, default={})
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})


class KeywordRanking(Base):
    """Keyword Rankings model."""
    __tablename__ = "keyword_rankings"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True)
    domain = Column(String(255), nullable=False, index=True)
    keyword = Column(String(255), nullable=False, index=True)
    position = Column(Integer)
    search_volume = Column(Integer)
    difficulty = Column(Float)
    cpc = Column(Float)
    tracked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    location = Column(String(100))
    device_type = Column(String(20))  # desktop, mobile, tablet
    metadata = Column(JSON, default={})


class Backlink(Base):
    """Backlink model."""
    __tablename__ = "backlinks"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True)
    target_domain = Column(String(255), nullable=False, index=True)
    source_url = Column(Text, nullable=False)
    source_domain = Column(String(255), index=True)
    anchor_text = Column(Text)
    link_type = Column(String(20))  # dofollow, nofollow
    domain_authority = Column(Integer)
    page_authority = Column(Integer)
    discovered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})


class CompetitorAnalysis(Base):
    """Competitor Analysis model."""
    __tablename__ = "competitor_analysis"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True)
    target_domain = Column(String(255), nullable=False, index=True)
    competitor_domain = Column(String(255), nullable=False, index=True)
    comparison_metrics = Column(JSON, default={})
    shared_keywords = Column(JSON, default=[])
    backlink_overlap = Column(JSON, default={})
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})


# LinkedIn Models
class LinkedInProfile(Base):
    """LinkedIn Profile model."""
    __tablename__ = "linkedin_profiles"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True)
    profile_url = Column(Text, unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    headline = Column(Text)
    location = Column(String(255))
    industry = Column(String(100))
    current_company = Column(String(255))
    current_position = Column(String(255))
    company_size = Column(String(50))
    experience = Column(JSON, default=[])
    education = Column(JSON, default=[])
    skills = Column(JSON, default=[])
    connections_count = Column(Integer)
    recommendations_count = Column(Integer)
    posts_count = Column(Integer)
    extracted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})


class LinkedInCompany(Base):
    """LinkedIn Company model."""
    __tablename__ = "linkedin_companies"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True)
    company_url = Column(Text, unique=True, nullable=False, index=True)
    company_name = Column(String(255), index=True)
    industry = Column(String(100))
    company_size = Column(String(50))
    headquarters = Column(String(255))
    website = Column(Text)
    description = Column(Text)
    employee_count = Column(Integer)
    followers_count = Column(Integer)
    specialties = Column(JSON, default=[])
    extracted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})


class LinkedInVertical(Base):
    """LinkedIn Vertical model."""
    __tablename__ = "linkedin_verticals"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True)
    vertical_name = Column(String(255), nullable=False, index=True)
    vertical_type = Column(String(50), nullable=False)  # industry, location, company_size, etc.
    criteria = Column(JSON, nullable=False)
    profile_ids = Column(JSON, default=[])
    company_ids = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    metadata = Column(JSON, default={})


class VerticalFilter(Base):
    """Vertical Filter model."""
    __tablename__ = "vertical_filters"

    id = Column(Integer, primary_key=True, index=True)
    vertical_id = Column(Integer, ForeignKey("linkedin_verticals.id", ondelete="CASCADE"), nullable=False)
    filter_type = Column(String(50), nullable=False)
    filter_value = Column(Text)
    applied_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})


# List Management Models
class ConfigurableList(Base):
    """Configurable List model."""
    __tablename__ = "configurable_lists"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True)
    list_name = Column(String(255), nullable=False, index=True)
    list_type = Column(String(50))  # linkedin_vertical, seo_keywords, targets, etc.
    description = Column(Text)
    columns = Column(JSON, default={})  # Column definitions
    sort_config = Column(JSON, default={})
    filter_config = Column(JSON, default={})
    view_config = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    metadata = Column(JSON, default={})


class ListItem(Base):
    """List Item model."""
    __tablename__ = "list_items"

    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("configurable_lists.id", ondelete="CASCADE"), nullable=False)
    item_data = Column(JSON, nullable=False)
    position = Column(Integer)
    tags = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    metadata = Column(JSON, default={})


class ListIntegration(Base):
    """List Integration model."""
    __tablename__ = "list_integrations"

    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("configurable_lists.id", ondelete="CASCADE"), nullable=False)
    integration_type = Column(String(50), nullable=False)  # zoho, notion, etc.
    integration_config = Column(JSON, default={})
    sync_status = Column(String(50))
    last_synced_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})


# Austrian Zoning Models
class ZoningSearch(Base):
    """Zoning Search model."""
    __tablename__ = "zoning_searches"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True)
    street_name = Column(String(255), nullable=False, index=True)
    house_number = Column(String(50), nullable=False)
    city = Column(String(255))
    search_result = Column(JSON, default={})
    plantextbestimmungen = Column(Text)
    parsed_data = Column(JSON, default={})
    searched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})
