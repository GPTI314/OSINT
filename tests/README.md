# OSINT Toolkit Testing Guide

Comprehensive testing documentation for the OSINT Toolkit project.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Types](#test-types)
- [Writing Tests](#writing-tests)
- [Coverage Requirements](#coverage-requirements)
- [Best Practices](#best-practices)
- [CI/CD Integration](#cicd-integration)

## Overview

This project maintains a comprehensive test suite with **80%+ code coverage** requirement. Our testing strategy includes:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions and external services
- **E2E Tests**: Test complete user workflows using Playwright

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── fixtures/                # Test data and factories
├── unit/                    # Unit tests (60% of tests)
│   ├── test_collectors.py
│   ├── test_enrichment.py
│   ├── test_analysis.py
│   ├── test_scoring.py
│   ├── test_workflow.py
│   └── test_api.py
├── integration/             # Integration tests (30% of tests)
│   ├── test_api_integration.py
│   ├── test_database_integration.py
│   └── test_service_integration.py
└── e2e/                     # End-to-end tests (10% of tests)
    ├── conftest.py
    └── test_user_flows.py
```

## Running Tests

### Prerequisites

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install Playwright browsers (for E2E tests)
playwright install
```

### Run All Tests

```bash
# Run entire test suite
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v
```

### Run Specific Test Types

```bash
# Unit tests only
pytest tests/unit -m unit

# Integration tests only
pytest tests/integration -m integration

# E2E tests only
pytest tests/e2e -m e2e

# Run tests excluding slow tests
pytest -m "not slow"
```

### Run Specific Test Files

```bash
# Run specific test file
pytest tests/unit/test_collectors.py

# Run specific test class
pytest tests/unit/test_collectors.py::TestDNSCollector

# Run specific test method
pytest tests/unit/test_collectors.py::TestDNSCollector::test_collect_a_records
```

### Run Tests in Parallel

```bash
# Run tests in parallel using pytest-xdist
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

## Test Types

### Unit Tests

**Purpose**: Test individual functions, methods, and classes in isolation.

**Characteristics**:
- Fast execution (< 1 second per test)
- No external dependencies
- Heavy use of mocking
- 60% of total test suite

**Example**:
```python
@pytest.mark.unit
def test_validate_ip_address(sample_ip_address):
    validator = IPValidator()
    assert validator.validate(sample_ip_address) is True
```

**Markers**:
- `@pytest.mark.unit` - Mark as unit test
- `@pytest.mark.slow` - Mark slow tests (skip in quick runs)

### Integration Tests

**Purpose**: Test interactions between components and external services.

**Characteristics**:
- Moderate execution time (1-10 seconds)
- May require database, Redis, or other services
- Tests real interactions with minimal mocking
- 30% of total test suite

**Example**:
```python
@pytest.mark.integration
@pytest.mark.requires_db
async def test_collector_to_database(db_session, mock_dns_collector):
    result = await mock_dns_collector.collect("example.com")
    stored = await db_session.save(result)
    assert stored.id is not None
```

**Markers**:
- `@pytest.mark.integration` - Mark as integration test
- `@pytest.mark.requires_db` - Requires database
- `@pytest.mark.requires_redis` - Requires Redis
- `@pytest.mark.requires_external_api` - Requires external API

### E2E Tests

**Purpose**: Test complete user workflows through the browser.

**Characteristics**:
- Slower execution (10-60 seconds)
- Tests real user interactions
- Uses Playwright for browser automation
- 10% of total test suite

**Example**:
```python
@pytest.mark.e2e
def test_complete_investigation_journey(page: Page, base_url: str):
    page.goto(f"{base_url}/login")
    page.fill("input[name='username']", "test_user")
    page.click("button[type='submit']")
    # ... complete workflow
    expect(page.locator(".report-preview")).to_be_visible()
```

**Markers**:
- `@pytest.mark.e2e` - Mark as E2E test
- `@pytest.mark.slow` - Long-running E2E tests

## Writing Tests

### Test Structure

Follow the **Arrange-Act-Assert (AAA)** pattern:

```python
def test_example():
    # Arrange: Set up test data and dependencies
    collector = DNSCollector()
    domain = "example.com"

    # Act: Execute the code being tested
    result = collector.collect(domain)

    # Assert: Verify the results
    assert result["status"] == "success"
    assert "A" in result["data"]
```

### Using Fixtures

```python
def test_with_fixtures(db_session, sample_entity_data):
    """Use fixtures for setup and test data."""
    entity = Entity(**sample_entity_data)
    db_session.add(entity)
    db_session.commit()

    retrieved = db_session.query(Entity).filter_by(id=entity.id).first()
    assert retrieved is not None
```

### Mocking External Services

```python
from unittest.mock import Mock, AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mocking(mock_shodan_api):
    """Mock external API calls."""
    collector = ShodanCollector(api=mock_shodan_api)
    result = await collector.collect_ip("8.8.8.8")

    mock_shodan_api.host.assert_called_once_with("8.8.8.8")
    assert "ip_str" in result
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async functions."""
    result = await async_function()
    assert result is not None
```

### Parameterized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("8.8.8.8", True),
    ("256.256.256.256", False),
    ("invalid", False),
])
def test_ip_validation(input, expected):
    validator = IPValidator()
    assert validator.validate(input) == expected
```

## Coverage Requirements

### Minimum Coverage: 80%

```bash
# Check coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Generate HTML coverage report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Coverage Exclusions

Excluded from coverage (in `pyproject.toml`):
- Test files (`*/tests/*`)
- Database migrations (`*/migrations/*`)
- `__init__.py` files
- Abstract methods
- Debug code

### Branch Coverage

Branch coverage is enabled to ensure all code paths are tested:

```bash
pytest --cov=src --cov-branch
```

## Best Practices

### 1. Test Naming

```python
# Good: Descriptive test names
def test_dns_collector_returns_a_records_for_valid_domain():
    pass

# Bad: Vague test names
def test_dns():
    pass
```

### 2. One Assert Per Test (When Possible)

```python
# Good: Single logical assertion
def test_user_creation():
    user = create_user("test@example.com")
    assert user.email == "test@example.com"

# Acceptable: Multiple related assertions
def test_user_full_attributes():
    user = create_user("test@example.com")
    assert user.email == "test@example.com"
    assert user.created_at is not None
    assert user.is_active is True
```

### 3. Test Independence

```python
# Good: Each test is independent
def test_create_entity():
    entity = Entity(name="test")
    assert entity.name == "test"

def test_update_entity():
    entity = Entity(name="test")
    entity.name = "updated"
    assert entity.name == "updated"

# Bad: Tests depend on each other
entity = None

def test_create():
    global entity
    entity = Entity(name="test")

def test_update():  # Depends on test_create
    entity.name = "updated"
    assert entity.name == "updated"
```

### 4. Use Fixtures Over Setup/Teardown

```python
# Good: Use fixtures
@pytest.fixture
def database():
    db = create_db()
    yield db
    db.close()

def test_with_db(database):
    result = database.query("SELECT 1")
    assert result is not None

# Avoid: setUp/tearDown methods
class TestDatabase:
    def setUp(self):
        self.db = create_db()

    def tearDown(self):
        self.db.close()
```

### 5. Test Edge Cases

```python
def test_edge_cases():
    validator = Validator()

    # Test empty input
    assert validator.validate("") is False

    # Test None
    assert validator.validate(None) is False

    # Test maximum length
    assert validator.validate("a" * 1000) is True

    # Test boundary conditions
    assert validator.validate("a" * 1001) is False
```

### 6. Clear Test Data

```python
# Good: Clear, readable test data
def test_user_serialization():
    user = User(
        username="john_doe",
        email="john@example.com",
        age=30
    )
    data = user.to_dict()
    assert data["username"] == "john_doe"

# Bad: Unclear test data
def test_user():
    u = User("jd", "j@e.c", 30)
    d = u.td()
    assert d["u"] == "jd"
```

## CI/CD Integration

### GitHub Actions Workflows

#### 1. **tests.yml** - Main test workflow
- Runs on push and pull requests
- Executes unit, integration, and E2E tests
- Uploads coverage reports
- Runs code quality checks

#### 2. **nightly-tests.yml** - Comprehensive nightly tests
- Runs complete test suite including slow tests
- Performance benchmarks
- Stress tests
- Scheduled daily at 2 AM UTC

#### 3. **pr-checks.yml** - Quick PR validation
- Fast unit tests for immediate feedback
- Code style validation
- Coverage check
- Tests across Python versions

### Running Tests Locally Like CI

```bash
# Simulate PR checks
pytest tests/unit -m "unit and not slow" -x --maxfail=5

# Simulate full CI test run
pytest tests/ --cov=src --cov-report=term-missing -n auto

# Check code quality
black --check src tests
ruff check src tests
mypy src
```

## Troubleshooting

### Common Issues

#### Tests Fail with Database Errors
```bash
# Ensure PostgreSQL is running
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15

# Set DATABASE_URL
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/osint_test
```

#### Tests Fail with Redis Errors
```bash
# Ensure Redis is running
docker run -d -p 6379:6379 redis:7

# Set REDIS_URL
export REDIS_URL=redis://localhost:6379/0
```

#### Playwright Tests Fail
```bash
# Reinstall browsers
playwright install --with-deps

# Run with headed mode for debugging
pytest tests/e2e --headed
```

#### Coverage Not Reaching 80%
```bash
# Generate detailed coverage report
pytest --cov=src --cov-report=html

# Open htmlcov/index.html to see uncovered lines
# Add tests for uncovered code
```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Playwright Python Documentation](https://playwright.dev/python/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure 80%+ coverage for new code
3. Add appropriate test markers
4. Update this documentation if needed
5. Run full test suite before submitting PR

```bash
# Before submitting PR
pytest --cov=src --cov-fail-under=80
black src tests
ruff check src tests
```
