#!/bin/bash
set -e

echo "Starting Order Service..."

# Wait for dependencies
echo "Waiting for dependencies..."
./scripts/wait-for-deps.sh

# Run database migrations if needed
echo "Running database migrations..."
python src/models/migrate.py

# Start the application
echo "Starting the Order Service application..."
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Starting in development mode..."
    python src/app.py
else
    echo "Starting in production mode with Gunicorn..."
    gunicorn --bind 0.0.0.0:8000 \
             --workers 4 \
             --worker-class uvicorn.workers.UvicornWorker \
             --timeout 120 \
             --keep-alive 2 \
             --max-requests 1000 \
             --max-requests-jitter 50 \
             --log-level info \
             --access-logfile - \
             --error-logfile - \
             src.app:app
fi