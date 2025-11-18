"""Application settings and configuration management."""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="OSINT Intelligence Platform")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1")
    cors_origins: str = Field(default="http://localhost:3000")

    # PostgreSQL
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="osint_platform")
    postgres_user: str = Field(default="osint_user")
    postgres_password: str = Field(default="changeme")
    database_url: Optional[str] = Field(default=None)

    # MongoDB
    mongo_host: str = Field(default="localhost")
    mongo_port: int = Field(default=27017)
    mongo_db: str = Field(default="osint_platform")
    mongo_user: str = Field(default="osint_user")
    mongo_password: str = Field(default="changeme")
    mongodb_url: Optional[str] = Field(default=None)

    # Redis
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: str = Field(default="")
    redis_url: Optional[str] = Field(default=None)

    # Elasticsearch
    elasticsearch_host: str = Field(default="localhost")
    elasticsearch_port: int = Field(default=9200)
    elasticsearch_url: Optional[str] = Field(default=None)

    # Celery
    celery_broker_url: Optional[str] = Field(default=None)
    celery_result_backend: Optional[str] = Field(default=None)
    celery_task_track_started: bool = Field(default=True)
    celery_task_time_limit: int = Field(default=3600)
    celery_task_soft_time_limit: int = Field(default=3000)

    # Security
    secret_key: str = Field(default="changeme")
    jwt_secret_key: str = Field(default="changeme")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    encryption_key: str = Field(default="changeme")

    # OAuth2
    google_client_id: Optional[str] = Field(default=None)
    google_client_secret: Optional[str] = Field(default=None)
    github_client_id: Optional[str] = Field(default=None)
    github_client_secret: Optional[str] = Field(default=None)

    # Third Party API Keys
    shodan_api_key: Optional[str] = Field(default=None)
    censys_api_id: Optional[str] = Field(default=None)
    censys_api_secret: Optional[str] = Field(default=None)
    virustotal_api_key: Optional[str] = Field(default=None)
    ipinfo_api_key: Optional[str] = Field(default=None)
    hunter_io_api_key: Optional[str] = Field(default=None)
    clearbit_api_key: Optional[str] = Field(default=None)
    full_contact_api_key: Optional[str] = Field(default=None)

    # Scraping Configuration
    max_concurrent_requests: int = Field(default=10)
    request_timeout: int = Field(default=30)
    max_retries: int = Field(default=3)
    retry_delay: int = Field(default=5)
    user_agent_rotation: bool = Field(default=True)
    proxy_rotation: bool = Field(default=True)

    # Proxy Configuration
    proxy_enabled: bool = Field(default=False)
    proxy_list_url: Optional[str] = Field(default=None)
    http_proxy: Optional[str] = Field(default=None)
    https_proxy: Optional[str] = Field(default=None)
    socks_proxy: Optional[str] = Field(default=None)

    # CAPTCHA
    captcha_solver: str = Field(default="2captcha")
    captcha_api_key: Optional[str] = Field(default=None)

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_per_minute: int = Field(default=60)
    rate_limit_per_hour: int = Field(default=1000)

    # Monitoring
    prometheus_enabled: bool = Field(default=True)
    prometheus_port: int = Field(default=9090)
    grafana_enabled: bool = Field(default=True)
    grafana_port: int = Field(default=3001)

    # Logging
    log_format: str = Field(default="json")
    log_file_enabled: bool = Field(default=True)
    log_file_path: str = Field(default="./logs/osint-platform.log")
    log_file_max_size: int = Field(default=10485760)
    log_file_backup_count: int = Field(default=5)

    # ELK Stack
    elk_enabled: bool = Field(default=False)
    logstash_host: str = Field(default="localhost")
    logstash_port: int = Field(default=5000)
    kibana_url: str = Field(default="http://localhost:5601")

    # Sentry
    sentry_enabled: bool = Field(default=False)
    sentry_dsn: Optional[str] = Field(default=None)

    # Feature Flags
    feature_social_intelligence: bool = Field(default=True)
    feature_image_intelligence: bool = Field(default=True)
    feature_threat_intelligence: bool = Field(default=True)
    feature_dark_web_monitoring: bool = Field(default=False)
    feature_real_time_alerts: bool = Field(default=True)

    # Storage
    storage_type: str = Field(default="local")
    storage_path: str = Field(default="./storage")
    s3_bucket: Optional[str] = Field(default=None)
    s3_region: Optional[str] = Field(default=None)
    s3_access_key: Optional[str] = Field(default=None)
    s3_secret_key: Optional[str] = Field(default=None)

    # Email
    email_enabled: bool = Field(default=False)
    smtp_host: Optional[str] = Field(default=None)
    smtp_port: int = Field(default=587)
    smtp_user: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)
    smtp_from: Optional[str] = Field(default=None)

    # WebSocket
    websocket_enabled: bool = Field(default=True)
    websocket_path: str = Field(default="/ws")

    # Performance
    max_workers: int = Field(default=4)
    worker_class: str = Field(default="uvicorn.workers.UvicornWorker")
    worker_connections: int = Field(default=1000)
    keepalive: int = Field(default=5)

    # Security Headers
    security_headers_enabled: bool = Field(default=True)
    hsts_enabled: bool = Field(default=True)
    hsts_max_age: int = Field(default=31536000)

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_url(cls, v, info):
        """Assemble PostgreSQL database URL if not provided."""
        if v:
            return v
        data = info.data
        return (
            f"postgresql+asyncpg://{data.get('postgres_user')}:"
            f"{data.get('postgres_password')}@{data.get('postgres_host')}:"
            f"{data.get('postgres_port')}/{data.get('postgres_db')}"
        )

    @field_validator("mongodb_url", mode="before")
    @classmethod
    def assemble_mongo_url(cls, v, info):
        """Assemble MongoDB URL if not provided."""
        if v:
            return v
        data = info.data
        return (
            f"mongodb://{data.get('mongo_user')}:{data.get('mongo_password')}"
            f"@{data.get('mongo_host')}:{data.get('mongo_port')}/{data.get('mongo_db')}"
        )

    @field_validator("redis_url", mode="before")
    @classmethod
    def assemble_redis_url(cls, v, info):
        """Assemble Redis URL if not provided."""
        if v:
            return v
        data = info.data
        password = data.get('redis_password')
        if password:
            return (
                f"redis://:{password}@{data.get('redis_host')}:"
                f"{data.get('redis_port')}/{data.get('redis_db')}"
            )
        return (
            f"redis://{data.get('redis_host')}:{data.get('redis_port')}/"
            f"{data.get('redis_db')}"
        )

    @field_validator("elasticsearch_url", mode="before")
    @classmethod
    def assemble_elasticsearch_url(cls, v, info):
        """Assemble Elasticsearch URL if not provided."""
        if v:
            return v
        data = info.data
        return f"http://{data.get('elasticsearch_host')}:{data.get('elasticsearch_port')}"

    @field_validator("celery_broker_url", mode="before")
    @classmethod
    def assemble_celery_broker_url(cls, v, info):
        """Use Redis URL for Celery broker if not provided."""
        if v:
            return v
        return info.data.get('redis_url')

    @field_validator("celery_result_backend", mode="before")
    @classmethod
    def assemble_celery_result_backend(cls, v, info):
        """Use Redis URL for Celery result backend if not provided."""
        if v:
            return v
        return info.data.get('redis_url')

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
