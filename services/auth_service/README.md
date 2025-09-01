# Auth Service

Independent JWT validation service for Order Processor.

## Structure

```
src/
├── __init__.py          # Package initialization
├── main.py              # FastAPI app entry point (includes root endpoint)
├── controllers/         # API endpoint handlers
│   ├── __init__.py      # Controllers package
│   ├── validate.py      # /internal/auth/validate endpoint
│   └── health.py        # /health endpoint
├── api_models/          # API request/response models
├── auth_exceptions/     # Auth-specific exceptions
└── utils/               # Utility functions
```

## Endpoints

- `GET /` - Service information (in main.py)
- `POST /internal/auth/validate` - JWT validation (internal Gateway only)
- `GET /health` - Health check for K8s probes
- `GET /docs` - API documentation (FastAPI auto-generated)

## Development

```bash
./dev.sh build    # Build service
./dev.sh test     # Run tests
./dev.sh clean    # Clean build artifacts
```

## Status

**Phase 1**: Basic skeleton structure created
**Next**: Implement JWT validation logic

## Notes

- Root endpoint (`/`) is directly in main.py (following other services pattern)
- Health endpoint uses separate controller with router
- Metrics endpoint not implemented yet (following other services pattern)
