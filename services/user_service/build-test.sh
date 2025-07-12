#!/bin/bash
# build-test.sh for user_service
# Thin wrapper to call the main build.sh script from the service directory
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICES_ROOT="$SCRIPT_DIR/.."

"$SERVICES_ROOT/build.sh" --coverage 0 user_service "$@"