#!/bin/bash
set -e

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
until nc -z postgres 5432; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "PostgreSQL is up!"

# Wait for Redis
echo "Waiting for Redis..."
until nc -z redis 6379; do
    echo "Redis is unavailable - sleeping"
    sleep 2
done
echo "Redis is up!"

# Wait for LocalStack
echo "Waiting for LocalStack..."
until nc -z localstack 4566; do
    echo "LocalStack is unavailable - sleeping"
    sleep 2
done
echo "LocalStack is up!"

# Wait for LocalStack services to be ready
echo "Waiting for LocalStack services to initialize..."
until curl -f http://localstack:4566/_localstack/health > /dev/null 2>&1; do
    echo "LocalStack services not ready - sleeping"
    sleep 5
done
echo "LocalStack services are ready!"

# Give services a moment to fully initialize
echo "Giving services time to fully initialize..."
sleep 15

echo "All dependencies are ready!"