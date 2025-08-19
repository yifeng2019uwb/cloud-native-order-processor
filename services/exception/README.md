# Order Processor Exception Package

Standardized exception handling package for the Order Processor system, implementing RFC 7807 Problem Details for HTTP APIs.

## Features

- **RFC 7807 Compliant**: Implements Problem Details for HTTP APIs standard
- **Type Safe**: Built with Pydantic for validation and type safety
- **FastAPI Integration**: Ready-to-use exception handlers for FastAPI
- **Standardized Error Codes**: 7 simplified error codes across all services
- **Security by Design**: Internal exceptions are never exposed to clients
- **Self-Documenting**: Error responses include links to documentation

## Architecture

The exception package provides a secure mapping layer between internal service exceptions and external client-facing error responses:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Internal        │    │ Exception        │    │ RFC 7807        │
│ Exceptions      │───▶│ Mapping Layer    │───▶│ Problem Details │
│ (Service-Specific)│    │ (Standardized)   │    │ (Client-Facing) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Exception Categories

**Shared Exceptions** (Exposed to Gateway):
- Authentication, Authorization, Resource, Validation, and Internal Server exceptions
- Mapped to standardized error codes
- Exposed to external clients

**Common Exceptions** (Internal Only):
- Database, Configuration, and External Service exceptions
- NOT mapped to external error codes
- Handled internally for security

## Installation

```bash
cd services/exception
pip install -e .
```

## Quick Start

### Basic Usage

```python
from exception import create_problem_details, ErrorCode

# Create a validation error
problem_details = create_problem_details(
    error_code=ErrorCode.VALIDATION_ERROR,
    detail="The request contains invalid data",
    instance="/api/v1/auth/register",
    trace_id="req-12345"
)
```

### FastAPI Integration

```python
from fastapi import FastAPI
from exception import register_exception_handlers

app = FastAPI()

# Register exception handlers
register_exception_handlers(app)

@app.get("/users/{username}")
async def get_user(username: str):
    if not user_exists(username):
        raise UserNotFoundException(f"User '{username}' not found")
    return {"username": username}
```

### Manual Exception Mapping

```python
from exception import map_service_exception

# Map internal exceptions to standardized responses
try:
    user = await user_service.get_user(username)
    if not user:
        raise UserNotFoundException(f"User '{username}' not found")
    return user
except UserNotFoundException as exc:
    problem_details = map_service_exception(
        exc=exc,
        instance=f"/api/v1/users/{username}",
        trace_id=request.headers.get("X-Trace-ID")
    )
    return JSONResponse(
        status_code=problem_details.status,
        content=problem_details.dict()
    )
```

## Error Codes

The package provides 7 standardized error codes:

### Authentication Errors (401)
- `AUTHENTICATION_FAILED`: All authentication issues (invalid credentials, expired tokens, etc.)

### Authorization Errors (403)
- `ACCESS_DENIED`: All permission and access control issues

### Resource Errors (404, 409)
- `RESOURCE_NOT_FOUND`: All "not found" cases
- `RESOURCE_ALREADY_EXISTS`: All "already exists" cases

### Validation Errors (422)
- `VALIDATION_ERROR`: All validation and input format issues

### Server Errors (500, 503)
- `INTERNAL_SERVER_ERROR`: All internal server issues
- `SERVICE_UNAVAILABLE`: External service failures

## Exception Mapping

### Shared Exceptions (Exposed)

```python
# Authentication
InvalidCredentialsException → AUTHENTICATION_FAILED (401)
TokenExpiredException → AUTHENTICATION_FAILED (401)

# Resources
UserNotFoundException → RESOURCE_NOT_FOUND (404)
EntityAlreadyExistsException → RESOURCE_ALREADY_EXISTS (409)

# Validation
OrderValidationException → VALIDATION_ERROR (422)

# Internal Server
InternalServerException → INTERNAL_SERVER_ERROR (500)
```

### Common Exceptions (Internal Only)

```python
# These are NOT mapped and fall back to INTERNAL_SERVER_ERROR
DatabaseOperationException → INTERNAL_SERVER_ERROR (500)
ConfigurationException → INTERNAL_SERVER_ERROR (500)
AWSServiceException → INTERNAL_SERVER_ERROR (500)
```

## Error Response Format

All error responses follow RFC 7807 Problem Details format:

```json
{
    "type": "https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/validation_error.md",
    "title": "Validation Error",
    "status": 422,
    "detail": "The request contains invalid data. Please check your input and try again.",
    "instance": "/api/v1/auth/register",
    "timestamp": "2024-01-15T10:30:00Z",
    "trace_id": "req-12345"
}
```

## Security Benefits

1. **Internal Details Hidden**: Database errors, AWS issues, and configuration problems are never exposed to clients
2. **Consistent Error Format**: All services return the same error structure
3. **Simplified Client Integration**: Only 7 error codes to handle
4. **RFC 7807 Compliant**: Industry standard error responses

## Integration Steps

### 1. Install the Package
```bash
cd services/exception
pip install -e .
```

### 2. Configure Exception Mappings
```python
from exception import configure_service_exceptions

# Configure shared exception mappings
configure_service_exceptions()
```

### 3. Register FastAPI Handlers
```python
from fastapi import FastAPI
from exception import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
```

### 4. Use in Your Services
```python
# Raise shared exceptions for business logic
    if not user_exists(username):
        raise UserNotFoundException(f"User '{username}' not found")

# Handle common exceptions internally
try:
    result = database_operation()
except DatabaseOperationException as exc:
    # Log the error internally
    logger.error(f"Database error: {exc}")
    # Re-raise as InternalServerException
    raise InternalServerException("Failed to process request")
```

## Testing

The exception package includes comprehensive tests to verify:

- ✅ Exception mapping functionality
- ✅ RFC 7807 compliance
- ✅ Security (common exceptions not exposed)
- ✅ Error code standardization
- ✅ FastAPI integration

Run tests with:
```bash
cd services/exception
python3 -c "from exception_mapping import configure_service_exceptions; configure_service_exceptions(); print('✅ Exception mapping configured successfully')"
```

## API Reference

### Core Functions

- `configure_service_exceptions()`: Configure shared exception mappings
- `map_service_exception(exc, instance, trace_id)`: Map exception to ProblemDetails
- `create_problem_details(error_code, detail, instance, errors, trace_id)`: Create ProblemDetails
- `register_exception_handlers(app)`: Register FastAPI exception handlers

### Error Codes

- `ErrorCode.AUTHENTICATION_FAILED`: Authentication errors (401)
- `ErrorCode.ACCESS_DENIED`: Authorization errors (403)
- `ErrorCode.RESOURCE_NOT_FOUND`: Resource not found (404)
- `ErrorCode.RESOURCE_ALREADY_EXISTS`: Resource already exists (409)
- `ErrorCode.VALIDATION_ERROR`: Validation errors (422)
- `ErrorCode.INTERNAL_SERVER_ERROR`: Internal server errors (500)
- `ErrorCode.SERVICE_UNAVAILABLE`: Service unavailable (503)

### Models

- `ProblemDetails`: RFC 7807 Problem Details model
- `ErrorDetails`: Field-specific validation error model

## Contributing

When adding new exceptions:

1. **Shared Exceptions**: Add to `common/src/exceptions/shared_exceptions.py` and register in `configure_service_exceptions()`
2. **Common Exceptions**: Add to `common/src/exceptions/exceptions.py` (NOT mapped)
3. **Service-Specific Exceptions**: Add to individual service exception modules

## License

This package is part of the Order Processor system and follows the same licensing terms.