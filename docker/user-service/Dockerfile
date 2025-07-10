FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY services/user-service/requirements.txt ./user-service/
COPY services/common/requirements.txt ./common/

# Install Python dependencies
RUN pip install --no-cache-dir -r ./user-service/requirements.txt
RUN pip install --no-cache-dir -r ./common/requirements.txt

# Copy source code
COPY services/common ./common
COPY services/user-service/src ./user-service/src

# Set Python path to find common package
ENV PYTHONPATH="/app/common/src:/app/user-service/src"

# Set working directory to user service
WORKDIR /app/user-service/src

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "main.py"]
