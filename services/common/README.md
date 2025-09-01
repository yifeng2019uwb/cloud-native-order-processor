# 🔧 Common Package

> Shared components, utilities, and data access objects for all microservices

## 🚀 Quick Start
- **Prerequisites**: Python 3.11+, pip, virtual environment
- **Install**: `cd common && python -m pip install -e .`
- **Test**: `python -m pytest`
- **Use**: Import in other services via `from common import ...`

## ✨ Key Features
- **Shared Entities**: User, Order, Inventory, and Asset data models
- **Data Access Objects**: Database operations and business logic
- **Security Management**: Centralized password hashing and JWT handling
- **Database Utilities**: DynamoDB connections and health checks
- **Exception Handling**: Domain-specific exceptions for all services

## 🔗 Quick Links
- [Services Overview](../README.md)
- [Build Script](../build.sh)
- [Entity Models](#entities)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All components implemented and tested
- **Last Updated**: August 20, 2025

## 🎯 Current Status

### ✅ **All Components Working**
- **Entities**: Complete data models for all services
- **DAOs**: Database operations and business logic
- **Security**: Password hashing, JWT management, and audit logging
- **Database**: DynamoDB connections and health monitoring
- **Exceptions**: Comprehensive error handling across all services

---

## 📁 Package Structure

```
common/
├── src/
│   ├── data/              # Data layer components
│   │   ├── entities/      # Data models and entities
│   │   │   ├── user/      # User, Balance, BalanceTransaction
│   │   │   ├── order/     # Order and related models
│   │   │   ├── inventory/ # Asset and inventory models
│   │   │   └── asset/     # Asset balance and transaction models
│   │   ├── dao/           # Data Access Objects
│   │   │   ├── user/      # User and balance DAOs
│   │   │   ├── order/     # Order DAO
│   │   │   ├── inventory/ # Asset DAO
│   │   │   └── asset/     # Asset management DAOs
│   │   ├── database/      # Database connections and utilities
│   │   └── exceptions/    # Database exception classes
│   ├── auth/              # Authentication components
│   │   ├── security/      # Security management components
│   │   │   ├── password_manager.py    # Password hashing and validation
│   │   │   ├── token_manager.py       # JWT token management
│   │   │   └── audit_logger.py        # Security event logging
│   │   ├── gateway/       # Gateway integration
│   │   └── exceptions/    # Auth exception classes
│   ├── core/              # Core business logic
│   │   ├── utils/         # Core utilities
│   │   └── validation/    # Core validation
│   ├── aws/               # AWS utilities (STS, etc.)
│   ├── exceptions/        # Shared exception classes
│   └── shared/            # Shared utilities
│       ├── health/        # Health check utilities
│       ├── logging/       # Logging utilities
│       └── monitoring/    # Monitoring utilities
├── tests/                  # Test suite
├── requirements.txt         # Python dependencies
└── setup.py                # Package configuration
```

## 🏗️ Architecture

### **Service-Based Organization**
- **User Service**: User, Balance, BalanceTransaction entities
- **Order Service**: Order and related models
- **Inventory Service**: Asset and inventory models
- **Asset Management**: AssetBalance, AssetTransaction models

### **Database Design**
- **Single Table Approach**: Service-specific tables with composite keys
- **DynamoDB**: Serverless, pay-per-use, minimal operational overhead
- **Composite Keys**: Efficient querying with PK/SK patterns
- **GSI Support**: Global Secondary Indexes for complex queries

### **Design Philosophy**
- **Cost Efficiency**: Minimize RCU/WCU usage through efficient key design
- **Development Velocity**: Prioritize rapid iteration over enterprise complexity
- **Atomic Operations**: Conditional expressions for cost optimization
- **Simplified Queries**: Single-table design for personal project scale

## 📊 Core Components

### **Entities**
- **User Entities**: User, Balance, BalanceTransaction, TransactionType, TransactionStatus
- **Order Entities**: Order, OrderCreate, OrderResponse, OrderType, OrderStatus
- **Inventory Entities**: Asset, AssetListResponse
- **Asset Management**: AssetBalance, AssetTransaction, AssetTransactionType, AssetTransactionStatus

### **Data Access Objects (DAOs)**
- **UserDAO**: User CRUD operations with integrated security
- **BalanceDAO**: Balance and transaction management
- **OrderDAO**: Order lifecycle management
- **AssetDAO**: Asset information and operations
- **AssetBalanceDAO**: Asset balance tracking
- **AssetTransactionDAO**: Asset transaction history

### **Security Management**
- **PasswordManager**: bcrypt-based password hashing and verification
- **TokenManager**: JWT token creation, validation, and management
- **AuditLogger**: Security event logging and audit trails

### **Database Utilities**
- **DynamoDB Connection**: Database connection management
- **Health Checks**: Service health monitoring
- **AWS Integration**: STS client for role assumption

## 🛠️ Technology Stack

- **Framework**: Python 3.11+ with type hints
- **Database**: AWS DynamoDB via boto3
- **Security**: bcrypt for password hashing, PyJWT for JWT handling
- **Validation**: Pydantic models and data validation
- **Testing**: pytest with comprehensive coverage
- **Monitoring**: Health checks and AWS integration

## 🧪 Testing

### **Test Coverage**
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test file
python -m pytest tests/test_entities.py

# Run with verbose output
python -m pytest -v
```

### **Test Structure**
- **Unit Tests**: Individual component testing with mocking
- **Integration Tests**: Database and external service integration
- **Entity Tests**: Data model validation and business logic
- **DAO Tests**: Database operation validation

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
python -c "from common.entities.user import User; print('Import successful')"
```

## 📚 Related Documentation

- **[Services Overview](../README.md)**: Complete services architecture
- **[Exception Package](../exception/README.md)**: Error handling patterns
- **[Build Script](../build.sh)**: Automated build and testing
- **[Individual Services](../user_service/README.md)**: Service-specific usage

---

**Note**: This package provides shared components for all microservices. For service-specific information, see the individual service READMEs.