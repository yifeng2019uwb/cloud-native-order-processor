#!/bin/bash

# Integration Test Runner Script
# This script runs integration tests with both services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Running Integration Tests...${NC}"

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}📁 Project root: ${PROJECT_ROOT}${NC}"

# Check if services are running
check_service() {
    local service_name=$1
    local port=$2
    local url=$3

    echo -e "${YELLOW}🔍 Checking ${service_name} on port ${port}...${NC}"

    if curl -s -f "${url}" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ ${service_name} is running on port ${port}${NC}"
        return 0
    else
        echo -e "${RED}❌ ${service_name} is not running on port ${port}${NC}"
        return 1
    fi
}

# Check both services
USER_SERVICE_RUNNING=false
INVENTORY_SERVICE_RUNNING=false

if check_service "User Service" 8000 "http://localhost:8000/health"; then
    USER_SERVICE_RUNNING=true
fi

if check_service "Inventory Service" 8001 "http://localhost:8001/health"; then
    INVENTORY_SERVICE_RUNNING=true
fi

# If services are not running, offer to start them
if [[ "$USER_SERVICE_RUNNING" == false || "$INVENTORY_SERVICE_RUNNING" == false ]]; then
    echo -e "${YELLOW}⚠️  Some services are not running.${NC}"
    echo -e "${BLUE}💡 You can start them manually:${NC}"
    echo -e "   User Service: cd services/user_service && ./deploy.sh"
    echo -e "   Inventory Service: cd services/inventory_service && ./deploy.sh"
    echo ""

    read -p "Do you want to run tests anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}⏭️  Skipping tests. Please start the services first.${NC}"
        exit 1
    fi
fi

# Run integration tests
echo -e "${GREEN}🚀 Running integration tests...${NC}"
cd "${PROJECT_ROOT}/integration_tests"

# Check if virtual environment exists
if [[ ! -d "../.venv" ]]; then
    echo -e "${YELLOW}🔧 Creating virtual environment...${NC}"
    python3 -m venv ../.venv
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source ../.venv/bin/activate

# Install dependencies
echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
pip install -r requirements.txt

# Run tests
echo -e "${GREEN}🧪 Starting integration tests...${NC}"
python run_tests.py

echo -e "${GREEN}🎉 Integration tests completed!${NC}"