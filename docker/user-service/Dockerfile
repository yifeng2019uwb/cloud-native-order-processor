# User Service Dockerfile - Following CNOP Standard Template
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY services/common/requirements.txt ./common/
COPY services/user_service/requirements.txt ./user_service/

# Install Python dependencies
RUN pip install --no-cache-dir -r ./common/requirements.txt
RUN pip install --no-cache-dir -r ./user_service/requirements.txt

# Copy the common source directory
COPY services/common/src ./common

# Copy user service source code
COPY services/user_service/src ./user_service/src

# Set Python path to include the app directory for imports
ENV PYTHONPATH="/app"

# Set working directory to service src for proper imports
WORKDIR /app/user_service/src

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
