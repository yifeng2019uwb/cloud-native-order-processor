#!/bin/bash

# Docker deployment script for Order Processor
# This script builds and runs the application using Docker Compose

set -e  # Exit on any error

echo "🚀 Starting Order Processor Docker deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Navigate to the docker directory
cd "$(dirname "$0")/../docker"

echo "📦 Building Docker images..."
docker-compose build

echo "🔄 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo "🏥 Checking service health..."

# Check user-service health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ User service is healthy"
else
    echo "❌ User service health check failed"
    docker-compose logs user-service
    exit 1
fi

# Check frontend (if accessible)
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "⚠️ Frontend health check failed (may still be starting)"
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Service URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "🔧 Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart services: docker-compose restart"
echo ""

# Show running containers
echo "📊 Running containers:"
docker-compose ps