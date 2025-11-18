#!/bin/bash
# OSINT Toolkit - Docker Deployment Script
# This script deploys the application using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_info "Please update .env file with your configuration before proceeding."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Determine Docker Compose command
DOCKER_COMPOSE="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
fi

# Parse arguments
ENVIRONMENT=${1:-production}
ACTION=${2:-up}

print_info "Starting OSINT Toolkit deployment..."
print_info "Environment: $ENVIRONMENT"
print_info "Action: $ACTION"

# Build and deploy based on environment
if [ "$ENVIRONMENT" == "dev" ] || [ "$ENVIRONMENT" == "development" ]; then
    print_info "Deploying development environment..."

    case $ACTION in
        up)
            $DOCKER_COMPOSE -f docker-compose.yml -f docker-compose.dev.yml up -d --build
            ;;
        down)
            $DOCKER_COMPOSE -f docker-compose.yml -f docker-compose.dev.yml down
            ;;
        logs)
            $DOCKER_COMPOSE -f docker-compose.yml -f docker-compose.dev.yml logs -f
            ;;
        restart)
            $DOCKER_COMPOSE -f docker-compose.yml -f docker-compose.dev.yml restart
            ;;
        *)
            print_error "Unknown action: $ACTION"
            exit 1
            ;;
    esac
else
    print_info "Deploying production environment..."

    case $ACTION in
        up)
            $DOCKER_COMPOSE up -d --build
            ;;
        down)
            $DOCKER_COMPOSE down
            ;;
        logs)
            $DOCKER_COMPOSE logs -f
            ;;
        restart)
            $DOCKER_COMPOSE restart
            ;;
        *)
            print_error "Unknown action: $ACTION"
            exit 1
            ;;
    esac
fi

if [ "$ACTION" == "up" ]; then
    print_info "Waiting for services to start..."
    sleep 10

    print_info "Checking service health..."
    $DOCKER_COMPOSE ps

    print_info ""
    print_info "==================================================================="
    print_info "OSINT Toolkit deployed successfully!"
    print_info "==================================================================="
    print_info "Frontend: http://localhost"
    print_info "Backend API: http://localhost:8000"
    print_info "Backend Health: http://localhost:8000/health"
    if [ "$ENVIRONMENT" == "dev" ] || [ "$ENVIRONMENT" == "development" ]; then
        print_info "Adminer (DB): http://localhost:8080"
        print_info "Redis Commander: http://localhost:8081"
    fi
    print_info "==================================================================="
fi

print_info "Done!"
