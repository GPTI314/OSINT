# Testing Documentation

## Quick Start

```bash
# Install dependencies
pip install -r requirements-dev.txt
playwright install

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest tests/unit -m unit
pytest tests/integration -m integration
pytest tests/e2e -m e2e
```

## Test Coverage Target: 80%+

This project maintains **80% minimum code coverage**. Coverage reports are generated automatically in CI/CD and can be viewed locally:

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Test Categories

### Unit Tests (tests/unit/)
- **Coverage**: 60% of test suite
- **Speed**: Fast (< 1s per test)
- **Dependencies**: None (heavily mocked)
- **Purpose**: Test individual components

### Integration Tests (tests/integration/)
- **Coverage**: 30% of test suite
- **Speed**: Moderate (1-10s per test)
- **Dependencies**: Database, Redis, external APIs
- **Purpose**: Test component interactions

### E2E Tests (tests/e2e/)
- **Coverage**: 10% of test suite
- **Speed**: Slow (10-60s per test)
- **Dependencies**: Full application stack
- **Purpose**: Test user workflows

## Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit           # Unit test
@pytest.mark.integration    # Integration test
@pytest.mark.e2e            # End-to-end test
@pytest.mark.slow           # Slow running test
@pytest.mark.requires_db    # Requires database
@pytest.mark.requires_redis # Requires Redis
```

Run tests by marker:
```bash
pytest -m unit
pytest -m "integration and not slow"
pytest -m "not requires_external_api"
```

## Writing Tests

### Test Structure (AAA Pattern)

```python
def test_example():
    # Arrange
    collector = DNSCollector()
    domain = "example.com"

    # Act
    result = collector.collect(domain)

    # Assert
    assert result["status"] == "success"
```

### Using Fixtures

```python
def test_with_database(db_session, sample_entity_data):
    entity = Entity(**sample_entity_data)
    db_session.add(entity)
    db_session.commit()
    assert entity.id is not None
```

### Mocking

```python
@pytest.mark.asyncio
async def test_with_mock(mock_shodan_api):
    collector = ShodanCollector(api=mock_shodan_api)
    result = await collector.collect("8.8.8.8")
    mock_shodan_api.host.assert_called_once()
```

## CI/CD

### Workflows

1. **tests.yml** - Runs on every push/PR
2. **nightly-tests.yml** - Comprehensive nightly tests
3. **pr-checks.yml** - Fast PR validation

### Local CI Simulation

```bash
# Run what CI runs
pytest tests/ --cov=src --cov-fail-under=80 -n auto
black --check src tests
ruff check src tests
```

## Common Commands

```bash
# Run fast tests
pytest -m "not slow"

# Run with verbose output
pytest -v

# Run specific file
pytest tests/unit/test_collectors.py

# Run specific test
pytest tests/unit/test_collectors.py::test_dns_collector

# Run in parallel
pytest -n auto

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Update snapshots (if using pytest-snapshot)
pytest --snapshot-update
```

## Coverage Tips

### View Uncovered Lines
```bash
pytest --cov=src --cov-report=term-missing
```

### Focus on Specific Module
```bash
pytest --cov=src.collectors --cov-report=html tests/unit/test_collectors.py
```

### Branch Coverage
```bash
pytest --cov=src --cov-branch
```

## Debugging Tests

### Use pdb
```python
def test_example():
    import pdb; pdb.set_trace()
    # ... test code
```

### Run with pdb on failure
```bash
pytest --pdb
```

### Show full diff for assertion failures
```bash
pytest -vv
```

### Capture output
```bash
pytest -s  # Show print statements
pytest --log-cli-level=DEBUG  # Show logs
```

## Best Practices

1. ✅ Write tests before code (TDD)
2. ✅ One logical assertion per test
3. ✅ Use descriptive test names
4. ✅ Keep tests independent
5. ✅ Use fixtures over setup/teardown
6. ✅ Test edge cases and error conditions
7. ✅ Mock external dependencies
8. ✅ Maintain 80%+ coverage
9. ✅ Run tests before committing
10. ✅ Update tests with code changes

## Resources

- [Full Testing Guide](tests/README.md)
- [pytest Documentation](https://docs.pytest.org/)
- [Playwright Python](https://playwright.dev/python/)
- [Coverage.py](https://coverage.readthedocs.io/)
