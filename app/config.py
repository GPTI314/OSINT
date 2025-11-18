"""
Application configuration management
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
import secrets


class Settings(BaseSettings):
    """Application settings with security defaults"""

    # Application
    APP_NAME: str = "OSINT Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    API_KEY_EXPIRE_DAYS: int = 365

    # Encryption (AES-256)
    ENCRYPTION_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    DATA_ENCRYPTION_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://osint_user:osint_password@localhost:5432/osint_db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_DB: int = 0
    REDIS_CACHE_DB: int = 1
    SESSION_EXPIRE_SECONDS: int = 3600

    # OAuth2
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/osint.log"
    AUDIT_LOG_FILE: str = "logs/audit.log"
    LOG_ROTATION: str = "midnight"
    LOG_RETENTION_DAYS: int = 90

    # Data Retention
    DATA_RETENTION_DAYS: int = 365
    PII_RETENTION_DAYS: int = 90
    AUDIT_LOG_RETENTION_DAYS: int = 730

    # Ethical Scraping
    RESPECT_ROBOTS_TXT: bool = True
    DEFAULT_CRAWL_DELAY: float = 1.0
    MAX_REQUESTS_PER_DOMAIN: int = 100
    USER_AGENT: str = "OSINTBot/1.0 (Ethical Research)"

    # Security Headers
    ENABLE_HSTS: bool = True
    HSTS_MAX_AGE: int = 31536000
    ENABLE_CSP: bool = True
    CSP_POLICY: str = "default-src 'self'"

    # Password Policy
    MIN_PASSWORD_LENGTH: int = 12
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_DIGITS: bool = True
    REQUIRE_SPECIAL_CHARS: bool = True
    PASSWORD_HISTORY_COUNT: int = 5

    # Account Security
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = 30
    REQUIRE_EMAIL_VERIFICATION: bool = True
    ENABLE_2FA: bool = True

    # PII Protection
    ENABLE_PII_ENCRYPTION: bool = True
    ENABLE_PII_MASKING: bool = True
    PII_FIELDS: List[str] = ["email", "phone", "ssn", "passport", "credit_card"]

    # Compliance
    GDPR_ENABLED: bool = True
    CCPA_ENABLED: bool = True
    DATA_EXPORT_FORMAT: str = "json"

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("PII_FIELDS", pre=True)
    def parse_pii_fields(cls, v):
        if isinstance(v, str):
            return [field.strip() for field in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
