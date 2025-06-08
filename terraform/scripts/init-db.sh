#!/bin/bash
set -e

echo "🗄️ Initializing database schema..."

# Get database endpoint from Terraform output
DB_ENDPOINT=$(terraform output -raw database_endpoint)
DB_PASSWORD=$(terraform output -raw db_password)

# Wait for RDS to be available
echo "⏳ Waiting for RDS to be ready..."
aws rds wait db-instance-available --db-instance-identifier order-processor-dev-postgres

# Run the SQL script
echo "📝 Creating schemas and tables..."
PGPASSWORD="$DB_PASSWORD" psql \
  -h "$DB_ENDPOINT" \
  -U orderuser \
  -d orderprocessor \
  -f scripts/init-database.sql

echo "✅ Database initialization completed!"