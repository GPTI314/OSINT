#!/bin/bash
# Start Celery Worker Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting OSINT Celery Worker...${NC}\n"

# Check if Redis is running
echo -e "${YELLOW}Checking Redis connection...${NC}"
if ! redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    echo -e "${RED}Error: Redis is not running!${NC}"
    echo "Please start Redis first: redis-server"
    exit 1
fi
echo -e "${GREEN}✓ Redis is running${NC}\n"

# Parse command line arguments
QUEUE="default"
CONCURRENCY=4
LOG_LEVEL="info"
WORKER_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--queue)
            QUEUE="$2"
            shift 2
            ;;
        -c|--concurrency)
            CONCURRENCY="$2"
            shift 2
            ;;
        -l|--log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        -n|--name)
            WORKER_NAME="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -q, --queue QUEUE           Queue to consume from (default: default)"
            echo "  -c, --concurrency N         Number of worker processes (default: 4)"
            echo "  -l, --log-level LEVEL       Log level (default: info)"
            echo "  -n, --name NAME            Worker name"
            echo "  -h, --help                  Show this help message"
            echo ""
            echo "Queue options: critical, high, default, low, batch, or comma-separated list"
            echo ""
            echo "Examples:"
            echo "  $0                          # Start default worker"
            echo "  $0 -q critical,high         # Start worker for critical and high queues"
            echo "  $0 -q low -c 2              # Start worker for low queue with 2 processes"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Set worker name if not provided
if [ -z "$WORKER_NAME" ]; then
    WORKER_NAME="${QUEUE}@%h"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start worker
echo -e "${GREEN}Starting Celery worker with configuration:${NC}"
echo "  Queue(s): $QUEUE"
echo "  Concurrency: $CONCURRENCY"
echo "  Log Level: $LOG_LEVEL"
echo "  Worker Name: $WORKER_NAME"
echo ""

exec celery -A celery_app worker \
    -Q "$QUEUE" \
    -c "$CONCURRENCY" \
    -l "$LOG_LEVEL" \
    -n "$WORKER_NAME" \
    --logfile=logs/worker_${QUEUE}.log \
    --pidfile=logs/worker_${QUEUE}.pid
