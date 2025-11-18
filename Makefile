# OSINT Toolkit - Makefile

.PHONY: help install dev-install start stop restart logs clean test build monitoring

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "OSINT Toolkit - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

dev-install: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy

start: ## Start all services
	docker-compose -f docker-compose.monitoring.yml up -d

stop: ## Stop all services
	docker-compose -f docker-compose.monitoring.yml down

restart: ## Restart all services
	docker-compose -f docker-compose.monitoring.yml restart

logs: ## Show logs from all services
	docker-compose -f docker-compose.monitoring.yml logs -f

logs-%: ## Show logs from specific service (e.g., make logs-osint-app)
	docker-compose -f docker-compose.monitoring.yml logs -f $*

status: ## Show status of all services
	docker-compose -f docker-compose.monitoring.yml ps

build: ## Build Docker images
	docker-compose -f docker-compose.monitoring.yml build

monitoring: ## Open monitoring dashboards
	@echo "Opening monitoring dashboards..."
	@echo "Kibana: http://localhost:5601"
	@echo "Grafana: http://localhost:3000 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"
	@echo "AlertManager: http://localhost:9093"

health: ## Check application health
	@curl -s http://localhost:5000/health | python -m json.tool

metrics: ## View Prometheus metrics
	@curl -s http://localhost:8000/metrics

performance: ## View performance statistics
	@curl -s http://localhost:5000/performance | python -m json.tool

test: ## Run tests
	pytest tests/ -v --cov=src --cov-report=html

clean: ## Clean up temporary files and volumes
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

clean-all: clean ## Clean everything including Docker volumes
	docker-compose -f docker-compose.monitoring.yml down -v
	rm -rf logs/*
	rm -rf prometheus_data grafana_data elasticsearch_data alertmanager_data

shell: ## Open shell in running app container
	docker exec -it osint-app /bin/bash

elk-setup: ## Setup ELK index templates
	@python -c "from src.logging.elk_handler import ELKHandler; handler = ELKHandler(); handler.create_index_template(); print('✓ ELK index template created')"

format: ## Format code with black
	black src/ tests/

lint: ## Lint code with flake8
	flake8 src/ tests/

type-check: ## Type check with mypy
	mypy src/

quality: format lint type-check ## Run all code quality checks

# Development helpers
dev-logs: ## Tail application logs
	tail -f logs/osint-toolkit.log

dev-json-logs: ## Tail JSON logs
	tail -f logs/osint-toolkit.json.log

dev-error-logs: ## Tail error logs
	tail -f logs/osint-toolkit.error.log

# Monitoring helpers
prom-reload: ## Reload Prometheus configuration
	curl -X POST http://localhost:9090/-/reload

alert-status: ## Check AlertManager status
	@curl -s http://localhost:9093/api/v2/status | python -m json.tool

# Backup
backup-logs: ## Backup logs
	@mkdir -p backups
	@tar -czf backups/logs-$$(date +%Y%m%d-%H%M%S).tar.gz logs/

backup-config: ## Backup configuration
	@mkdir -p backups
	@tar -czf backups/config-$$(date +%Y%m%d-%H%M%S).tar.gz config/ monitoring/ .env
