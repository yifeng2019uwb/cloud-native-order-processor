#!/bin/bash

# Simple Lambda build script
# Run this from the project root: ./lambda_package/build.sh

set -e

echo "🔨 Building Lambda package..."

# Clean previous builds
rm -rf package/
rm -f lambda_package.zip

# Create package directory
mkdir -p package

# Copy handler to root level
cp lambda_handler.py package/lambda_handler.py

# Install dependencies (using Python 3.11 for Lambda compatibility)
python3.11 -m pip install -r requirements.txt -t package/

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