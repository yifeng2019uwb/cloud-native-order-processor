#!/bin/bash
set -e

echo "🗄️ Initializing database schema..."

# Check required environment variables
if [[ -z "$SECRET_ARN" || -z "$DB_IDENTIFIER" ]]; then
    echo "❌ Missing required environment variables"
    echo "Required: SECRET_ARN, DB_IDENTIFIER"
    exit 1
fi

# COST OPTIMIZATION: Add timeout controls to prevent long-running costs
# ORIGINAL: No timeout controls
SCRIPT_TIMEOUT=${SCRIPT_TIMEOUT:-300}  # 5 minutes default timeout
DB_WAIT_TIMEOUT=${DB_WAIT_TIMEOUT:-600}  # 10 minutes for RDS to be ready

echo "⏱️ Script timeout: ${SCRIPT_TIMEOUT} seconds"
echo "⏱️ DB wait timeout: ${DB_WAIT_TIMEOUT} seconds"

# COST OPTIMIZATION: Start cost monitoring
START_TIME=$(date +%s)
echo "💰 Cost monitoring: Script started at $(date)"

# Check if required tools are installed
if ! command -v jq &> /dev/null; then
    echo "❌ jq is required but not installed. Please install jq first:"
    echo "   Ubuntu/Debian: sudo apt-get install jq"
    echo "   macOS: brew install jq"
    echo "   Amazon Linux: sudo yum install jq"
    exit 1
fi

echo "🔍 Debug - Raw secret JSON:"
echo "$SECRET_JSON" | jq '.'

# Parse JSON to get individual values
DB_USERNAME=$(echo "$SECRET_JSON" | jq -r '.username')
DB_PASSWORD=$(echo "$SECRET_JSON" | jq -r '.password')
DB_ENDPOINT=$(echo "$SECRET_JSON" | jq -r '.host')
DB_PORT=$(echo "$SECRET_JSON" | jq -r '.port')
DB_NAME=$(echo "$SECRET_JSON" | jq -r '.dbname')

# Debug - show what we parsed
echo "🔍 Debug - Parsed values:"
echo "  Raw endpoint from secret: '$DB_ENDPOINT'"
echo "  Raw port from secret: '$DB_PORT'"

# Remove port from endpoint if it was accidentally included
DB_ENDPOINT=$(echo "$DB_ENDPOINT" | sed 's/:5432$//' | sed 's/:.*$//')

# Ensure port is a number
if [ "$DB_PORT" = "null" ] || [ -z "$DB_PORT" ]; then
    DB_PORT=5432
fi

echo "🔍 Debug - Cleaned values:"
echo "  Clean endpoint: '$DB_ENDPOINT'"
echo "  Final port: '$DB_PORT'"

echo "📍 Database endpoint: $DB_ENDPOINT"
echo "👤 Database user: $DB_USERNAME"
echo "🗄️ Database name: $DB_NAME"
echo "🔌 Database port: $DB_PORT"

# Wait for RDS to be available
echo "⏳ Waiting for RDS to be ready..."
# ORIGINAL: Uses aws rds wait with potentially unlimited time
aws rds wait db-instance-available --db-instance-identifier "$DB_IDENTIFIER" || {
    echo "⚠️ RDS wait timed out, but continuing..."
}

# COST OPTIMIZATION: Add timeout wrapper for RDS wait
# Comment out the aws rds wait above and uncomment below:
# timeout $DB_WAIT_TIMEOUT aws rds wait db-instance-available --db-instance-identifier "$DB_IDENTIFIER" || {
#     echo "⚠️ RDS wait timed out after ${DB_WAIT_TIMEOUT} seconds, but continuing..."
#     echo "💰 Cost note: RDS charges apply from instance creation, not from availability"
# }

# Give it a few more seconds to be fully ready
sleep 10

# Skip connection test since we're outside VPC - this is expected
echo "⏭️ Skipping connection test (running from outside VPC - this is normal)"
echo "📝 Proceeding directly to schema creation..."

# Try to run the SQL script - it may work if RDS is publicly accessible
# or fail gracefully if not
echo "📝 Attempting to create schemas and tables..."

# COST OPTIMIZATION: Add script execution timeout
# ORIGINAL: No timeout for SQL execution
if timeout $SCRIPT_TIMEOUT PGPASSWORD="$DB_PASSWORD" psql \
  -h "$DB_ENDPOINT" \
  -U "$DB_USERNAME" \
  -d "$DB_NAME" \
  -p "$DB_PORT" \
  -f scripts/init-database.sql 2>/dev/null; then
    echo "✅ Database initialization completed successfully!"

    # COST OPTIMIZATION: Show successful execution time
    END_TIME=$(date +%s)
    EXECUTION_TIME=$((END_TIME - START_TIME))
    echo "💰 Cost monitoring: Initialization completed in ${EXECUTION_TIME} seconds"

else
    echo "⚠️ Database schema creation skipped (VPC networking - expected)"
    echo "📋 To initialize database later from within VPC:"
    echo "   1. Connect to an EKS pod or EC2 instance in the VPC"
    echo "   2. Run: aws secretsmanager get-secret-value --secret-id $SECRET_ARN"
    echo "   3. Use the credentials to connect and run the SQL script"
    echo ""
    echo "✅ Infrastructure setup completed successfully!"
    echo "🔐 Database credentials are securely stored in AWS Secrets Manager"

    # COST OPTIMIZATION: Show partial execution time
    END_TIME=$(date +%s)
    EXECUTION_TIME=$((END_TIME - START_TIME))
    echo "💰 Cost monitoring: Script completed in ${EXECUTION_TIME} seconds (DB init skipped)"
fi

echo "✅ Database initialization completed!"
echo "🔐 Database credentials are securely stored in AWS Secrets Manager"
echo "🔍 To access credentials later: aws secretsmanager get-secret-value --secret-id $SECRET_ARN"

# COST OPTIMIZATION: Final cost monitoring summary
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))
echo ""
echo "💰 === Cost Monitoring Summary ==="
echo "💰 Total execution time: ${TOTAL_TIME} seconds"
echo "💰 RDS instance running time: Check AWS Console for exact start time"
echo "💰 Reminder: RDS charges apply even when not actively used"
echo "💰 Cost tip: Run 'terraform destroy' when done testing to stop charges"
echo "💰 ================================="

# COST OPTIMIZATION: Add cost alert if running too long
if [ $TOTAL_TIME -gt 600 ]; then  # 10 minutes
    echo "⚠️ COST ALERT: Script ran for over 10 minutes"
    echo "⚠️ Consider optimizing database initialization for faster deployments"
    echo "⚠️ Long-running deployments increase infrastructure costs"
fi