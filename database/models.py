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


# ============================================================================
# CREDIT RISK SCORING MODELS
# ============================================================================


class ApplicationStatus(enum.Enum):
    """Application status enumeration."""
    PENDING = "pending"
    COLLECTING_DATA = "collecting_data"
    ANALYZING = "analyzing"
    SCORED = "scored"
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"


class RiskTier(enum.Enum):
    """Risk tier enumeration."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    HIGH_RISK = "high_risk"


class RiskLevel(enum.Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class FraudSeverity(enum.Enum):
    """Fraud severity enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConsumerApplication(Base):
    """Consumer credit application model."""
    __tablename__ = "consumer_applications"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True)
    applicant_name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    address = Column(Text, nullable=True)
    requested_amount = Column(Float, nullable=True)
    loan_purpose = Column(String(100), nullable=True)
    employment_status = Column(String(50), nullable=True)
    monthly_income = Column(Float, nullable=True)
    application_status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False, index=True)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    risk_scores = relationship("ConsumerRiskScore", back_populates="application", cascade="all, delete-orphan")
    osint_data = relationship("ConsumerOSINTData", back_populates="application", cascade="all, delete-orphan")
    financial_data = relationship("ConsumerFinancialData", back_populates="application", cascade="all, delete-orphan")
    behavioral_data = relationship("ConsumerBehavioralData", back_populates="application", cascade="all, delete-orphan")
    fraud_indicators = relationship("ConsumerFraudIndicator", back_populates="application", cascade="all, delete-orphan")


class ConsumerRiskScore(Base):
    """Consumer risk score model."""
    __tablename__ = "consumer_risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("consumer_applications.id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Integer, nullable=True)  # 300-850 scale
    osint_score = Column(Integer, nullable=True)
    traditional_score = Column(Integer, nullable=True)
    behavioral_score = Column(Integer, nullable=True)
    fraud_score = Column(Integer, nullable=True)
    risk_tier = Column(SQLEnum(RiskTier), nullable=True, index=True)
    risk_level = Column(SQLEnum(RiskLevel), nullable=True, index=True)
    probability_of_default = Column(Float, nullable=True)
    recommended_interest_rate = Column(Float, nullable=True)
    recommended_loan_amount = Column(Float, nullable=True)
    approval_recommendation = Column(String(20), nullable=True)  # approve, reject, manual_review
    score_components = Column(JSON, default={})
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})

    # Relationships
    application = relationship("ConsumerApplication", back_populates="risk_scores")


class ConsumerOSINTData(Base):
    """Consumer OSINT data model."""
    __tablename__ = "consumer_osint_data"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("consumer_applications.id", ondelete="CASCADE"), nullable=False)
    data_type = Column(String(50), nullable=False, index=True)  # social_media, domain, email, phone, etc.
    source = Column(String(100), nullable=False)
    data = Column(JSON, nullable=False)
    risk_signals = Column(JSON, default={})
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})

    # Relationships
    application = relationship("ConsumerApplication", back_populates="osint_data")


class ConsumerFinancialData(Base):
    """Consumer financial data model."""
    __tablename__ = "consumer_financial_data"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("consumer_applications.id", ondelete="CASCADE"), nullable=False)
    bank_accounts = Column(JSON, default={})
    credit_cards = Column(JSON, default={})
    loans = Column(JSON, default={})
    income_sources = Column(JSON, default={})
    expenses = Column(JSON, default={})
    debt_to_income_ratio = Column(Float, nullable=True)
    credit_utilization = Column(Float, nullable=True)
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})

    # Relationships
    application = relationship("ConsumerApplication", back_populates="financial_data")


class ConsumerBehavioralData(Base):
    """Consumer behavioral data model."""
    __tablename__ = "consumer_behavioral_data"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("consumer_applications.id", ondelete="CASCADE"), nullable=False)
    online_activity = Column(JSON, default={})
    payment_patterns = Column(JSON, default={})
    social_media_activity = Column(JSON, default={})
    digital_footprint_score = Column(Integer, nullable=True)
    behavioral_indicators = Column(JSON, default={})
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})

    # Relationships
    application = relationship("ConsumerApplication", back_populates="behavioral_data")


class ConsumerFraudIndicator(Base):
    """Consumer fraud indicator model."""
    __tablename__ = "consumer_fraud_indicators"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("consumer_applications.id", ondelete="CASCADE"), nullable=False)
    indicator_type = Column(String(50), nullable=False, index=True)
    severity = Column(SQLEnum(FraudSeverity), nullable=False, index=True)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, default={})
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})

    # Relationships
    application = relationship("ConsumerApplication", back_populates="fraud_indicators")


class BusinessApplication(Base):
    """Business credit application model."""
    __tablename__ = "business_applications"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True)
    company_name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(255), nullable=True)
    registration_number = Column(String(100), nullable=True, index=True)
    tax_id = Column(String(100), nullable=True, index=True)
    domain = Column(String(255), nullable=True, index=True)
    industry = Column(String(100), nullable=True, index=True)
    business_type = Column(String(50), nullable=True)  # llc, corporation, partnership, etc.
    founded_date = Column(DateTime(timezone=True), nullable=True)
    number_of_employees = Column(Integer, nullable=True)
    annual_revenue = Column(Float, nullable=True)
    requested_amount = Column(Float, nullable=True)
    loan_purpose = Column(Text, nullable=True)
    application_status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False, index=True)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    risk_scores = relationship("BusinessRiskScore", back_populates="application", cascade="all, delete-orphan")
    osint_data = relationship("BusinessOSINTData", back_populates="application", cascade="all, delete-orphan")
    financial_data = relationship("BusinessFinancialData", back_populates="application", cascade="all, delete-orphan")
    operational_data = relationship("BusinessOperationalData", back_populates="application", cascade="all, delete-orphan")
    fraud_indicators = relationship("BusinessFraudIndicator", back_populates="application", cascade="all, delete-orphan")


class BusinessRiskScore(Base):
    """Business risk score model."""
    __tablename__ = "business_risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("business_applications.id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Integer, nullable=True)  # 0-1000 scale
    osint_score = Column(Integer, nullable=True)
    financial_score = Column(Integer, nullable=True)
    operational_score = Column(Integer, nullable=True)
    industry_score = Column(Integer, nullable=True)
    management_score = Column(Integer, nullable=True)
    risk_tier = Column(SQLEnum(RiskTier), nullable=True, index=True)
    risk_level = Column(SQLEnum(RiskLevel), nullable=True, index=True)
    probability_of_default = Column(Float, nullable=True)
    recommended_interest_rate = Column(Float, nullable=True)
    recommended_loan_amount = Column(Float, nullable=True)
    recommended_term_months = Column(Integer, nullable=True)
    approval_recommendation = Column(String(20), nullable=True)  # approve, reject, manual_review
    score_components = Column(JSON, default={})
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})

    # Relationships
    application = relationship("BusinessApplication", back_populates="risk_scores")


class BusinessOSINTData(Base):
    """Business OSINT data model."""
    __tablename__ = "business_osint_data"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("business_applications.id", ondelete="CASCADE"), nullable=False)
    data_type = Column(String(50), nullable=False, index=True)  # domain, social_media, news, reviews, etc.
    source = Column(String(100), nullable=False)
    data = Column(JSON, nullable=False)
    risk_signals = Column(JSON, default={})
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})

    # Relationships
    application = relationship("BusinessApplication", back_populates="osint_data")


class BusinessFinancialData(Base):
    """Business financial data model."""
    __tablename__ = "business_financial_data"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("business_applications.id", ondelete="CASCADE"), nullable=False)
    balance_sheet = Column(JSON, default={})
    income_statement = Column(JSON, default={})
    cash_flow_statement = Column(JSON, default={})
    financial_ratios = Column(JSON, default={})
    credit_history = Column(JSON, default={})
    trade_references = Column(JSON, default={})
    bank_statements = Column(JSON, default={})
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})

    # Relationships
    application = relationship("BusinessApplication", back_populates="financial_data")


class BusinessOperationalData(Base):
    """Business operational data model."""
    __tablename__ = "business_operational_data"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("business_applications.id", ondelete="CASCADE"), nullable=False)
    management_team = Column(JSON, default={})
    business_model = Column(Text, nullable=True)
    market_position = Column(String(50), nullable=True)
    competitive_analysis = Column(JSON, default={})
    operational_metrics = Column(JSON, default={})
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})

    # Relationships
    application = relationship("BusinessApplication", back_populates="operational_data")


class BusinessFraudIndicator(Base):
    """Business fraud indicator model."""
    __tablename__ = "business_fraud_indicators"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("business_applications.id", ondelete="CASCADE"), nullable=False)
    indicator_type = Column(String(50), nullable=False, index=True)
    severity = Column(SQLEnum(FraudSeverity), nullable=False, index=True)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, default={})
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, default={})

    # Relationships
    application = relationship("BusinessApplication", back_populates="fraud_indicators")
