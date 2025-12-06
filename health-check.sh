#!/bin/bash

# Health Check Script for HackNation 2025
# Verifies all services are running correctly

echo "======================================"
echo "HackNation 2025 - Health Check"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a service is running
check_service() {
    local service=$1
    local status=$(docker-compose ps -q $service 2>/dev/null)
    
    if [ -z "$status" ]; then
        echo -e "${RED}✗${NC} $service: Not running"
        return 1
    else
        echo -e "${GREEN}✓${NC} $service: Running"
        return 0
    fi
}

# Function to check HTTP endpoint
check_http() {
    local name=$1
    local url=$2
    
    if curl -sf "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name: Responding"
        return 0
    else
        echo -e "${RED}✗${NC} $name: Not responding"
        return 1
    fi
}

# Check Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}✗${NC} Docker is not running"
    exit 1
fi

echo "Checking Docker services..."
echo ""

# Check all services
SERVICES=("database" "llm-en" "llm-pl" "backend" "frontend")
ALL_RUNNING=true

for service in "${SERVICES[@]}"; do
    if ! check_service "$service"; then
        ALL_RUNNING=false
    fi
done

echo ""
echo "Checking HTTP endpoints..."
echo ""

# Check HTTP endpoints
check_http "Frontend" "http://localhost:3000"
check_http "Backend Health" "http://localhost:8080/health"

echo ""
echo "Checking database connection..."
echo ""

# Check database
DB_USER=${POSTGRES_USER:-postgres}
if docker-compose exec -T database pg_isready -U "$DB_USER" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Database: Ready"
else
    echo -e "${RED}✗${NC} Database: Not ready"
    ALL_RUNNING=false
fi

echo ""
echo "======================================"

if [ "$ALL_RUNNING" = true ]; then
    echo -e "${GREEN}All services are healthy!${NC}"
    echo ""
    echo "Access the application at:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:8080"
    exit 0
else
    echo -e "${YELLOW}Some services are not healthy${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Check logs: docker-compose logs"
    echo "  2. Restart services: docker-compose restart"
    echo "  3. Rebuild: docker-compose down && docker-compose up -d"
    exit 1
fi
