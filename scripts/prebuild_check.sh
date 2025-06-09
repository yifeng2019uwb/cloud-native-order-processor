#!/bin/bash

# Pre-Build Environment Check - Fixed for Actual Project Structure
# Validates that everything is ready for Docker build and ECR push

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo "🔍 Pre-Build Environment Check"
echo "=============================="
echo ""

# Track if we have any errors
ERRORS=0

# Check 1: Docker
echo "🐳 Checking Docker..."
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        check_success "Docker is installed and running"
        DOCKER_VERSION=$(docker --version)
        check_info "Version: $DOCKER_VERSION"
    else
        check_error "Docker is installed but not running"
        ERRORS=$((ERRORS + 1))
    fi
else
    check_error "Docker is not installed"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# Check 2: AWS CLI
echo "☁️  Checking AWS CLI..."
if command -v aws &> /dev/null; then
    check_success "AWS CLI is installed"
    AWS_VERSION=$(aws --version)
    check_info "Version: $AWS_VERSION"

    # Check AWS credentials
    if aws sts get-caller-identity &> /dev/null; then
        AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
        AWS_USER=$(aws sts get-caller-identity --query Arn --output text)
        check_success "AWS credentials are configured"
        check_info "Account: $AWS_ACCOUNT"
        check_info "Identity: $AWS_USER"
    else
        check_error "AWS credentials are not configured"
        ERRORS=$((ERRORS + 1))
    fi
else
    check_error "AWS CLI is not installed"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# Check 3: Project structure (Fixed for actual structure)
echo "📁 Checking project structure..."

required_files=(
    "services/order-service/src/app.py"
    "services/order-service/requirements.txt"
    "services/common/requirements.txt"
    "services/common/__init__.py"
    "services/common/setup.py"
)

required_dirs=(
    "services/"
    "services/order-service/"
    "services/common/"
    "docker/"
)

# Check if we can find the services directory structure
if [ -d "services" ]; then
    check_success "Found services directory"

    # List what's actually in services to help debug
    check_info "Services directory contains:"
    ls -la services/ | while read line; do
        check_info "  $line"
    done
else
    check_error "Missing services directory"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# Check for key files with actual paths
echo "🔍 Checking for key application files..."

# Order service files
if [ -f "services/order-service/src/app.py" ]; then
    check_success "Found order service app.py"
else
    check_error "Missing order service app.py"
    check_info "Expected: services/order-service/src/app.py"
    ERRORS=$((ERRORS + 1))
fi

# Requirements files
if [ -f "services/order-service/requirements.txt" ]; then
    check_success "Found order service requirements.txt"
else
    check_error "Missing order service requirements.txt"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "services/common/requirements.txt" ]; then
    check_success "Found common requirements.txt"
else
    check_error "Missing common requirements.txt"
    ERRORS=$((ERRORS + 1))
fi

# Common package files (flexible matching for __init__.py)
if [ -f "services/common/__init__.py" ] || [ -f "services/common/**init**.py" ] || ls services/common/*init*.py >/dev/null 2>&1; then
    check_success "Found common package __init__.py"
else
    check_error "Missing common package __init__.py"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "services/common/setup.py" ]; then
    check_success "Found common package setup.py"
else
    check_warning "Missing common package setup.py (recommended)"
fi

# Check key directories
if [ -d "services/common/database" ]; then
    check_success "Found common database module"
fi

if [ -d "services/common/models" ]; then
    check_success "Found common models module"
fi

# Docker files
if [ -d "docker" ]; then
    check_success "Found docker directory"

    if [ -f "docker/order-service/Dockerfile" ] || [ -f "docker/order-service/Dockerfile.fixed" ]; then
        check_success "Found order service Dockerfile"
    else
        check_warning "No Dockerfile found for order service"
        check_info "Will create one automatically during build"
    fi
else
    check_warning "Missing docker directory"
    check_info "Will create necessary files during build"
fi

echo ""

# Check 4: ECR Repository
echo "📦 Checking ECR repository..."
AWS_REGION="us-west-2"  # Update if different
ECR_REPOSITORY="order-processor-dev"

if aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION &> /dev/null; then
    check_success "ECR repository '$ECR_REPOSITORY' exists"
    REPO_URI=$(aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION --query 'repositories[0].repositoryUri' --output text)
    check_info "Repository URI: $REPO_URI"
else
    check_warning "ECR repository '$ECR_REPOSITORY' not found"
    check_info "It will be created automatically during build"
fi

echo ""

# Check 5: Git (for tagging)
echo "🔄 Checking Git..."
if command -v git &> /dev/null; then
    if git rev-parse --git-dir &> /dev/null; then
        check_success "Git repository detected"
        COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
        check_info "Current commit: $COMMIT_SHA"
    else
        check_warning "Not in a Git repository"
        check_info "Images will be tagged with 'local' instead of commit SHA"
    fi
else
    check_warning "Git is not installed"
    check_info "Images will be tagged with 'local' instead of commit SHA"
fi

echo ""

# Summary
echo "📊 Summary"
echo "=========="

if [ $ERRORS -eq 0 ]; then
    check_success "All critical checks passed! Ready to build and push."
    echo ""
    echo "🚀 To proceed:"
    echo "   1. Run the quick build script: ./scripts/quick_build.sh"
    echo "   2. Or run the full build script: ./scripts/ecr_build_push.sh"
    echo ""
    echo "📋 Configuration detected:"
    echo "   Region: $AWS_REGION"
    echo "   Repository: $ECR_REPOSITORY"
    echo "   Account: ${AWS_ACCOUNT:-'Not detected'}"
elif [ $ERRORS -le 2 ]; then
    check_warning "$ERRORS minor issues found, but build should still work."
    echo ""
    echo "🚀 You can proceed with:"
    echo "   ./scripts/quick_build.sh"
    echo ""
    echo "The build script will handle missing files automatically."
else
    check_error "$ERRORS critical issues found. Please fix them before building."
    echo ""
    echo "🔧 Common fixes:"
    echo "   - Install Docker: https://docs.docker.com/get-docker/"
    echo "   - Install AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html"
    echo "   - Configure AWS: aws configure"
    echo "   - Start Docker service: sudo systemctl start docker"
    echo "   - Check your project structure matches the expected layout"
    exit 1
fi

echo ""
echo "📁 Your Project Structure:"
echo "========================="
if [ -d "services" ]; then
    tree services/ 2>/dev/null || find services/ -type f | head -20
else
    echo "services/ directory not found"
fi