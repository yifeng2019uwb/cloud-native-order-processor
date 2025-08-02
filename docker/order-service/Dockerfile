FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY services/order_service/requirements.txt ./order_service/
COPY services/common/requirements.txt ./common/

# Install Python dependencies
RUN pip install --no-cache-dir -r ./order_service/requirements.txt
RUN pip install --no-cache-dir -r ./common/requirements.txt

# Copy the common src directory structure
COPY services/common/src ./common

# Copy order service source code
COPY services/order_service/src ./order_service/src

# Set Python path to include the common directory for imports
ENV PYTHONPATH="/app:/app/order_service/src"

# Set working directory to order service
WORKDIR /app/order_service/src

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run the application as a module
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]