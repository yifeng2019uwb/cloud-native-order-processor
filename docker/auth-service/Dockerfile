# Auth Service Dockerfile - Multi-Stage Build (FIXED)
# Stage 1: Builder (with build dependencies)
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY services/common/requirements.txt ./common/requirements.txt
COPY services/auth_service/requirements.txt ./auth_service/requirements.txt

# Install Python dependencies with --user flag
RUN pip install --no-cache-dir --user \
    -r ./common/requirements.txt \
    -r ./auth_service/requirements.txt

# Stage 2: Runtime (minimal, no build tools)
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies (curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder to /usr/local (system-wide)
COPY --from=builder /root/.local/lib /usr/local/lib
COPY --from=builder /root/.local/bin /usr/local/bin

# Copy source code (common and service)
COPY services/common/src ./common
COPY services/auth_service/src ./auth_service/src

# Set Python path
ENV PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Set working directory to service src
WORKDIR /app/auth_service/src

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]