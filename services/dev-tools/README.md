# Development Tools Package

This package contains shared development utilities and tools that can be used across all services in the CNOP system.

## Structure

```
dev-tools/
├── __init__.py              # Package initialization
├── mock-env.py              # Mock environment setup
├── common-validation.py     # Shared validation functions
└── README.md               # This file
```

## Usage

### Mock Environment Setup

```python
from common.dev_tools.mock_env import setup_mock_environment

# Setup mock environment variables for import validation
setup_mock_environment()
```

This sets up consistent environment variables across all services:
- DynamoDB table names
- AWS configuration
- JWT configuration
- Service configuration
- Redis configuration

### Import Validation

```python
from common.dev_tools.mock_env import validate_import, validate_service_imports

# Validate a single import
success = validate_import('main', 'Main application')

# Validate multiple imports for a service
import_tests = [
    ('main', 'Main application'),
    ('controllers.auth.register', 'Auth controller'),
    ('user_exceptions', 'Service exceptions')
]
success = validate_service_imports('user_service', import_tests)
```

### Common Validation Functions

```python
from common.dev_tools.common_validation import (
    check_python_syntax,
    check_prerequisites,
    validate_service_structure
)

# Check Python syntax
success, file_count, errors = check_python_syntax('src')

# Check prerequisites
prereq_ok, issues = check_prerequisites()

# Validate service structure
structure_ok, issues = validate_service_structure('user_service')
```

## Integration with dev.sh Scripts

All service `dev.sh` scripts can now use these shared utilities:

```bash
# In dev.sh scripts
python3 -c "
from common.dev_tools.mock_env import setup_mock_environment, validate_import
setup_mock_environment()
validate_import('main', 'Main application')
"
```

## Benefits

1. **Consistency**: All services use the same mock environment
2. **Maintainability**: Centralized validation logic
3. **Reusability**: Shared functions across all services
4. **Professional**: Standardized development workflow

## Adding New Services

When adding a new service, simply import from `common.dev_tools`:

```python
from common.dev_tools.mock_env import setup_mock_environment
from common.dev_tools.common_validation import check_prerequisites

# Use the shared utilities
setup_mock_environment()
prereq_ok, issues = check_prerequisites()
```
