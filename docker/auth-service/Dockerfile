# Auth Service Dockerfile - Following CNOP Standard Template
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
COPY services/auth_service/requirements.txt ./auth_service/

# Install Python dependencies
RUN pip install --no-cache-dir -r ./common/requirements.txt
RUN pip install --no-cache-dir -r ./auth_service/requirements.txt

# Copy the common source directory
COPY services/common/src ./common

# Copy service source code
COPY services/auth_service/src ./auth_service/src

# Set Python path to include the app directory for imports
ENV PYTHONPATH="/app"

# Set working directory to service src for proper imports
WORKDIR /app/auth_service/src

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
