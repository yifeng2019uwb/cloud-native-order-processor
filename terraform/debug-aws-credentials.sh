#!/bin/bash
# debug-aws-credentials.sh

echo "🔍 Debugging AWS credentials..."

# Check if credentials file exists
echo "📁 Checking AWS credentials file:"
if [ -f ~/.aws/credentials ]; then
    echo "✅ ~/.aws/credentials exists"
    echo "📄 Contents (without sensitive data):"
    grep -E "^\[.*\]$" ~/.aws/credentials || echo "No profiles found"
else
    echo "❌ ~/.aws/credentials does not exist"
fi

# Check if config file exists
echo ""
echo "📁 Checking AWS config file:"
if [ -f ~/.aws/config ]; then
    echo "✅ ~/.aws/config exists"
    echo "📄 Contents:"
    cat ~/.aws/config
else
    echo "❌ ~/.aws/config does not exist"
fi

# Check environment variables
echo ""
echo "🌍 Checking AWS environment variables:"
if [ -n "$AWS_ACCESS_KEY_ID" ]; then
    echo "✅ AWS_ACCESS_KEY_ID is set"
else
    echo "❌ AWS_ACCESS_KEY_ID is not set"
fi

if [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "✅ AWS_SECRET_ACCESS_KEY is set"
else
    echo "❌ AWS_SECRET_ACCESS_KEY is not set"
fi

if [ -n "$AWS_DEFAULT_REGION" ]; then
    echo "✅ AWS_DEFAULT_REGION is set to: $AWS_DEFAULT_REGION"
else
    echo "❌ AWS_DEFAULT_REGION is not set"
fi

if [ -n "$AWS_PROFILE" ]; then
    echo "✅ AWS_PROFILE is set to: $AWS_PROFILE"
else
    echo "❌ AWS_PROFILE is not set (will use default)"
fi

# Try different ways to test credentials
echo ""
echo "🧪 Testing AWS credentials with different methods:"

echo "1. Using default profile:"
aws sts get-caller-identity 2>&1

echo ""
echo "2. Listing available profiles:"
aws configure list-profiles 2>&1

echo ""
echo "3. Current configuration:"
aws configure list 2>&1

echo ""
echo "💡 Suggestions:"
echo "   - If no profiles found, run: aws configure"
echo "   - If using named profile, run: export AWS_PROFILE=your-profile-name"
echo "   - If using environment variables, make sure they're set in current shell"