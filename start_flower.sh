#!/bin/bash
# Start Flower Monitoring Dashboard Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting OSINT Flower Monitoring Dashboard...${NC}\n"

# Check if Redis is running
echo -e "${YELLOW}Checking Redis connection...${NC}"
if ! redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    echo -e "${RED}Error: Redis is not running!${NC}"
    echo "Please start Redis first: redis-server"
    exit 1
fi
echo -e "${GREEN}✓ Redis is running${NC}\n"

# Parse command line arguments
PORT=5555
BASIC_AUTH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -a|--auth)
            BASIC_AUTH="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -p, --port PORT             Port to run on (default: 5555)"
            echo "  -a, --auth USER:PASS        Enable basic auth (format: user:password)"
            echo "  -h, --help                  Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Start on default port 5555"
            echo "  $0 -p 8080                  # Start on port 8080"
            echo "  $0 -a admin:secret          # Start with authentication"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Start Flower
echo -e "${GREEN}Starting Flower with configuration:${NC}"
echo "  Port: $PORT"
echo "  URL: http://localhost:$PORT"
if [ -n "$BASIC_AUTH" ]; then
    echo "  Authentication: Enabled"
fi
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"

if [ -n "$BASIC_AUTH" ]; then
    exec celery -A celery_app flower --port="$PORT" --basic_auth="$BASIC_AUTH"
else
    exec celery -A celery_app flower --port="$PORT"
fi
