#!/bin/bash

# Frontend Redeploy Script
# Usage: ./scripts/redeploy-frontend.sh [--no-cache]

set -e  # Exit on any error

echo "🚀 Frontend Redeploy Script"
echo "==========================="

# Parse arguments
NO_CACHE=""
if [[ "$1" == "--no-cache" ]]; then
    NO_CACHE="--no-cache"
    echo "📝 Using --no-cache flag"
fi

# Get script directory to ensure we're in the right location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📂 Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

echo ""
echo "🛑 Step 1: Stopping and removing existing frontend container..."
docker stop order-processor-frontend 2>/dev/null || echo "   ℹ️  Container not running"
docker rm order-processor-frontend 2>/dev/null || echo "   ℹ️  Container not found"

echo ""
echo "🗑️  Step 2: Removing existing frontend image..."
docker rmi docker-frontend 2>/dev/null || echo "   ℹ️  Image not found"

echo ""
echo "🏗️  Step 3: Building frontend..."
cd frontend
echo "   📦 Running npm build..."
npm run build

echo ""
echo "🐳 Step 4: Building Docker image..."
cd "$PROJECT_ROOT"
if [[ -n "$NO_CACHE" ]]; then
    echo "   🔥 Building with --no-cache..."
    docker build --no-cache -f docker/frontend/Dockerfile -t docker-frontend .
else
    echo "   📦 Building with cache..."
    docker build -f docker/frontend/Dockerfile -t docker-frontend .
fi

echo ""
echo "🚀 Step 5: Deploying frontend container..."
docker-compose -f docker/docker-compose.yml up -d frontend

echo ""
echo "✅ Step 6: Verifying deployment..."
sleep 3

# Check if container is running
if docker ps | grep -q "order-processor-frontend"; then
    echo "   ✅ Frontend container is running"

    # Test if frontend is accessible
    if curl -s http://localhost:3000 > /dev/null; then
        echo "   ✅ Frontend is accessible at http://localhost:3000"
        echo ""
        echo "🎉 Frontend redeployment completed successfully!"
        echo ""
        echo "🔗 Frontend URL: http://localhost:3000"
        echo "📊 Container status:"
        docker ps | grep frontend
    else
        echo "   ⚠️  Frontend container is running but not accessible"
        echo "   📋 Checking container logs..."
        docker logs order-processor-frontend --tail 10
    fi
else
    echo "   ❌ Frontend container failed to start"
    echo "   📋 Checking logs..."
    docker logs order-processor-frontend --tail 20 2>/dev/null || echo "   No logs available"
    exit 1
fi

echo ""
echo "📝 To check logs: docker logs order-processor-frontend"
echo "🔄 To redeploy again: $0 [--no-cache]"
