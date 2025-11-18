# OSINT Toolkit - Makefile
# Simplifies common deployment and development tasks

.PHONY: help docker-build docker-up docker-down docker-logs docker-dev k8s-deploy k8s-delete k8s-status clean

# Default target
.DEFAULT_GOAL := help

# Variables
DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_DEV = docker-compose -f docker-compose.yml -f docker-compose.dev.yml
KUBECTL = kubectl
NAMESPACE = osint

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Docker targets
docker-build: ## Build Docker images
	@echo "Building Docker images..."
	@chmod +x scripts/build-images.sh
	@./scripts/build-images.sh

docker-up: ## Start Docker Compose services (production)
	@echo "Starting Docker Compose services..."
	@chmod +x scripts/deploy-docker.sh
	@./scripts/deploy-docker.sh production up

docker-down: ## Stop Docker Compose services
	@echo "Stopping Docker Compose services..."
	@$(DOCKER_COMPOSE) down

docker-logs: ## View Docker Compose logs
	@$(DOCKER_COMPOSE) logs -f

docker-dev: ## Start Docker Compose in development mode
	@echo "Starting Docker Compose in development mode..."
	@chmod +x scripts/deploy-docker.sh
	@./scripts/deploy-docker.sh dev up

docker-dev-down: ## Stop development services
	@$(DOCKER_COMPOSE_DEV) down

docker-restart: ## Restart Docker Compose services
	@$(DOCKER_COMPOSE) restart

docker-clean: ## Remove all Docker containers, volumes, and images
	@echo "Cleaning Docker environment..."
	@$(DOCKER_COMPOSE) down -v --remove-orphans
	@docker system prune -f

# Kubernetes targets
k8s-deploy: ## Deploy to Kubernetes
	@echo "Deploying to Kubernetes..."
	@chmod +x scripts/deploy-k8s.sh
	@./scripts/deploy-k8s.sh apply

k8s-delete: ## Delete Kubernetes deployment
	@echo "Deleting Kubernetes deployment..."
	@chmod +x scripts/deploy-k8s.sh
	@./scripts/deploy-k8s.sh delete

k8s-status: ## Check Kubernetes deployment status
	@echo "Checking Kubernetes status..."
	@$(KUBECTL) get all -n $(NAMESPACE)

k8s-logs-backend: ## View backend logs in Kubernetes
	@$(KUBECTL) logs -n $(NAMESPACE) -l app=osint-backend --tail=100 -f

k8s-logs-frontend: ## View frontend logs in Kubernetes
	@$(KUBECTL) logs -n $(NAMESPACE) -l app=osint-frontend --tail=100 -f

k8s-logs-worker: ## View worker logs in Kubernetes
	@$(KUBECTL) logs -n $(NAMESPACE) -l app=osint-worker --tail=100 -f

k8s-shell-backend: ## Open shell in backend pod
	@$(KUBECTL) exec -it -n $(NAMESPACE) $$($(KUBECTL) get pod -n $(NAMESPACE) -l app=osint-backend -o jsonpath='{.items[0].metadata.name}') -- /bin/bash

k8s-port-forward: ## Port forward backend service
	@echo "Port forwarding backend to localhost:8000..."
	@$(KUBECTL) port-forward -n $(NAMESPACE) svc/osint-backend 8000:8000

# Database targets
db-backup: ## Backup database (Docker)
	@echo "Backing up database..."
	@mkdir -p backups
	@docker-compose exec -T postgres pg_dump -U osint osint > backups/backup-$$(date +%Y%m%d-%H%M%S).sql
	@echo "Backup created in backups/"

db-restore: ## Restore database from latest backup (Docker)
	@echo "Restoring database from latest backup..."
	@docker-compose exec -T postgres psql -U osint osint < $$(ls -t backups/*.sql | head -1)
	@echo "Database restored"

k8s-db-backup: ## Backup database (Kubernetes)
	@echo "Backing up database..."
	@mkdir -p backups
	@$(KUBECTL) exec postgres-0 -n $(NAMESPACE) -- pg_dump -U osint osint > backups/k8s-backup-$$(date +%Y%m%d-%H%M%S).sql
	@echo "Backup created in backups/"

# Development targets
dev-setup: ## Initial development setup
	@echo "Setting up development environment..."
	@cp -n .env.example .env || true
	@echo "Please update .env file with your configuration"
	@chmod +x scripts/*.sh
	@echo "Setup complete!"

lint: ## Run code linting
	@echo "Running linting..."
	@docker-compose exec backend black --check .
	@docker-compose exec backend flake8 .

format: ## Format code
	@echo "Formatting code..."
	@docker-compose exec backend black .

test: ## Run tests
	@echo "Running tests..."
	@docker-compose exec backend pytest

# Utility targets
clean: docker-clean ## Clean all temporary files and Docker resources

env-check: ## Check environment configuration
	@echo "Checking environment configuration..."
	@test -f .env && echo "✓ .env file exists" || echo "✗ .env file missing"
	@test -f k8s/secrets.yaml && echo "✓ k8s/secrets.yaml exists" || echo "✗ k8s/secrets.yaml missing"
	@docker --version && echo "✓ Docker installed" || echo "✗ Docker not found"
	@docker-compose --version && echo "✓ Docker Compose installed" || echo "✗ Docker Compose not found"
	@kubectl version --client && echo "✓ kubectl installed" || echo "✗ kubectl not found"

permissions: ## Fix script permissions
	@echo "Fixing script permissions..."
	@chmod +x scripts/*.sh
	@echo "Permissions updated"
