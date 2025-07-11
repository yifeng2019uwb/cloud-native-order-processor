#!/bin/bash
# scripts/build-test-frontend.sh
# Build and (placeholder) test script for React frontend

set -e

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
VERBOSE=false
DRY_RUN=false
SKIP_BUILD=false

show_usage() {
    cat << EOF
$(printf "${BLUE}🎨 Frontend Build & Test Script${NC}")

Usage: $0 [OPTIONS]

OPTIONS:
    --skip-build         Skip the build step (useful for test-only)
    --dry-run            Show what would be run, but do not execute
    -v, --verbose        Enable verbose output
    -h, --help           Show this help message

EXAMPLES:
    $0                   # Build frontend (npm ci && npm run build)
    $0 --skip-build      # Skip build step
    $0 --dry-run         # Print commands, do not execute
    $0 -v                # Verbose output
EOF
}

log_info() {
    printf "${BLUE}[INFO]${NC} %s\n" "$1"
}

log_success() {
    printf "${GREEN}[SUCCESS]${NC} %s\n" "$1"
}

log_warning() {
    printf "${YELLOW}[WARNING]${NC} %s\n" "$1"
}

log_error() {
    printf "${RED}[ERROR]${NC} %s\n" "$1"
}

log_step() {
    printf "\n${BLUE}=== %s ===${NC}\n" "$1"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

FRONTEND_DIR="$PROJECT_ROOT/frontend"

if [[ ! -d "$FRONTEND_DIR" ]]; then
    log_error "Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

log_step "Preparing to build frontend (React) app"

if [[ "$DRY_RUN" == "true" ]]; then
    log_info "[DRY RUN] Would run: cd $FRONTEND_DIR"
else
    cd "$FRONTEND_DIR"
fi

if [[ "$SKIP_BUILD" == "true" ]]; then
    log_info "Skipping build step (--skip-build set)"
else
    log_step "Installing dependencies (npm ci)"
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would run: npm ci"
    else
        if [[ "$VERBOSE" == "true" ]]; then
            npm ci
        else
            npm ci --silent
        fi
    fi

    log_step "Building frontend (npm run build)"
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would run: npm run build"
    else
        if [[ "$VERBOSE" == "true" ]]; then
            npm run build
        else
            npm run build --silent
        fi
    fi
fi

log_step "Test coverage (placeholder)"
log_info "No frontend tests found. Setting test coverage to 0%."

log_success "Frontend build complete. Test coverage: 0% (no tests found)"