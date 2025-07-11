#!/bin/bash
# integration-tests/run-integration-tests.sh
# Run integration tests for the cloud-native order processor
set -e

ENV="dev"
VERBOSE=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --environment) ENV="$2"; shift 2 ;;
    --verbose|-v) VERBOSE="-v"; shift ;;
    *) shift ;;
  esac
done

echo "[INFO] Running integration tests for environment: $ENV"
cd "$(dirname "$0")"

if [[ -f requirements-test.txt ]]; then
  echo "[INFO] Installing integration test dependencies..."
  pip install -r requirements-test.txt
fi

pytest infrastructure/test_infrastructure.py $VERBOSE