"""
Pytest configuration and shared fixtures for OSINT Toolkit tests.

This module provides fixtures for:
- Database setup and teardown
- Mock external API responses
- Test data factories
- Authentication/authorization mocks
"""

import asyncio
import os
from typing import AsyncGenerator, Dict, Generator, Any
from unittest.mock import Mock, AsyncMock

import pytest
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Mock imports for non-existent modules (will be replaced when actual code exists)
# from src.database.models import Base
# from src.api.app import app
# from src.utils.config import Settings

fake = Faker()


# ============================================================================
# Session-scoped fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Dict[str, Any]:
    """Provide test configuration settings."""
    return {
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/1",
        "API_KEY_SHODAN": "test_shodan_key",
        "API_KEY_CENSYS": "test_censys_key",
        "API_KEY_VIRUSTOTAL": "test_virustotal_key",
        "DEBUG": True,
        "TESTING": True,
        "LOG_LEVEL": "DEBUG",
    }


# ============================================================================
# Database fixtures
# ============================================================================

@pytest.fixture(scope="function")
def db_engine(test_settings):
    """Create a test database engine."""
    engine = create_engine(
        test_settings["DATABASE_URL"],
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Base.metadata.create_all(bind=engine)
    yield engine
    # Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
async def async_db_session(db_engine) -> AsyncGenerator:
    """Create an async test database session."""
    # For SQLAlchemy async session
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    async_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    async with AsyncSession(async_engine) as session:
        yield session

    await async_engine.dispose()


# ============================================================================
# Mock external services
# ============================================================================

@pytest.fixture
def mock_shodan_api():
    """Mock Shodan API client."""
    mock = Mock()
    mock.host.return_value = {
        "ip_str": "8.8.8.8",
        "org": "Google LLC",
        "data": [
            {
                "port": 53,
                "transport": "udp",
                "product": "Google DNS",
            }
        ],
        "ports": [53, 443],
        "vulns": [],
    }
    return mock


@pytest.fixture
def mock_virustotal_api():
    """Mock VirusTotal API client."""
    mock = AsyncMock()
    mock.get_ip_report.return_value = {
        "response_code": 1,
        "detected_urls": [],
        "detected_communicating_samples": [],
        "detected_downloaded_samples": [],
        "resolutions": [
            {"last_resolved": "2024-01-01", "hostname": "example.com"}
        ],
    }
    return mock


@pytest.fixture
def mock_whois_service():
    """Mock WHOIS service."""
    mock = Mock()
    mock.lookup.return_value = {
        "domain_name": "example.com",
        "registrar": "Example Registrar Inc.",
        "creation_date": "2000-01-01",
        "expiration_date": "2025-01-01",
        "name_servers": ["ns1.example.com", "ns2.example.com"],
    }
    return mock


@pytest.fixture
def mock_dns_resolver():
    """Mock DNS resolver."""
    mock = Mock()
    mock.resolve.return_value = [
        Mock(address="93.184.216.34"),
    ]
    return mock


@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    mock = AsyncMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = 1
    mock.exists.return_value = False
    return mock


# ============================================================================
# Test data factories
# ============================================================================

@pytest.fixture
def sample_ip_address() -> str:
    """Generate a sample IP address."""
    return fake.ipv4()


@pytest.fixture
def sample_domain() -> str:
    """Generate a sample domain name."""
    return fake.domain_name()


@pytest.fixture
def sample_email() -> str:
    """Generate a sample email address."""
    return fake.email()


@pytest.fixture
def sample_url() -> str:
    """Generate a sample URL."""
    return fake.url()


@pytest.fixture
def sample_entity_data() -> Dict[str, Any]:
    """Generate sample entity data."""
    return {
        "entity_type": "ip_address",
        "value": fake.ipv4(),
        "metadata": {
            "first_seen": fake.date_time_this_year().isoformat(),
            "last_seen": fake.date_time_this_month().isoformat(),
            "source": "test",
        },
        "tags": ["test", "sample"],
    }


@pytest.fixture
def sample_collection_result() -> Dict[str, Any]:
    """Generate sample collection result."""
    return {
        "collector_name": "dns_collector",
        "target": "example.com",
        "timestamp": fake.date_time_this_month().isoformat(),
        "status": "success",
        "data": {
            "A": ["93.184.216.34"],
            "MX": ["mail.example.com"],
            "NS": ["ns1.example.com", "ns2.example.com"],
        },
        "metadata": {
            "execution_time": 1.23,
            "errors": [],
        },
    }


@pytest.fixture
def sample_risk_score() -> Dict[str, Any]:
    """Generate sample risk score data."""
    return {
        "entity_id": fake.uuid4(),
        "score": fake.random_int(min=0, max=100),
        "factors": {
            "malware_detected": False,
            "blacklist_count": 0,
            "ssl_issues": False,
            "reputation_score": 85,
        },
        "severity": "low",
        "timestamp": fake.date_time_this_month().isoformat(),
    }


@pytest.fixture
def sample_graph_data() -> Dict[str, Any]:
    """Generate sample graph/relationship data."""
    return {
        "nodes": [
            {"id": "1", "type": "ip", "value": "8.8.8.8"},
            {"id": "2", "type": "domain", "value": "google.com"},
            {"id": "3", "type": "domain", "value": "dns.google"},
        ],
        "edges": [
            {"source": "2", "target": "1", "relationship": "resolves_to"},
            {"source": "3", "target": "1", "relationship": "resolves_to"},
        ],
    }


@pytest.fixture
def sample_workflow_definition() -> Dict[str, Any]:
    """Generate sample workflow definition."""
    return {
        "name": "IP Investigation",
        "description": "Comprehensive IP address investigation",
        "tasks": [
            {
                "id": "collect_whois",
                "collector": "whois_collector",
                "params": {"target": "${input.ip}"},
            },
            {
                "id": "collect_shodan",
                "collector": "shodan_collector",
                "params": {"target": "${input.ip}"},
                "depends_on": ["collect_whois"],
            },
            {
                "id": "analyze_risk",
                "analyzer": "risk_scorer",
                "params": {"entity_id": "${collect_whois.entity_id}"},
                "depends_on": ["collect_whois", "collect_shodan"],
            },
        ],
        "output": {
            "whois": "${collect_whois.result}",
            "shodan": "${collect_shodan.result}",
            "risk_score": "${analyze_risk.score}",
        },
    }


# ============================================================================
# API testing fixtures
# ============================================================================

@pytest.fixture
def api_client():
    """Create a test API client."""
    from fastapi.testclient import TestClient
    # from src.api.app import app

    # Mock app for now
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/health")
    def health_check():
        return {"status": "healthy"}

    client = TestClient(app)
    return client


@pytest.fixture
async def async_api_client():
    """Create an async test API client."""
    from httpx import AsyncClient
    # from src.api.app import app

    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/health")
    def health_check():
        return {"status": "healthy"}

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Generate authentication headers for API tests."""
    return {
        "Authorization": "Bearer test_token_12345",
        "Content-Type": "application/json",
    }


# ============================================================================
# Mock collectors
# ============================================================================

@pytest.fixture
def mock_dns_collector():
    """Mock DNS collector."""
    mock = AsyncMock()
    mock.collect.return_value = {
        "status": "success",
        "data": {
            "A": ["93.184.216.34"],
            "AAAA": ["2606:2800:220:1:248:1893:25c8:1946"],
            "MX": [{"priority": 10, "host": "mail.example.com"}],
            "NS": ["ns1.example.com", "ns2.example.com"],
            "TXT": ["v=spf1 include:_spf.example.com ~all"],
        },
    }
    return mock


@pytest.fixture
def mock_whois_collector():
    """Mock WHOIS collector."""
    mock = AsyncMock()
    mock.collect.return_value = {
        "status": "success",
        "data": {
            "domain_name": "example.com",
            "registrar": "Example Registrar Inc.",
            "creation_date": "2000-01-01T00:00:00",
            "expiration_date": "2025-01-01T00:00:00",
            "registrant": {
                "organization": "Example Organization",
                "country": "US",
            },
        },
    }
    return mock


# ============================================================================
# Utility fixtures
# ============================================================================

@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test content")
    return file_path


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)
