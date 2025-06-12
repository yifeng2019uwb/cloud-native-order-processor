#!/bin/bash
# scripts/workspace-cleanup.sh
# Simple cleanup script for build-test generated files

set -e

echo "🧹 Cleaning up workspace..."

# Clean up all build-test generated files
find . -type d -name "__pycache__" -exec rm -rf {} + && \
find . -name "*.pyc" -delete && \
rm -rf services/*/dist/ services/*/build/ services/*/*.egg-info/ && \
rm -rf test-results/ .test-workspace/ tests/reports/ .pytest_cache/ && \
rm -f .coverage coverage.xml && rm -rf htmlcov/ && \
docker system prune -f 2>/dev/null || true

echo "✅ Workspace cleanup completed!"