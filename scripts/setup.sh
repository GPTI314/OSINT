#!/bin/bash

# OSINT Platform Setup Script

set -e

echo "========================================="
echo "OSINT Intelligence Platform Setup"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Create .env file from example
if [ ! -f backend/.env ]; then
    echo "Creating .env file from .env.example..."
    cp backend/.env.example backend/.env
    echo "⚠ Please edit backend/.env with your configuration"
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data/{raw,processed,exports}
mkdir -p logs
mkdir -p infrastructure/nginx/ssl

echo "✓ Directories created"
echo ""

# Build Docker images
echo "Building Docker images..."
docker-compose build

echo "✓ Docker images built"
echo ""

# Start services
echo "Starting services..."
docker-compose up -d postgres mongodb elasticsearch redis rabbitmq

echo "⏳ Waiting for databases to be ready..."
sleep 20

# Run database migrations
echo "Running database migrations..."
docker-compose run --rm backend alembic upgrade head

echo "✓ Database migrations completed"
echo ""

# Start all services
echo "Starting all services..."
docker-compose up -d

echo ""
echo "========================================="
echo "✓ OSINT Platform setup completed!"
echo "========================================="
echo ""
echo "Access points:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/api/v1/docs"
echo "  - Flower (Celery): http://localhost:5555"
echo "  - Grafana: http://localhost:3001"
echo "  - Prometheus: http://localhost:9090"
echo "  - RabbitMQ Management: http://localhost:15672"
echo ""
echo "Default credentials (CHANGE IN PRODUCTION):"
echo "  - RabbitMQ: osint_user / change_this_password"
echo "  - Grafana: admin / admin"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""
