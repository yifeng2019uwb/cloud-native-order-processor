# Order Service Dockerfile - Multi-Stage Build
# Stage 1: Builder (with build dependencies)
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY services/common/requirements.txt ./common/
COPY services/order_service/requirements.txt ./order_service/

# Install Python dependencies (cache enabled for faster rebuilds)
# Using --user flag to install to /root/.local
RUN pip install --user \
    -r ./common/requirements.txt \
    -r ./order_service/requirements.txt

# Stage 2: Runtime (minimal, no build tools)
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies (curl for health checks)
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Ensure local packages are in PATH
ENV PATH=/root/.local/bin:$PATH

# Copy the common source directory
COPY services/common/src ./common

# Copy order service source code
COPY services/order_service/src ./order_service/src

# Set Python path to include the app directory for imports
ENV PYTHONPATH="/app"

# Set working directory to service src for proper imports
WORKDIR /app/order_service/src

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run the application as a module
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
