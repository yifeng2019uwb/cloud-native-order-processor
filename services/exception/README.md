# Order Processor Exception Package

Standardized exception handling package for the Order Processor system, implementing RFC 7807 Problem Details for HTTP APIs.

## Features

- **RFC 7807 Compliant**: Implements Problem Details for HTTP APIs standard
- **Type Safe**: Built with Pydantic for validation and type safety
- **FastAPI Integration**: Ready-to-use exception handlers for FastAPI
- **Standardized Error Codes**: Consistent error codes across all services
- **Self-Documenting**: Error responses include links to documentation

## Installation

```bash
pip install -e .
```

## Quick Start

### Basic Usage

```python
from exception import create_problem_details, ErrorCode, ErrorDetails

# Create a validation error
errors = [
    ErrorDetails(field="email", message="Invalid email format", value="invalid-email")
]

problem_details = create_problem_details(
    error_code=ErrorCode.VALIDATION_ERROR,
    detail="The request contains invalid data",
    errors=errors,
    instance="/api/v1/auth/register"
)
```

### FastAPI Integration

```python
from fastapi import FastAPI
from exception import register_exception_handlers

app = FastAPI()

# Register exception handlers
register_exception_handlers(app)

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    if not user_exists(user_id):
        raise HTTPException(
            status_code=404,
            detail=f"User '{user_id}' not found"
        )
    return {"user_id": user_id}
```

### Manual Error Handling

```python
from exception import (
    handle_validation_error,
    handle_authentication_error,
    handle_resource_not_found
)

# Validation error
validation_error = handle_validation_error(
    detail="Invalid input data",
    errors=[ErrorDetails(field="username", message="Username is required")],
    instance="/api/v1/auth/register"
)

# Authentication error
auth_error = handle_authentication_error(
    detail="Invalid credentials",
    instance="/api/v1/auth/login"
)

# Resource not found
not_found_error = handle_resource_not_found(
    detail="User not found",
    instance="/api/v1/users/123"
)
```

## Error Codes

### Validation Errors (422)
- `VALIDATION_ERROR`: General validation failure
- `INVALID_INPUT`: Invalid input data
- `MISSING_REQUIRED_FIELD`: Required field is missing
- `INVALID_FORMAT`: Invalid data format

### Authentication Errors (401)
- `AUTHENTICATION_FAILED`: Authentication failed
- `INVALID_CREDENTIALS`: Invalid username/password
- `TOKEN_EXPIRED`: JWT token expired
- `TOKEN_INVALID`: Invalid JWT token
- `MISSING_TOKEN`: No authentication token provided

### Authorization Errors (403)
- `INSUFFICIENT_PERMISSIONS`: User lacks required permissions
- `ACCESS_DENIED`: Access denied to resource

### Resource Errors (404, 409)
- `RESOURCE_NOT_FOUND`: Resource not found
- `USER_NOT_FOUND`: User not found
- `ASSET_NOT_FOUND`: Asset not found
- `RESOURCE_ALREADY_EXISTS`: Resource already exists
- `USERNAME_TAKEN`: Username already taken
- `EMAIL_TAKEN`: Email already registered

### Server Errors (500)
- `INTERNAL_SERVER_ERROR`: Unexpected server error
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable
- `DATABASE_ERROR`: Database operation failed
- `EXTERNAL_SERVICE_ERROR`: External service error

## Response Format

All error responses follow RFC 7807 Problem Details format:

```json
{
  "type": "https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/validation-error.md",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request contains invalid data",
  "instance": "/api/v1/auth/register",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "value": "invalid-email"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z",
  "trace_id": "req-12345"
}
```

## Documentation

Error documentation is available at:
- [Validation Error](./docs/errors/validation-error.md)
- [Authentication Error](./docs/errors/authentication-error.md)
- [Resource Not Found](./docs/errors/resource-not-found.md)
- [Resource Exists](./docs/errors/resource-exists.md)
- [Internal Error](./docs/errors/internal-error.md)

## Development

### Running Tests

```bash
pytest tests/
```

### Building Package

```bash
python setup.py sdist bdist_wheel
```