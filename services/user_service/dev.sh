#!/bin/bash
# services/user_service/dev.sh
# User Service development script - build, test, clean
# Build always includes validation and import checking

set -e

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SERVICE_NAME="user_service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
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
    printf "${CYAN}[STEP]${NC} %s\n" "$1"
}

# Usage function
show_usage() {
    cat << EOF
User Service Development Script

Usage: $0 {build|test|clean} [options] [test_target]

Commands:
    build [--no-cache]     Full build with validation and import checking
                          --no-cache: Force reinstall all dependencies
    test [test_target]     Run user service tests (all or specific)
    clean                  Clean build artifacts and caches

Build Process (always runs):
    1. Check prerequisites and environment
    2. Setup/activate virtual environment
    3. Install common package (with --no-cache if specified)
    4. Install service dependencies
    5. Validate Python syntax
    6. Test critical imports (catches circular imports)
    7. Build package

Examples:
    $0 build                    # Full build with validation
    $0 build --no-cache        # Full build, force fresh install
    $0 test                     # Run all tests (builds first if needed)
    $0 test test_auth          # Test specific test file
    $0 clean                   # Clean all artifacts

EOF
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."

            # Get Python version from centralized config
    python_cmd=$(python3 -c "import sys; sys.path.insert(0, '../dev-tools'); from dev_tools import validate_python_version; print(validate_python_version())")

    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed"
        exit 1
    fi

    local python_version=$("$python_cmd" --version | cut -d' ' -f2)
    log_info "Python version: $python_version"

    # Check if we're in the right directory
    if [[ ! -f "src/main.py" ]]; then
        log_error "Not in user service directory - src/main.py not found"
        exit 1
    fi

    # Check common package exists
    if [[ ! -d "../common" ]]; then
        log_error "Common package not found at ../common"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Setup virtual environment
setup_venv() {
    log_step "Setting up virtual environment..."

    cd "$SCRIPT_DIR"

    # Create virtual environment if it doesn't exist
    if [[ ! -d ".venv-${SERVICE_NAME}" ]]; then
        log_info "Creating virtual environment..."
        python3.11 -m venv ".venv-${SERVICE_NAME}"
    fi

    # Activate virtual environment
    source ".venv-${SERVICE_NAME}/bin/activate"

    log_success "Virtual environment ready"
}

# Install dependencies with validation
install_dependencies() {
    local no_cache="$1"

    log_step "Installing dependencies..."

    # Use centralized dependency installation
    if [[ "$no_cache" == "true" ]]; then
        python3 -c "import sys; sys.path.insert(0, '../dev-tools'); from dev_tools import install_dependencies; install_dependencies('.', True)"
    else
        python3 -c "import sys; sys.path.insert(0, '../dev-tools'); from dev_tools import install_dependencies; install_dependencies('.', False)"
    fi

    log_success "Dependencies installed"
}

# Validate syntax and imports (always runs during build)
validate_build() {
    log_step "Validating syntax and imports..."

    # Ensure Python command is set
    if [[ -z "$python_cmd" ]]; then
        python_cmd=$(python3 -c "import sys; sys.path.insert(0, '../dev-tools'); from dev_tools import validate_python_version; print(validate_python_version())")
    fi

    # Use centralized validation functions
    if "$python_cmd" -c "
import sys
sys.path.insert(0, '../dev-tools')
from dev_tools import check_python_syntax, validate_service_imports

# Check syntax
success, file_count, errors = check_python_syntax('src')
if not success:
    print(f'✗ Found {errors} syntax errors in {file_count} files')
    sys.exit(1)
print(f'✓ Python syntax validation passed ({file_count} files)')

# Check imports
success, issues = validate_service_imports('user_service')
if not success:
    for issue in issues:
        print(f'✗ {issue}')
    sys.exit(1)
print('✓ Import validation completed - no circular imports detected')
" ; then
        log_success "All validation passed"
    else
        log_error "Validation failed"
        exit 1
    fi
}

# Full build process (always includes validation)
build() {
    local no_cache="false"

    # Parse build arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-cache)
                no_cache="true"
                shift
                ;;
            *)
                log_error "Unknown build option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    log_info "Building ${SERVICE_NAME}$([ "$no_cache" == "true" ] && echo " (no-cache mode)")..."

    check_prerequisites
    setup_venv
    install_dependencies "$no_cache"
    validate_build  # Always validate during build

    # Build the package if setup.py exists
    if [[ -f "setup.py" ]]; then
        log_step "Building package..."
        if python setup.py build ; then
            log_success "Package build completed"
        else
            log_error "Package build failed"
            exit 1
        fi
    fi

    log_success "✅ ${SERVICE_NAME} build completed successfully!"
    log_info "✅ All syntax and import validation passed"
    log_info "✅ Ready for testing and development"
}

# Enhanced test function
test() {
    local test_target="$1"

    # Always ensure we have a working build first
    if [[ ! -d ".venv-${SERVICE_NAME}" ]]; then
        log_warning "Virtual environment not found, running full build first..."
        build
        return  # build() already activates venv and runs validation
    fi

    # Activate virtual environment
    source ".venv-${SERVICE_NAME}/bin/activate"

    # Quick validation to catch any issues
    log_step "Pre-test validation..."
    validate_build

    # Run tests
    log_step "Running tests..."

    if [[ -n "$test_target" ]]; then
        log_info "Running tests for: $test_target"
        if [[ "$test_target" == *".py" ]]; then
            python -m pytest "tests/$test_target" -v --tb=short
        else
            python -m pytest "tests/" -k "$test_target" -v --tb=short
        fi
    else
        log_info "Running all tests..."
        python -m pytest tests/ -v --tb=short --durations=10
    fi

    log_success "✅ ${SERVICE_NAME} tests completed"
}

# Enhanced clean function
clean() {
    log_step "Cleaning ${SERVICE_NAME} build artifacts..."

    # Remove build directories (more efficient)
    rm -rf dist build *.egg-info .eggs 2>/dev/null || true

    # Remove cache files and directories (single find command)
    find . \( -name "__pycache__" -o -name ".pytest_cache" -o -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true

    log_success "✅ ${SERVICE_NAME} cleanup completed"
}

# Main function
main() {
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 1
    fi

    local command="$1"
    shift  # Remove command from arguments

    # Execute command
    case $command in
        build)
            build "$@"
            ;;
        test)
            test "$1"
            ;;
        clean)
            clean
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Script execution
main "$@"
