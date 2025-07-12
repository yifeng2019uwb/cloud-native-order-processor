#!/bin/bash
# build-test.sh for inventory_service
# Thin wrapper to call the main build.sh script from the service directory
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICES_ROOT="$SCRIPT_DIR/.."

# Install dependencies before running build
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "[INFO] Installing dependencies for inventory_service..."
    pip install --upgrade pip
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

"$SERVICES_ROOT/build.sh" --coverage 0 inventory_service "$@"