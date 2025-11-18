#!/bin/bash
# OSINT Toolkit - Docker Image Build Script
# Builds all Docker images for the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
REGISTRY=${REGISTRY:-""}
VERSION=${VERSION:-"latest"}
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

# Add registry prefix if specified
if [ -n "$REGISTRY" ]; then
    IMAGE_PREFIX="$REGISTRY/"
else
    IMAGE_PREFIX=""
fi

print_info "Building OSINT Toolkit Docker images..."
print_info "Version: $VERSION"
print_info "Build Date: $BUILD_DATE"
if [ -n "$REGISTRY" ]; then
    print_info "Registry: $REGISTRY"
fi

# Build backend image
print_info "Building backend image..."
docker build \
    --build-arg BUILD_DATE="$BUILD_DATE" \
    --build-arg VERSION="$VERSION" \
    -f Dockerfile \
    -t "${IMAGE_PREFIX}osint/backend:$VERSION" \
    -t "${IMAGE_PREFIX}osint/backend:latest" \
    .

# Build worker image
print_info "Building worker image..."
docker build \
    --build-arg BUILD_DATE="$BUILD_DATE" \
    --build-arg VERSION="$VERSION" \
    -f Dockerfile.worker \
    -t "${IMAGE_PREFIX}osint/worker:$VERSION" \
    -t "${IMAGE_PREFIX}osint/worker:latest" \
    .

# Build frontend image
print_info "Building frontend image..."
docker build \
    --build-arg BUILD_DATE="$BUILD_DATE" \
    --build-arg VERSION="$VERSION" \
    -f Dockerfile.frontend \
    -t "${IMAGE_PREFIX}osint/frontend:$VERSION" \
    -t "${IMAGE_PREFIX}osint/frontend:latest" \
    .

print_info ""
print_info "==================================================================="
print_info "All images built successfully!"
print_info "==================================================================="
docker images | grep "osint/"
print_info "==================================================================="

# Push to registry if specified
if [ -n "$REGISTRY" ]; then
    read -p "Push images to registry? (yes/no): " push_confirm
    if [ "$push_confirm" == "yes" ]; then
        print_info "Pushing images to $REGISTRY..."
        docker push "${IMAGE_PREFIX}osint/backend:$VERSION"
        docker push "${IMAGE_PREFIX}osint/backend:latest"
        docker push "${IMAGE_PREFIX}osint/worker:$VERSION"
        docker push "${IMAGE_PREFIX}osint/worker:latest"
        docker push "${IMAGE_PREFIX}osint/frontend:$VERSION"
        docker push "${IMAGE_PREFIX}osint/frontend:latest"
        print_info "Images pushed successfully!"
    fi
fi

print_info "Done!"
