# Standard Dockerfile Template for CNOP Python Services

This directory contains a standardized Dockerfile template that all Python microservices should follow for consistency.

## Template File

- `Dockerfile.template` - Base template for all Python services

## How to Use

### 1. Copy the Template
```bash
cp docker/standard/Dockerfile.template docker/YOUR_SERVICE/Dockerfile
```

### 2. Replace Placeholders
Replace these placeholders in your Dockerfile:
- `SERVICE_NAME` → Your service name (e.g., `auth_service`, `user_service`)
- `SERVICE_PORT` → Your service port (e.g., `8000`, `8001`, `8003`)

### 3. Example for Auth Service
```dockerfile
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
```

## Key Principles

1. **Consistent Structure**: All services follow the same pattern
2. **Working Directory**: Always set `WORKDIR` to the service's src directory
3. **Import Strategy**: Copy common package source, not install as package
4. **Python Path**: Set `PYTHONPATH="/app"` for proper import resolution
5. **Health Checks**: Standardized health check configuration
6. **Dependencies**: Install common requirements first, then service requirements

## Benefits

- **Consistency**: All services behave the same way
- **Maintainability**: Easy to update all services at once
- **Debugging**: Predictable structure across all services
- **Onboarding**: New developers know what to expect
- **Import Resolution**: PYTHONPATH ensures common package imports work correctly

## Migration Path

1. **Phase 1**: Use this template for new services
2. **Phase 2**: Gradually migrate existing services
3. **Phase 3**: Remove old individual Dockerfiles

## Notes

- This template uses the "copy source" approach (like user_service) rather than "install package" approach
- All services should have a `/health` endpoint for health checks
- The working directory is set to the service's src directory to avoid import path issues
- **PYTHONPATH="/app"** is crucial for resolving imports from the common package
