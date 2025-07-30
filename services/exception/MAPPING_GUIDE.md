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

## ** Mapping Flow**

1. **Internal Exception** (Service-specific) → **External Exception** (Standardized)
2. **External Exception** → **RFC 7807 Problem Details** (Client-facing)

## ** Usage Examples**

### **1. Basic Exception Mapping**

```python
from exception import map_service_exception, ErrorCode

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

```python
# In your service exceptions file (e.g., user_service/exceptions.py)
from exception import ErrorCode, exception_mapper

class UserNotFoundException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class UsernameTakenException(Exception):
    def __init__(self, username: str):
        self.message = f"Username '{username}' is already taken"
        super().__init__(self.message)

# Register exceptions with the mapper
exception_mapper.register_exception_mapping(UserNotFoundException, ErrorCode.USER_NOT_FOUND)
exception_mapper.register_exception_mapping(UsernameTakenException, ErrorCode.USERNAME_TAKEN)
```

### **3. Custom Exception Mappers**

```python
from exception import exception_mapper, ProblemDetails, ErrorDetails

class ComplexValidationException(Exception):
    def __init__(self, field_errors: dict):
        self.field_errors = field_errors
        super().__init__("Complex validation failed")

def map_complex_validation(exc: ComplexValidationException, instance: str, trace_id: str, **kwargs):
    """Custom mapper for complex validation exceptions"""
    errors = []
    for field, error_info in exc.field_errors.items():
        errors.append(ErrorDetails(
            field=field,
            message=error_info.get('message', 'Validation failed'),
            value=error_info.get('value')
        ))

    return create_validation_error(
        detail="Complex validation failed",
        errors=errors,
        instance=instance,
        trace_id=trace_id
    )

# Register custom mapper
exception_mapper.register_custom_mapper(ComplexValidationException, map_complex_validation)
```

### **4. Database Exception Mapping**

```python
from exception import map_database_exception

async def create_user(user_data: dict):
    try:
        user = await user_dao.create_user(user_data)
        return user
    except Exception as exc:
        # Map database exceptions to standardized responses
        problem_details = map_database_exception(
            exc=exc,
            instance="/api/v1/users",
            trace_id=request.headers.get("X-Trace-ID")
        )
        return JSONResponse(
            status_code=problem_details.status,
            content=problem_details.dict()
        )
```

### **5. FastAPI Integration with Exception Handlers**

```python
from fastapi import FastAPI, HTTPException
from exception import register_exception_handlers, map_service_exception

app = FastAPI()

# Register automatic exception handlers
register_exception_handlers(app)

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    try:
        user = await user_service.get_user(user_id)
        if not user:
            # This will be automatically handled by the exception handler
            raise HTTPException(
                status_code=404,
                detail=f"User '{user_id}' not found"
            )
        return user
    except UserNotFoundException as exc:
        # Map service-specific exceptions
        problem_details = map_service_exception(
            exc=exc,
            instance=f"/api/v1/users/{user_id}",
            trace_id=request.headers.get("X-Trace-ID")
        )
        return JSONResponse(
            status_code=problem_details.status,
            content=problem_details.dict()
        )
```

## ** Common Mapping Patterns**

### **User Service Exceptions**

```python
# Internal exceptions
class UserNotFoundException(Exception): pass
class UserAlreadyExistsException(Exception): pass
class InvalidCredentialsException(Exception): pass
class UsernameTakenException(Exception): pass
class EmailTakenException(Exception): pass

# Mapping registration
exception_mapper.register_exception_mapping(UserNotFoundException, ErrorCode.USER_NOT_FOUND)
exception_mapper.register_exception_mapping(UserAlreadyExistsException, ErrorCode.RESOURCE_ALREADY_EXISTS)
exception_mapper.register_exception_mapping(InvalidCredentialsException, ErrorCode.INVALID_CREDENTIALS)
exception_mapper.register_exception_mapping(UsernameTakenException, ErrorCode.USERNAME_TAKEN)
exception_mapper.register_exception_mapping(EmailTakenException, ErrorCode.EMAIL_TAKEN)
```

### **Inventory Service Exceptions**

```python
# Internal exceptions
class AssetNotFoundException(Exception): pass
class AssetAlreadyExistsException(Exception): pass
class InvalidAssetDataException(Exception): pass

# Mapping registration
exception_mapper.register_exception_mapping(AssetNotFoundException, ErrorCode.ASSET_NOT_FOUND)
exception_mapper.register_exception_mapping(AssetAlreadyExistsException, ErrorCode.RESOURCE_ALREADY_EXISTS)
exception_mapper.register_exception_mapping(InvalidAssetDataException, ErrorCode.INVALID_INPUT)
```

### **Order Service Exceptions** (Future)

```python
# Internal exceptions
class OrderNotFoundException(Exception): pass
class InsufficientFundsException(Exception): pass
class InvalidOrderStateException(Exception): pass

# Mapping registration
exception_mapper.register_exception_mapping(OrderNotFoundException, ErrorCode.RESOURCE_NOT_FOUND)
exception_mapper.register_exception_mapping(InsufficientFundsException, ErrorCode.INVALID_INPUT)
exception_mapper.register_exception_mapping(InvalidOrderStateException, ErrorCode.INVALID_INPUT)
```

## ** Error Response Examples**

### **User Not Found**
```json
{
  "type": "https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/resource-not-found.md",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "User 'john_doe123' not found",
  "instance": "/api/v1/users/john_doe123",
  "timestamp": "2024-01-15T10:30:00Z",
  "trace_id": "req-12345"
}
```

### **Validation Error**
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
    },
    {
      "field": "password",
      "message": "Password must be at least 12 characters",
      "value": "short"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z",
  "trace_id": "req-12345"
}
```

### **Username Already Taken**
```json
{
  "type": "https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/resource-exists.md",
  "title": "Resource Already Exists",
  "status": 409,
  "detail": "Username 'john_doe123' is already taken",
  "instance": "/api/v1/auth/register",
  "timestamp": "2024-01-15T10:30:00Z",
  "trace_id": "req-12345"
}
```

## ** Best Practices**

### **1. Register Exceptions Early**
```python
# In your service's __init__.py or main.py
from exception import exception_mapper, ErrorCode
from .exceptions import UserNotFoundException, UsernameTakenException

# Register all exceptions when the service starts
def register_exceptions():
    exception_mapper.register_exception_mapping(UserNotFoundException, ErrorCode.USER_NOT_FOUND)
    exception_mapper.register_exception_mapping(UsernameTakenException, ErrorCode.USERNAME_TAKEN)

register_exceptions()
```

### **2. Use Consistent Error Messages**
```python
class UserNotFoundException(Exception):
    def __init__(self, user_id: str):
        self.message = f"User '{user_id}' not found"
        super().__init__(self.message)

class UsernameTakenException(Exception):
    def __init__(self, username: str):
        self.message = f"Username '{username}' is already taken"
        super().__init__(self.message)
```

### **3. Include Trace IDs**
```python
# Always include trace_id for debugging
problem_details = map_service_exception(
    exc=exc,
    instance=request.url.path,
    trace_id=request.headers.get("X-Trace-ID")
)
```

### **4. Use Appropriate HTTP Status Codes**
```python
# Let the mapper handle status codes automatically
problem_details = map_service_exception(exc, instance="/api/v1/users")
return JSONResponse(
    status_code=problem_details.status,  # Automatically set based on error code
    content=problem_details.dict()
)
```

## ** Migration Guide**

### **From Old Error Handling**

**Before:**
```python
# Old way - inconsistent error responses
if not user:
    return JSONResponse(
        status_code=404,
        content={"error": "User not found", "message": f"User {user_id} not found"}
    )
```

**After:**
```python
# New way - standardized error responses
if not user:
    raise UserNotFoundException(f"User '{user_id}' not found")

# Exception handler automatically maps to RFC 7807 format
```

### **From Custom Error Responses**

**Before:**
```python
# Custom error format
return JSONResponse(
    status_code=422,
    content={
        "success": False,
        "errors": [
            {"field": "email", "message": "Invalid email"}
        ]
    }
)
```

**After:**
```python
# Standardized RFC 7807 format
from exception import create_validation_error, ErrorDetails

errors = [ErrorDetails(field="email", message="Invalid email")]
problem_details = create_validation_error(
    detail="The request contains invalid data",
    errors=errors,
    instance="/api/v1/auth/register"
)
return JSONResponse(
    status_code=422,
    content=problem_details.dict()
)
```

## ** Testing Exception Mapping**

```python
import pytest
from exception import map_service_exception, ErrorCode

def test_user_not_found_mapping():
    exc = UserNotFoundException("User 'test' not found")
    problem_details = map_service_exception(
        exc=exc,
        instance="/api/v1/users/test"
    )

    assert problem_details.status == 404
    assert problem_details.title == "Resource Not Found"
    assert "User 'test' not found" in problem_details.detail

def test_validation_error_mapping():
    from pydantic import ValidationError

    # Simulate Pydantic validation error
    errors = [{"loc": ("email",), "msg": "Invalid email", "input": "invalid"}]
    exc = ValidationError.from_exception_dict(errors, {})

    problem_details = map_service_exception(
        exc=exc,
        instance="/api/v1/auth/register"
    )

    assert problem_details.status == 422
    assert problem_details.title == "Validation Error"
    assert problem_details.errors is not None
    assert len(problem_details.errors) == 1
```

This mapping system ensures consistent error handling across all services while maintaining the flexibility to handle service-specific exceptions appropriately.