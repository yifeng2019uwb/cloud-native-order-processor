FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY services/user_service/requirements.txt ./user_service/
COPY services/common/requirements.txt ./common/

# Install Python dependencies
RUN pip install --no-cache-dir -r ./user_service/requirements.txt
RUN pip install --no-cache-dir -r ./common/requirements.txt

# Copy the common src directory structure
COPY services/common/src ./common

# Copy the exception module
COPY services/exception ./exception

# Copy user service source code
COPY services/user_service/src ./user_service/src

# Set Python path to include the common directory for imports
ENV PYTHONPATH="/app:/app/user_service/src:/app/exception"

# Set working directory to user service
WORKDIR /app/user_service/src

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application as a module
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
