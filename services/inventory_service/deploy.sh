#!/bin/bash

# Inventory Service Deploy Script
# This script sets up the environment and starts the inventory service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="inventory_service"
PORT=8001
PYTHON_VERSION="3.11"

echo -e "${BLUE}🚀 Deploying ${SERVICE_NAME}...${NC}"

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICES_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$SERVICES_DIR")"

echo -e "${YELLOW}📁 Script directory: ${SCRIPT_DIR}${NC}"
echo -e "${YELLOW}📁 Services directory: ${SERVICES_DIR}${NC}"
echo -e "${YELLOW}📁 Project root: ${PROJECT_ROOT}${NC}"

# Check if we're in the right directory
if [[ ! -f "src/main.py" ]]; then
    echo -e "${RED}❌ Error: src/main.py not found. Please run this script from the inventory_service directory.${NC}"
    exit 1
fi

# Check Python version
if ! command -v python${PYTHON_VERSION} &> /dev/null; then
    echo -e "${RED}❌ Error: Python ${PYTHON_VERSION} is not installed.${NC}"
    echo -e "${YELLOW}💡 Please install Python ${PYTHON_VERSION} or update the PYTHON_VERSION variable.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"

# Check if virtual environment exists
if [[ ! -d ".venv-${SERVICE_NAME}" ]]; then
    echo -e "${YELLOW}🔧 Creating virtual environment...${NC}"
    python${PYTHON_VERSION} -m venv .venv-${SERVICE_NAME}
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source .venv-${SERVICE_NAME}/bin/activate

# Install dependencies if requirements.txt exists
if [[ -f "requirements.txt" ]]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

# Install common package if it exists
if [[ -d "../common" ]]; then
    echo -e "${YELLOW}📦 Installing common package...${NC}"
    pip install -e ../common
    echo -e "${GREEN}✅ Common package installed${NC}"
fi

# Check if port is available
if lsof -Pi :${PORT} -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Port ${PORT} is already in use. Checking if it's our service...${NC}"
    PID=$(lsof -Pi :${PORT} -sTCP:LISTEN -t)
    if ps -p $PID | grep -q "uvicorn"; then
        echo -e "${GREEN}✅ Service already running on port ${PORT} (PID: ${PID})${NC}"
        echo -e "${BLUE}🌐 Service URL: http://localhost:${PORT}${NC}"
        echo -e "${BLUE}📚 API Docs: http://localhost:${PORT}/docs${NC}"
        echo -e "${BLUE}❤️  Health Check: http://localhost:${PORT}/health${NC}"
        exit 0
    else
        echo -e "${RED}❌ Port ${PORT} is in use by another process (PID: ${PID})${NC}"
        echo -e "${YELLOW}💡 Please stop the process using port ${PORT} or change the PORT variable.${NC}"
        exit 1
    fi
fi

# Set environment variables
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"

# Load environment variables from .env if it exists
if [[ -f "${SERVICES_DIR}/.env" ]]; then
    echo -e "${YELLOW}🔧 Loading environment variables from ${SERVICES_DIR}/.env${NC}"
    export $(grep -v '^#' ${SERVICES_DIR}/.env | xargs)
fi

# Start the service
echo -e "${GREEN}🚀 Starting ${SERVICE_NAME} on port ${PORT}...${NC}"
echo -e "${BLUE}🌐 Service will be available at: http://localhost:${PORT}${NC}"
echo -e "${BLUE}📚 API Docs will be available at: http://localhost:${PORT}/docs${NC}"
echo -e "${BLUE}❤️  Health Check: http://localhost:${PORT}/health${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop the service${NC}"
echo ""

# Start uvicorn
python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT} --reload