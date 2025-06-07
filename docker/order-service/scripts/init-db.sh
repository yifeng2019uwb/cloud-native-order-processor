#!/bin/bash
set -e

# This script runs during PostgreSQL container initialization

echo "Initializing Order Service database..."

# Create additional databases if needed
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    -- Create schemas
    CREATE SCHEMA IF NOT EXISTS orders;
    CREATE SCHEMA IF NOT EXISTS audit;
    
    -- Grant permissions
    GRANT ALL PRIVILEGES ON SCHEMA orders TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON SCHEMA audit TO $POSTGRES_USER;
    
    -- Create basic tables structure (will be managed by migrations)
    CREATE TABLE IF NOT EXISTS orders.orders (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        customer_id UUID NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        total_amount DECIMAL(10,2) NOT NULL,
        currency VARCHAR(3) NOT NULL DEFAULT 'USD',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    CREATE TABLE IF NOT EXISTS audit.order_events (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        order_id UUID NOT NULL,
        event_type VARCHAR(50) NOT NULL,
        event_data JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders.orders(customer_id);
    CREATE INDEX IF NOT EXISTS idx_orders_status ON orders.orders(status);
    CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders.orders(created_at);
    CREATE INDEX IF NOT EXISTS idx_audit_order_id ON audit.order_events(order_id);
    CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit.order_events(event_type);
    
EOSQL

echo "Database initialization completed!"