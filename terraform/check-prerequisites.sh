#!/bin/bash
# check-prerequisites.sh

echo "🔍 Checking prerequisites for AWS Secrets Manager setup..."

# Check AWS CLI
if command -v aws &> /dev/null; then
    echo "✅ AWS CLI is installed"
    aws --version
else
    echo "❌ AWS CLI is not installed"
    echo "Install it: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check jq
if command -v jq &> /dev/null; then
    echo "✅ jq is installed"
    jq --version
else
    echo "❌ jq is not installed"
    echo "Install it:"
    echo "  Ubuntu/Debian: sudo apt-get install jq"
    echo "  macOS: brew install jq"
    echo "  Amazon Linux: sudo yum install jq"
    exit 1
fi

# Check PostgreSQL client
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL client is installed"
    psql --version
else
    echo "❌ PostgreSQL client (psql) is not installed"
    echo "Install it:"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql-client"
    echo "  macOS: brew install postgresql"
    echo "  Amazon Linux: sudo yum install postgresql"
    exit 1
fi

# Check AWS credentials
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ AWS credentials are configured"
    aws sts get-caller-identity
else
    echo "❌ AWS credentials are not configured"
    echo "Configure them: aws configure"
    exit 1
fi

# Check Terraform
if command -v terraform &> /dev/null; then
    echo "✅ Terraform is installed"
    terraform version
else
    echo "❌ Terraform is not installed"
    exit 1
fi

echo ""
echo "🎉 All prerequisites are met! You can proceed with the Secrets Manager setup."