FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY services/inventory_service/requirements.txt ./inventory_service/
COPY services/common/requirements.txt ./common/

# Install Python dependencies
RUN pip install --no-cache-dir -r ./inventory_service/requirements.txt
RUN pip install --no-cache-dir -r ./common/requirements.txt

# Copy the common src directory structure
COPY services/common/src ./common

# Copy inventory service source code
COPY services/inventory_service/src ./inventory_service/src

# Set Python path to include the common directory for imports
ENV PYTHONPATH="/app:/app/inventory_service/src"

# Set working directory to inventory service
WORKDIR /app/inventory_service/src

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]