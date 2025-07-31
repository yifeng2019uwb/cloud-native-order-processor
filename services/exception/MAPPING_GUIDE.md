# Exception Mapping Guide

This guide explains how to map internal service-specific exceptions to external standardized exceptions using the `services/exception/` package.

## ** Architecture Overview**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Internal        │    │ Exception        │    │ RFC 7807        │
│ Exceptions      │───▶│ Mapping Layer    │───▶│ Problem Details │
│ (Service-Specific)│    │ (Standardized)   │    │ (Client-Facing) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## ** Exception Categories**

### **1. Shared Exceptions (Exposed to Gateway)**
These exceptions are **mapped to external error codes** and exposed to clients:

```python
# Authentication (401)
InvalidCredentialsException, TokenExpiredException, TokenInvalidException

# Authorization (403)
AuthorizationException, AccessDeniedException, InsufficientPermissionsException

# Resources (404, 409)
EntityNotFoundException, UserNotFoundException, OrderNotFoundException, AssetNotFoundException
EntityAlreadyExistsException

# Validation (422)
EntityValidationException, UserValidationException, OrderValidationException, AssetValidationException

# Internal Server (500)
InternalServerException
```

### **2. Common Exceptions (Internal Only)**
These exceptions are **NOT mapped** and should be handled internally by services:

```python
# Database (internal)
DatabaseConnectionException, DatabaseOperationException

# Configuration (internal)
ConfigurationException

# External Services (internal)
AWSServiceException, ExternalServiceException

# Generic (internal)
CommonServerException
```

## ** Simplified Error Codes (7 total)**

```python
# Authentication Errors (401)
AUTHENTICATION_FAILED = "authentication_failed"    # All auth issues (invalid creds, expired token, etc.)

# Authorization Errors (403)
ACCESS_DENIED = "access_denied"                    # All permission issues

# Resource Errors (404, 409)
RESOURCE_NOT_FOUND = "resource_not_found"          # All "not found" cases
RESOURCE_ALREADY_EXISTS = "resource_already_exists" # All "already exists" cases

# Validation Errors (422)
VALIDATION_ERROR = "validation_error"              # All validation issues

# Server Errors (500, 503)
INTERNAL_SERVER_ERROR = "internal_server_error"    # All internal issues
SERVICE_UNAVAILABLE = "service_unavailable"        # External service failures
```

## ** Usage Examples**

### **1. Basic Exception Mapping**

```python
from exception import map_service_exception

# In your service controller
async def get_user(user_id: str):
    try:
        user = await user_service.get_user(user_id)
        if not user:
            raise UserNotFoundException(f"User '{user_id}' not found")
        return user
    except UserNotFoundException as exc:
        # Map internal exception to external standardized response
        problem_details = map_service_exception(
            exc=exc,
            instance="/api/v1/users/{user_id}",
            trace_id=request.headers.get("X-Trace-ID")
        )
        return JSONResponse(
            status_code=problem_details.status,
            content=problem_details.dict()
        )
```

### **2. Automatic Exception Registration**

The exception mapper automatically registers all shared exceptions from the common package:

```python
# Shared exceptions are automatically mapped:
UserNotFoundException → RESOURCE_NOT_FOUND
EntityAlreadyExistsException → RESOURCE_ALREADY_EXISTS
InvalidCredentialsException → AUTHENTICATION_FAILED
OrderValidationException → VALIDATION_ERROR
InternalServerException → INTERNAL_SERVER_ERROR

# Common exceptions are NOT mapped (security):
DatabaseOperationException → INTERNAL_SERVER_ERROR (fallback)
ConfigurationException → INTERNAL_SERVER_ERROR (fallback)
AWSServiceException → INTERNAL_SERVER_ERROR (fallback)
```

### **3. FastAPI Integration**

```python
from fastapi import FastAPI
from exception import register_exception_handlers

app = FastAPI()

# Register exception handlers for automatic error handling
register_exception_handlers(app)

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    # Exceptions are automatically mapped to RFC 7807 Problem Details
    if not user_exists(user_id):
        raise UserNotFoundException(f"User '{user_id}' not found")
    return {"user_id": user_id}
```

### **4. Manual Error Handling**

```python
from exception import create_problem_details, ErrorCode

# Create custom problem details
problem_details = create_problem_details(
    error_code=ErrorCode.VALIDATION_ERROR,
    detail="Invalid email format",
    instance="/api/v1/auth/register",
    trace_id="req-12345"
)
```

## ** Exception Mapping Examples**

### **Authentication Exceptions**
```python
# All authentication issues map to AUTHENTICATION_FAILED
InvalidCredentialsException → AUTHENTICATION_FAILED (401)
TokenExpiredException → AUTHENTICATION_FAILED (401)
TokenInvalidException → AUTHENTICATION_FAILED (401)
```

### **Resource Exceptions**
```python
# All "not found" issues map to RESOURCE_NOT_FOUND
UserNotFoundException → RESOURCE_NOT_FOUND (404)
OrderNotFoundException → RESOURCE_NOT_FOUND (404)
AssetNotFoundException → RESOURCE_NOT_FOUND (404)

# All "already exists" issues map to RESOURCE_ALREADY_EXISTS
EntityAlreadyExistsException → RESOURCE_ALREADY_EXISTS (409)
```

### **Validation Exceptions**
```python
# All validation issues map to VALIDATION_ERROR
UserValidationException → VALIDATION_ERROR (422)
OrderValidationException → VALIDATION_ERROR (422)
AssetValidationException → VALIDATION_ERROR (422)
```

### **Server Exceptions**
```python
# All internal issues map to INTERNAL_SERVER_ERROR
InternalServerException → INTERNAL_SERVER_ERROR (500)

# All external service issues map to SERVICE_UNAVAILABLE
ExternalServiceException → SERVICE_UNAVAILABLE (503)
```

**Note**: Common exceptions (DatabaseOperationException, ConfigurationException, AWSServiceException) are handled at the service level and should not be mapped to external error codes. They automatically fall back to INTERNAL_SERVER_ERROR for security.

## ** Security Benefits**

1. **Internal Details Hidden**: Database errors, AWS issues, and configuration problems are never exposed
2. **Consistent Error Format**: All services return the same error structure
3. **Simplified Client Integration**: Only 7 error codes to handle
4. **RFC 7807 Compliant**: Industry standard error responses

## ** Error Response Format**

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

## ** Integration Steps**

### **1. Install the Exception Package**
```bash
cd services/exception
pip install -e .
```

### **2. Configure Exception Mappings**
```python
from exception import configure_service_exceptions

# Configure shared exception mappings
configure_service_exceptions()
```

### **3. Register FastAPI Handlers**
```python
from fastapi import FastAPI
from exception import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
```

### **4. Use in Your Services**
```python
# Raise shared exceptions for business logic
if not user_exists(user_id):
    raise UserNotFoundException(f"User '{user_id}' not found")

# Handle common exceptions internally
try:
    result = database_operation()
except DatabaseOperationException as exc:
    # Log the error internally
    logger.error(f"Database error: {exc}")
    # Re-raise as InternalServerException
    raise InternalServerException("Failed to process request")
```

## ** Testing**

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