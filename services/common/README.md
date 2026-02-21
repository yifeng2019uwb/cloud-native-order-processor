# 🔧 Common Package

> **Shared components and utilities** for the Cloud Native Order Processor microservices platform

## 🎯 What is the Common Package?

The Common Package provides shared functionality across all microservices in the CNOP system. It includes data models, database access objects, authentication utilities, exception handling, and shared constants.

## 🏗️ Package Structure

```
common/
├── src/
│   ├── auth/                    # Authentication & Security
│   ├── aws/                     # AWS Integration
│   ├── core/                    # Core Utilities
│   ├── data/                    # Data Layer
│   │   ├── entities/           # Domain models + Database models
│   │   └── dao/                # Data Access Objects
│   ├── exceptions/              # Exception Handling
│   └── shared/                  # Shared Utilities
│       ├── constants/          # Centralized constants
│       └── logging/            # Structured logging
└── tests/                      # Comprehensive test suite
```

## 🔧 Core Components

### **1. Data Layer**
**What it provides**: Database models and data access objects
- **Entities**: User, Order, Asset, Balance, AssetBalance, AssetTransaction
- **DAOs**: UserDAO, OrderDAO, AssetDAO, BalanceDAO, AssetBalanceDAO, AssetTransactionDAO
- **Features**: Type safety, ORM integration, atomic operations, comprehensive error handling

### **2. Authentication & Security**
**What it provides**: Security utilities for all services
- **Password Management**: bcrypt hashing, password validation
- **Token Management**: JWT generation and validation
- **Gateway Integration**: Header validation, user context extraction

### **3. Core Utilities**
**What it provides**: Shared business logic utilities
- **Lock Manager**: User-level locking for atomic operations
- **Transaction Manager**: Distributed transaction coordination
- **Validation**: Shared validation functions and input sanitization

### **4. Exception Handling**
**What it provides**: Consistent error handling across services
- **Exception Hierarchy**: Base exceptions, infrastructure exceptions, business logic exceptions
- **Features**: Structured error handling, error mapping, audit logging, type safety

### **5. Shared Constants**
**What it provides**: Centralized configuration and constants
- **HTTP Status Codes**: Standardized HTTP responses
- **Error Messages**: Consistent error messaging
- **Service Names**: Service identification
- **Field Constraints**: Validation limits

## 🚀 How Services Use It

**Data Operations:**
```python
# Services import and use DAOs
from common.data.dao.user.user_dao import UserDAO
user_dao = UserDAO()
user = user_dao.create_user(user_data)
```

**Authentication:**
```python
# Services use authentication utilities
from common.auth.security.password_manager import PasswordManager
password_manager = PasswordManager()
hashed_password = password_manager.hash_password(password)
```

**Exception Handling:**
```python
# Services use shared exceptions
from common.exceptions import CNOPUserNotFoundException
raise CNOPUserNotFoundException("User not found")
```

**Logging:**
```python
# Services use shared logging
from common.shared.logging import BaseLogger, LoggerName, LogAction
logger = BaseLogger(LoggerName.USER)
logger.info(action=LogAction.USER_REGISTRATION_SUCCESS, message="User created")
```

## 🧪 Testing

**Running Tests:**
```bash
# Run all tests
cd services/common
python -m pytest

# Run specific test categories
python -m pytest tests/data/entities/
python -m pytest tests/data/dao/
python -m pytest tests/core/utils/
python -m pytest tests/auth/
```

## 🔧 Configuration

**Environment Variables:**
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# DynamoDB Tables
USERS_TABLE=users
ORDERS_TABLE=orders
INVENTORY_TABLE=inventory

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
```

## 🚀 Development

**Adding New Components:**
1. **Create Entity**: Add Pydantic model + PynamoDB model
2. **Create DAO**: Add data access object with CRUD operations
3. **Add Tests**: Comprehensive test coverage
4. **Update Constants**: Add any new constants to shared constants
5. **Documentation**: Update this README

**Code Standards:**
- **Type Hints**: All functions must have type hints
- **Docstrings**: Comprehensive documentation
- **Error Handling**: Proper exception handling
- **Logging**: Structured logging for all operations
- **Testing**: Unit tests for all functionality

## 📊 Performance

**Optimization Features:**
- **Connection Pooling**: Efficient database connections
- **Caching**: Redis integration for frequently accessed data
- **Batch Operations**: Efficient bulk operations
- **Query Optimization**: Efficient DynamoDB queries

**Monitoring:**
- **Metrics**: Prometheus metrics; see [docs/METRICS.md](../../docs/METRICS.md) for application metric plan and PromQL
- **Logging**: Structured JSON logging
- **Tracing**: Request correlation IDs
- **Health Checks**: Service health monitoring

## 🔒 Security

**Security Features:**
- **Password Security**: bcrypt hashing with salt
- **JWT Security**: Secure token generation and validation
- **Input Validation**: Comprehensive input sanitization
- **Audit Logging**: Security event tracking

**Best Practices:**
- **Least Privilege**: Minimal required permissions
- **Defense in Depth**: Multiple security layers
- **Secure Defaults**: Secure configuration defaults
- **Regular Updates**: Keep dependencies updated

## 📚 Documentation

**API Documentation:**
- **Entity Models**: Pydantic model documentation
- **DAO Methods**: Data access object documentation
- **Exception Types**: Exception hierarchy documentation
- **Utility Functions**: Helper function documentation

**Architecture Documentation:**
- **Data Flow**: How data flows through the system
- **Error Handling**: Exception handling patterns
- **Security Model**: Authentication and authorization
- **Performance**: Optimization strategies

---

**🔧 Built for**: Production microservices with enterprise-grade reliability and security

**🛡️ Perfect for**: Shared functionality across multiple services with consistent patterns

**🔒 Questions about implementation?** Check the source code or open an issue

*Built with type safety, comprehensive testing, and production-ready patterns*