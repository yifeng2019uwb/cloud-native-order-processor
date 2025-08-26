# Quick Reference: Dockerfile Template

## Template Location
`docker/standard/Dockerfile.template`

## What to Replace
- `SERVICE_NAME` → Your service name
- `SERVICE_PORT` → Your service port

## Key Points
1. **Working Directory**: Always ends at `/app/SERVICE_NAME/src`
2. **Import Strategy**: Copy common source, don't install as package
3. **Python Path**: **Must set `ENV PYTHONPATH="/app"`** for imports to work
4. **Health Check**: Must have `/health` endpoint
5. **Command**: `python -m uvicorn main:app --host 0.0.0.0 --port SERVICE_PORT`

## Example Commands
```bash
# Copy template
cp docker/standard/Dockerfile.template docker/auth_service/Dockerfile

# Build service
docker build -f docker/auth_service/Dockerfile .

# Run service
docker run -p 8003:8003 your-image-name
```

## File Structure in Container
```
/app/
├── common/           # Common package source
├── SERVICE_NAME/     # Your service source
│   └── src/         # Working directory
│       ├── main.py
│       └── ...
└── ...
```

## Common Issues
- ❌ `WORKDIR /app` + `src.main:app` = Import errors
- ✅ `WORKDIR /app/SERVICE_NAME/src` + `main:app` = Works
- ❌ Installing common as package = Complex dependency management
- ✅ Copying common source = Simple and reliable
- ❌ Missing `ENV PYTHONPATH="/app"` = Import resolution fails
- ✅ `ENV PYTHONPATH="/app"` = Common package imports work correctly
