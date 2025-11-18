#!/bin/bash
# ============================================================================
# PostgreSQL Database Setup Script
# ============================================================================
# This script sets up the OSINT platform PostgreSQL database
# ============================================================================

set -e

# Configuration
DB_NAME="${DB_NAME:-osint_platform}"
DB_USER="${DB_USER:-osint_user}"
DB_PASSWORD="${DB_PASSWORD:-changeme}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

# Check if PostgreSQL is running
print_step "Checking PostgreSQL connection..."
if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" > /dev/null 2>&1; then
    print_error "PostgreSQL is not running or not accessible at $DB_HOST:$DB_PORT"
    exit 1
fi
print_success "PostgreSQL is running"

# Create database user if it doesn't exist
print_step "Creating database user..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -tc "SELECT 1 FROM pg_user WHERE usename = '$DB_USER'" | grep -q 1 || \
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
print_success "User $DB_USER created or already exists"

# Create database if it doesn't exist
print_step "Creating database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
print_success "Database $DB_NAME created or already exists"

# Grant privileges
print_step "Granting privileges..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
print_success "Privileges granted"

# Run schema setup
print_step "Setting up database schema..."
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f ../postgresql/schema.sql
print_success "Schema created successfully"

# Ask if user wants to load seed data
read -p "Do you want to load seed data for development? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Loading seed data..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f ./seed_data.sql
    print_success "Seed data loaded"
fi

# Display connection info
print_success "Database setup complete!"
echo ""
print_info "Connection details:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""
print_info "Connection string:"
echo "  postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""
print_info "To connect to the database:"
echo "  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
