#!/bin/bash

# Quick ECR Build Script - Minimal version for immediate deployment
set -e

# Configuration
AWS_REGION="us-west-2"
ECR_REPOSITORY="order-processor-dev"
SERVICE_NAME="order-service"

echo "🚀 Quick ECR Build and Push"
echo "=========================="

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "📋 Configuration:"
echo "   AWS Account: $AWS_ACCOUNT_ID"
echo "   Region: $AWS_REGION"
echo "   Registry: $ECR_REGISTRY"
echo "   Repository: $ECR_REPOSITORY"
echo ""

# Step 1: ECR Login
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Step 2: Create a simple Dockerfile for order-service if needed
if [ ! -f "docker/order-service/Dockerfile.simple" ]; then
    echo "📝 Creating simplified Dockerfile..."
    cat > docker/order-service/Dockerfile.simple << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY services/common/requirements.txt ./common-requirements.txt
COPY services/order-service/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r common-requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/common ./common
COPY services/order-service/src ./src

# Install common package
RUN pip install -e ./common

# Set Python path
ENV PYTHONPATH=/app:/app/common:/app/src

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Simple health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "src/app.py"]
EOF
fi

# Step 3: Build the image
echo "🔨 Building Docker image..."
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
IMAGE_TAG="$ECR_REGISTRY/$ECR_REPOSITORY:$SERVICE_NAME-$TIMESTAMP"
IMAGE_LATEST="$ECR_REGISTRY/$ECR_REPOSITORY:$SERVICE_NAME-latest"

docker build -f docker/order-service/Dockerfile.simple -t $IMAGE_TAG -t $IMAGE_LATEST .

# Step 4: Push to ECR
echo "📤 Pushing to ECR..."
docker push $IMAGE_TAG
docker push $IMAGE_LATEST

echo ""
echo "✅ Success! Your image is now in ECR:"
echo "   📦 $IMAGE_TAG"
echo "   📦 $IMAGE_LATEST"
echo ""
echo "🎯 Next: Deploy to EKS using these image URIs"
echo ""

# Show ECR repository contents
echo "📋 ECR Repository Contents:"
aws ecr list-images --repository-name $ECR_REPOSITORY --region $AWS_REGION --output table