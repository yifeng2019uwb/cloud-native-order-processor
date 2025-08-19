# 👤 User Service

> FastAPI microservice for user authentication, profile management, and balance operations

## 🚀 Quick Start
- **Prerequisites**: Python 3.11+, pip, virtual environment
- **Install**: `cd user_service && python -m pip install -e .`
- **Test**: `python -m pytest`
- **Run**: `python -m uvicorn src.main:app --reload --port 8000`

## ✨ Key Features
- **JWT Authentication**: Secure token-based authentication system
- **Balance Management**: Deposit, withdrawal, and transaction tracking
- **Profile Management**: User registration, login, and profile updates
- **Distributed Locking**: Redis-based atomic operations for consistency
- **Security Integration**: Centralized password hashing and audit logging

## 🔗 Quick Links
- [Services Overview](../README.md)
- [Build Script](../build.sh)
- [API Documentation](#api-endpoints)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All features implemented and tested
- **Last Updated**: August 20, 2025

## 🎯 Current Status

### ✅ **All Features Working**
- **Authentication**: User registration, login, and JWT token management
- **Profile Management**: User profile creation, retrieval, and updates
- **Balance Operations**: Deposit, withdrawal, and transaction history
- **Security**: Password hashing, audit logging, and input validation
- **Integration**: Working with API Gateway and other services

---

## 📁 Project Structure

```
user_service/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── balance.py         # Balance management endpoints
│   │   └── profile.py         # Profile management endpoints
│   ├── controllers/            # Business logic controllers
│   │   ├── auth_controller.py # Authentication logic
│   │   ├── balance_controller.py # Balance operations
│   │   └── profile_controller.py # Profile management
│   ├── validation/            # Input validation and business rules
│   │   ├── business_validators.py # Business logic validation
│   │   └── field_validators.py # Field-level validation
│   └── models/                # Pydantic models
│       ├── auth_models.py     # Authentication request/response models
│       ├── balance_models.py  # Balance operation models
│       └── profile_models.py  # Profile management models
├── tests/                     # Test suite
├── requirements.txt            # Python dependencies
└── setup.py                   # Package configuration
```

## 🔐 API Endpoints

### **Authentication**
```bash
POST /auth/register        # Register new user
POST /auth/login           # User login and JWT token
POST /auth/logout          # User logout
```

### **User Management**
```bash
GET  /auth/profile         # Get user profile
PUT  /auth/profile         # Update user profile
```

### **Balance Management**
```bash
GET  /balance              # Get current balance
POST /balance/deposit      # Deposit funds
POST /balance/withdraw     # Withdraw funds
GET  /balance/transactions # Get transaction history
```

### **System**
```bash
GET  /health               # Service health status
GET  /metrics              # Prometheus metrics
```

## 🏗️ Architecture

### **Database Design**
- **Single Table Design**: DynamoDB with composite PK/SK
- **User Entity**: PK=username, SK=USER
- **Balance Entity**: PK=username, SK=BALANCE
- **Transaction Entity**: PK=TRANS#username, SK=timestamp

### **Integration Points**
- **Order Service**: Balance validation before order creation
- **Inventory Service**: Portfolio information for user assets
- **API Gateway**: Authentication and request routing

### **Security Integration**
- **PasswordManager**: Centralized bcrypt password hashing
- **TokenManager**: JWT token creation and validation
- **AuditLogger**: Security event logging and audit trails

## 🛠️ Technology Stack

- **Framework**: FastAPI with async support
- **Database**: AWS DynamoDB via common package
- **Authentication**: JWT tokens with centralized management
- **Validation**: Pydantic models and business validators
- **Testing**: pytest with comprehensive coverage
- **Monitoring**: Prometheus metrics and health checks
- **Security**: Centralized security components

## 🧪 Testing & Development

```bash
# Test this service
../build.sh --test-only user_service

# Test all services
../build.sh --test-only
```

## 🔍 Troubleshooting

```bash
../build.sh --check-prerequisites user_service
```

## 📚 Related Documentation

- **[Services Overview](../README.md)**: Complete services architecture
- **[Common Package](../common/README.md)**: Shared utilities and DAOs
- **[Exception Package](../exception/README.md)**: Error handling patterns
- **[Build Script](../build.sh)**: Automated build and testing

---

**Note**: This service provides complete user authentication and balance management functionality. For system-wide information, see the main services README.