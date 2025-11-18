.PHONY: help install test test-unit test-integration test-e2e test-fast test-all coverage clean format lint type-check

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

install-e2e:  ## Install E2E test dependencies
	pip install playwright pytest-playwright
	playwright install --with-deps

test:  ## Run all tests
	pytest tests/ -v

test-unit:  ## Run unit tests only
	pytest tests/unit -v -m unit

test-integration:  ## Run integration tests only
	pytest tests/integration -v -m integration

test-e2e:  ## Run E2E tests only
	pytest tests/e2e -v -m e2e

test-fast:  ## Run fast tests (exclude slow tests)
	pytest tests/ -v -m "not slow"

test-all:  ## Run all tests including slow tests
	pytest tests/ -v -n auto

coverage:  ## Run tests with coverage report
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "\nCoverage report generated in htmlcov/index.html"

coverage-unit:  ## Coverage for unit tests only
	pytest tests/unit --cov=src --cov-report=html --cov-report=term-missing

coverage-check:  ## Check if coverage meets 80% requirement
	pytest tests/ --cov=src --cov-fail-under=80

watch:  ## Run tests in watch mode
	pytest-watch tests/

clean:  ## Clean up generated files
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf test-results/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

format:  ## Format code with Black
	black src tests

format-check:  ## Check code formatting
	black --check src tests

lint:  ## Lint code with Ruff
	ruff check src tests

lint-fix:  ## Lint and auto-fix issues
	ruff check --fix src tests

type-check:  ## Run type checking with mypy
	mypy src

quality:  ## Run all code quality checks
	@echo "Checking code formatting..."
	@make format-check
	@echo "\nLinting code..."
	@make lint
	@echo "\nType checking..."
	@make type-check

ci:  ## Run CI checks locally
	@echo "Running CI checks..."
	@make format-check
	@make lint
	@make test-fast
	@make coverage-check

pre-commit:  ## Run pre-commit checks
	pre-commit run --all-files

setup-hooks:  ## Set up git hooks
	pre-commit install

# Docker commands
docker-test:  ## Run tests in Docker
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit

docker-clean:  ## Clean up Docker test environment
	docker-compose -f docker-compose.test.yml down -v

# Database commands
db-start:  ## Start test database
	docker run -d -p 5432:5432 --name osint-test-db \
		-e POSTGRES_PASSWORD=postgres \
		-e POSTGRES_DB=osint_test \
		postgres:15

db-stop:  ## Stop test database
	docker stop osint-test-db
	docker rm osint-test-db

redis-start:  ## Start Redis for tests
	docker run -d -p 6379:6379 --name osint-test-redis redis:7

redis-stop:  ## Stop Redis
	docker stop osint-test-redis
	docker rm osint-test-redis

services-start:  ## Start all test services
	@make db-start
	@make redis-start

services-stop:  ## Stop all test services
	@make db-stop
	@make redis-stop

# Benchmarks
benchmark:  ## Run performance benchmarks
	pytest tests/ --benchmark-only

# Reports
report-html:  ## Generate HTML test report
	pytest tests/ --html=test-report.html --self-contained-html

report-junit:  ## Generate JUnit XML report
	pytest tests/ --junitxml=junit.xml

# Development
dev-install:  ## Install in development mode
	pip install -e .

dev-test:  ## Run tests in development mode
	pytest tests/ -v -s --pdb-trace

# All-in-one commands
all:  ## Run quality checks and all tests
	@make quality
	@make test-all
	@make coverage-check

quick:  ## Quick checks before commit
	@make format
	@make lint-fix
	@make test-fast
