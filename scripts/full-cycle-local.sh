#!/bin/bash
# scripts/full-cycle-local.sh
# Orchestrate full build → deploy → integration test → cleanup cycle for personal use
# Always cleans up at the end to save costs

set -e

# Color setup
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()    { printf "${BLUE}[INFO]${NC} %s\n" "$1"; }
log_success(){ printf "${GREEN}[SUCCESS]${NC} %s\n" "$1"; }
log_warn()   { printf "${YELLOW}[WARN]${NC} %s\n" "$1"; }
log_error()  { printf "${RED}[ERROR]${NC} %s\n" "$1"; }

# Defaults
ENVIRONMENT="dev"
VERBOSE=""
DO_INFRA=false
DO_APP=false
DO_TEST=false
DO_CLEANUP=false
SHOW_HELP=false

usage() {
  cat << EOF
${BLUE}Full Cycle Local Orchestrator${NC}
Usage: $0 [--env dev|prod] [--infra] [--app] [--test] [--cleanup] [--verbose] [--help]

Options:
  --env dev|prod   Set environment (default: dev)
  --infra          Run infrastructure deploy step
  --app            Run application deploy step
  --test           Run integration test step
  --cleanup        Run cleanup (destroy) step
  --verbose        Enable verbose output
  --help           Show this help message

If no step flags are given, all steps (infra, app, test, cleanup) are run in order.
If any step flag is given, only those steps are run (in order: infra, app, test, cleanup).

Examples:
  # Full cycle (default):
  $0 --env dev

  # Only infra deploy:
  $0 --infra --env dev

  # Only integration test:
  $0 --test --env dev

  # App deploy and cleanup only:
  $0 --app --cleanup --env dev

  # Verbose output:
  $0 --verbose
EOF
  exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --env) ENVIRONMENT="$2"; shift 2 ;;
    --infra) DO_INFRA=true; shift ;;
    --app) DO_APP=true; shift ;;
    --test) DO_TEST=true; shift ;;
    --cleanup) DO_CLEANUP=true; shift ;;
    --verbose|-v) VERBOSE="-v"; shift ;;
    --help|-h) SHOW_HELP=true; shift ;;
    *) log_error "Unknown arg: $1"; usage ;;
  esac
done

if $SHOW_HELP; then
  usage
fi

# If no step flags, run all steps
if ! $DO_INFRA && ! $DO_APP && ! $DO_TEST && ! $DO_CLEANUP; then
  DO_INFRA=true
  DO_APP=true
  DO_TEST=true
  DO_CLEANUP=true
fi

# Print summary
log_info "Environment: $ENVIRONMENT"
log_info "Steps to run:"
$DO_INFRA    && log_info "  - Infrastructure deploy"
$DO_APP      && log_info "  - Application deploy"
$DO_TEST     && log_info "  - Integration test"
$DO_CLEANUP  && log_info "  - Cleanup (destroy)"
echo

trap 'log_warn "Script interrupted or failed. Running cleanup..."; ./scripts/destroy.sh --environment "$ENVIRONMENT" --force $VERBOSE; exit 1' ERR INT

if $DO_INFRA; then
  log_info "Step: Deploy infrastructure ($ENVIRONMENT)"
  if ! ./scripts/deploy.sh --environment "$ENVIRONMENT" $VERBOSE; then
    log_error "Infrastructure deploy failed. Aborting."
    exit 1
  fi
fi

if $DO_APP; then
  log_info "Step: Deploy application ($ENVIRONMENT)"
  if ! ./scripts/deploy-app.sh --environment "$ENVIRONMENT" $VERBOSE; then
    log_error "App deploy failed. Aborting."
    exit 1
  fi
fi

if $DO_TEST; then
  log_info "Step: Run integration tests ($ENVIRONMENT)"
  if [[ -f ./scripts/test-integration.sh ]]; then
    if ! ./scripts/test-integration.sh --environment "$ENVIRONMENT" $VERBOSE; then
      log_warn "Integration tests failed. Proceeding to cleanup."
    fi
  else
    log_warn "No integration test script found (scripts/test-integration.sh)"
  fi
fi

if $DO_CLEANUP; then
  log_info "Step: Cleanup (destroy all resources)"
  if ./scripts/destroy.sh --environment "$ENVIRONMENT" --force $VERBOSE; then
    log_success "Cleanup complete. All resources destroyed."
  else
    log_error "Cleanup failed. Manual intervention may be required."
    exit 1
  fi
fi

echo
log_success "Full cycle complete! (env: $ENVIRONMENT)"