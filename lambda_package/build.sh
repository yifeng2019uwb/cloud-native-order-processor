#!/bin/bash

# Lambda build script - Includes real FastAPI services
# Run this from the project root: ./lambda_package/build.sh

set -e

echo "🔨 Building Lambda package with real services..."

# Clean previous builds
rm -rf package/
rm -f lambda_package.zip

# Create package directory
mkdir -p package

# Copy handler to root level
cp lambda_handler.py package/lambda_handler.py

# Copy actual service code
echo "📁 Copying real service modules..."

# Copy user service
if [ -d "../services/user_service/src" ]; then
    mkdir -p package/services/user_service/src
    cp -r ../services/user_service/src/* package/services/user_service/src/
    echo "✅ User service copied"
else
    echo "⚠️ User service not found"
fi

# Copy inventory service
if [ -d "../services/inventory_service/src" ]; then
    mkdir -p package/services/inventory_service/src
    cp -r ../services/inventory_service/src/* package/services/inventory_service/src/
    echo "✅ Inventory service copied"
else
    echo "⚠️ Inventory service not found"
fi

# Copy common package
if [ -d "../services/common/src" ]; then
    mkdir -p package/services/common/src
    cp -r ../services/common/src/* package/services/common/src/
    echo "✅ Common package copied"
else
    echo "⚠️ Common package not found"
fi

# Install dependencies (using Python 3.11 for Lambda compatibility)
echo "📦 Installing dependencies..."
python3.11 -m pip install -r requirements.txt -t package/

# Install service-specific dependencies
if [ -f "../services/user_service/requirements.txt" ]; then
    echo "📦 Installing user service dependencies..."
    python3.11 -m pip install -r ../services/user_service/requirements.txt -t package/
fi

if [ -f "../services/inventory_service/requirements.txt" ]; then
    echo "📦 Installing inventory service dependencies..."
    python3.11 -m pip install -r ../services/inventory_service/requirements.txt -t package/
fi

if [ -f "../services/common/requirements.txt" ]; then
    echo "📦 Installing common package dependencies..."
    python3.11 -m pip install -r ../services/common/requirements.txt -t package/
fi

# Create zip file
cd package
zip -r ../lambda_package.zip .
cd ..

echo "✅ Lambda package built: lambda_package.zip"
echo "📦 Package size: $(du -h lambda_package.zip | cut -f1)"

echo ""
echo "🚀 Ready to deploy to AWS Lambda!"
echo "   Handler: lambda_package.lambda_handler"
echo "   Package: lambda_package.zip"
echo "   Services: Real FastAPI services included"