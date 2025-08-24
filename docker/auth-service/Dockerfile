# services/auth_service/Dockerfile - Production-Ready (No Tests)
FROM python:3.11-slim

WORKDIR /app

# System dependencies - minimize and clean up
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/*

# Install common package FIRST (best Docker layer caching)
COPY services/common ./common/
RUN cd ./common && \
    pip install --no-cache-dir -e . && \
    pip cache purge

# Install service dependencies
COPY services/auth_service/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# Copy ONLY production source code (NO tests)
COPY services/auth_service/src ./src/

# Security: non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Optimized health check
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=2 \
    CMD curl -f http://localhost:8003/health || exit 1

EXPOSE 8003

# Optimized uvicorn settings
CMD ["uvicorn", "src.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8003", \
     "--workers", "1", \
     "--access-log", \
     "--log-level", "info"]
