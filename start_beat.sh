#!/bin/bash
# Start Celery Beat Scheduler Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting OSINT Celery Beat Scheduler...${NC}\n"

# Check if Redis is running
echo -e "${YELLOW}Checking Redis connection...${NC}"
if ! redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    echo -e "${RED}Error: Redis is not running!${NC}"
    echo "Please start Redis first: redis-server"
    exit 1
fi
echo -e "${GREEN}✓ Redis is running${NC}\n"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start beat scheduler
echo -e "${GREEN}Starting Celery Beat scheduler...${NC}"
echo "  Scheduler: PersistentScheduler"
echo "  Schedule File: /tmp/celerybeat-schedule"
echo "  Log File: logs/beat.log"
echo ""

exec celery -A celery_app beat \
    -l info \
    --scheduler celery.beat:PersistentScheduler \
    --logfile=logs/beat.log \
    --pidfile=logs/beat.pid
