"""
Pytest configuration for E2E tests using Playwright.
"""

import pytest
from typing import Generator
from playwright.sync_api import Page, BrowserContext, Browser


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context."""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create a new browser context for each test."""
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture(scope="function")
def authenticated_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create authenticated browser context."""
    context = browser.new_context()

    # Set authentication cookies/tokens
    # context.add_cookies([...])

    yield context
    context.close()


@pytest.fixture
def base_url() -> str:
    """Base URL for the application."""
    return "http://localhost:8000"


@pytest.fixture
def api_base_url() -> str:
    """Base URL for API."""
    return "http://localhost:8000/api/v1"


@pytest.fixture
def test_user_credentials():
    """Test user credentials."""
    return {
        "username": "test_user",
        "password": "test_password_123",
        "email": "test@example.com",
    }
