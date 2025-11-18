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
