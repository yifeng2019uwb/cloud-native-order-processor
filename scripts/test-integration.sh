#!/bin/bash
# scripts/test-integration.sh
# Wrapper to run integration tests from the integration-tests package
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$DIR/integration-tests/run-integration-tests.sh" "$@"