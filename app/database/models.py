"""
Database models for users, roles, permissions, and audit logging
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .base import Base


# Association tables for many-to-many relationships
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'))
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE')),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'))
)


class User(Base):
    """User model with secure authentication"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # Security fields
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=func.now())
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 compatible

    # 2FA
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)

    # OAuth2
    oauth_provider = Column(String(50), nullable=True)
    oauth_id = Column(String(255), nullable=True)

    # PII (encrypted)
    phone = Column(String(255), nullable=True)
    encrypted_data = Column(JSON, nullable=True)  # Store additional encrypted PII

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class Role(Base):
    """Role model for RBAC"""
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    is_system = Column(Boolean, default=False)  # System roles cannot be deleted

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"


class Permission(Base):
    """Permission model for fine-grained access control"""
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    resource = Column(String(100), nullable=False)  # e.g., 'user', 'report', 'investigation'
    action = Column(String(50), nullable=False)  # e.g., 'create', 'read', 'update', 'delete'
    description = Column(String(255))

    created_at = Column(DateTime, default=func.now())

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name})>"


class APIKey(Base):
    """API Key model for programmatic access"""
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    name = Column(String(100), nullable=False)  # User-friendly name
    key_hash = Column(String(255), unique=True, nullable=False)  # Hashed API key
    key_prefix = Column(String(10), nullable=False)  # First few chars for identification

    # Permissions and scopes
    scopes = Column(JSON, default=list)  # List of allowed scopes

    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    last_used_ip = Column(String(45), nullable=True)

    # Rate limiting
    rate_limit = Column(Integer, nullable=True)  # Custom rate limit for this key

    created_at = Column(DateTime, default=func.now())
    revoked_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<APIKey(id={self.id}, name={self.name}, prefix={self.key_prefix})>"


class Session(Base):
    """Session model for tracking user sessions"""
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token = Column(String(255), unique=True, nullable=True)

    # Session metadata
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    device_info = Column(JSON)

    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=func.now())
    last_activity_at = Column(DateTime, default=func.now())
    revoked_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id})>"


class AuditLog(Base):
    """Audit log for tracking all security-relevant actions"""
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Action details
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), index=True)
    resource_id = Column(String(100), index=True)
    status = Column(String(20), nullable=False)  # success, failure, denied

    # Request details
    method = Column(String(10))  # HTTP method
    endpoint = Column(String(500))
    ip_address = Column(String(45), index=True)
    user_agent = Column(String(500))

    # Data
    request_data = Column(JSON)  # Sanitized request data
    response_data = Column(JSON)  # Sanitized response data
    changes = Column(JSON)  # Before/after for updates
    error_message = Column(Text)

    # Additional metadata
    session_id = Column(String(255))
    api_key_id = Column(Integer, nullable=True)
    duration_ms = Column(Integer)  # Request duration

    # Compliance
    pii_accessed = Column(Boolean, default=False)
    data_exported = Column(Boolean, default=False)

    timestamp = Column(DateTime, default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, status={self.status})>"


class PasswordHistory(Base):
    """Track password history to prevent reuse"""
    __tablename__ = 'password_history'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<PasswordHistory(id={self.id}, user_id={self.user_id})>"
