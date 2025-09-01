# 🚨 Exception Package

> Standardized exception handling with RFC 7807 Problem Details for HTTP APIs

## 🚀 Quick Start
- **Prerequisites**: Python 3.11+, pip, virtual environment
- **Install**: `cd exception && python -m pip install -e .`
- **Test**: `python -m pytest`
- **Use**: Import in other services via `from exception import ...`

## ✨ Key Features
- **RFC 7807 Compliant**: Problem Details for HTTP APIs standard
- **Type Safe**: Built with Pydantic for validation and type safety
- **FastAPI Integration**: Ready-to-use exception handlers
- **Standardized Error Codes**: 7 simplified error codes across all services
- **Security by Design**: Internal exceptions never exposed to clients

## 🔗 Quick Links
- [Services Overview](../README.md)
- [Build Script](../build.sh)
- [Error Codes](#error-codes)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All components implemented and tested
- **Last Updated**: August 20, 2025

## 🎯 Current Status

### ✅ **All Components Working**
- **Exception Mapping**: Internal to external error mapping
- **FastAPI Integration**: Automatic exception handlers
- **Error Codes**: Standardized error responses
- **Security**: Internal exceptions protected from exposure
- **Testing**: Comprehensive test coverage

---

## 📁 Package Structure

```
exception/
├── __init__.py               # Package exports
├── error_codes.py            # Standardized error code definitions
├── error_models.py           # Pydantic models for Problem Details
├── exception_handlers.py     # FastAPI exception handlers
├── exception_mapping.py      # Exception mapping logic
├── MAPPING_GUIDE.md          # Exception mapping guide
├── tests/                    # Test suite
├── requirements.txt           # Python dependencies
└── setup.py                  # Package configuration
```

## 🏗️ Architecture

### **Exception Flow**
```
Internal Exceptions → Exception Mapping Layer → RFC 7807 Problem Details
(Service-Specific)    (Standardized)           (Client-Facing)
```

### **Exception Categories**
- **Shared Exceptions**: Authentication, Authorization, Resource, Validation, Internal Server
- **Common Exceptions**: Database, Configuration, External Service (internal only)

## 🔐 Error Codes

### **Standardized Error Codes**
```python
class ErrorCode(Enum):
    AUTHENTICATION_ERROR = "AUTH_001"
    AUTHORIZATION_ERROR = "AUTH_002"
    RESOURCE_NOT_FOUND = "RES_001"
    VALIDATION_ERROR = "VAL_001"
    INTERNAL_SERVER_ERROR = "INT_001"
    SERVICE_UNAVAILABLE = "SVC_001"
    RATE_LIMIT_EXCEEDED = "RATE_001"
```

### **Problem Details Structure**
```python
{
    "type": "https://api.example.com/errors/AUTH_001",
    "title": "Authentication Error",
    "status": 401,
    "detail": "Invalid credentials provided",
    "instance": "/api/v1/auth/login",
    "trace_id": "req-12345",
    "timestamp": "2025-08-20T10:00:00Z"
}
```

## 🛠️ Technology Stack

- **Framework**: Python 3.11+ with type hints
- **Validation**: Pydantic models and data validation
- **Standards**: RFC 7807 Problem Details for HTTP APIs
- **Integration**: FastAPI exception handling
- **Testing**: pytest with comprehensive coverage
- **Security**: Internal exception protection

## 🧪 Testing

### **Test Coverage**
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test file
python -m pytest tests/test_exception_mapper.py

# Run with verbose output
python -m pytest -v
```

### **Test Structure**
- **Unit Tests**: Individual component testing with mocking
- **Integration Tests**: FastAPI integration validation
- **Exception Tests**: Error mapping and response validation
- **Security Tests**: Internal exception protection

## 🔄 Development Workflow

### **Local Development**
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run tests
python -m pytest

# 4. Install in development mode
pip install -e .
```

### **Code Changes**
```bash
# 1. Make code changes
# 2. Run tests to verify
python -m pytest

# 3. Check code quality
python -m flake8 src/
python -m black src/

# 4. Commit changes
git add .
git commit -m "Description of changes"
```

## 🔍 Troubleshooting

### **Common Issues**
```bash
# Python version issues
python --version  # Should be 3.11+

# Virtual environment problems
source venv/bin/activate
pip install -r requirements.txt

# Test failures
python -m pytest -v
python -m pytest --tb=short
```

### **Import Issues**
```bash
# Ensure package is installed
pip install -e .

# Check import paths
python -c "from exception import create_problem_details; print('Import successful')"
```

## 📚 Related Documentation

- **[Services Overview](../README.md)**: Complete services architecture
- **[Common Package](../common/README.md)**: Shared utilities and components
- **[Build Script](../build.sh)**: Automated build and testing
- **[RFC 7807](https://tools.ietf.org/html/rfc7807)**: Problem Details for HTTP APIs

---

**Note**: This package provides standardized exception handling for all microservices. For service-specific information, see the individual service READMEs.