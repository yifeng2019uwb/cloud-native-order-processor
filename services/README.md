# 🐍 Services Component

> Microservices architecture with FastAPI-based backend services for authentication, order processing, and asset management

## 🚀 Quick Start
- **Prerequisites**: Python 3.11+, pip, virtual environment
- **Build All**: `./build.sh`
- **Build Specific**: `./build.sh user_service`
- **Test Only**: `./build.sh --test-only`
- **Build Only**: `./build.sh --build-only`

## ✨ Key Features
- **Microservices Architecture**: Independent, scalable service design
- **FastAPI Framework**: High-performance, async-capable Python web framework
- **Centralized Security**: JWT authentication and role-based access control
- **Distributed Locking**: Redis-based atomic operations for consistency
- **Comprehensive Testing**: Unit and integration test coverage

## 🔗 Quick Links
- [Design Documentation](../docs/design-docs/services-design.md)
- [Build & Test Scripts](build.md)
- [User Service](user_service/README.md)
- [Order Service](order_service/README.md)
- [Inventory Service](inventory_service/README.md)
- [Common Package](common/README.md)
- [Exception Package](exception/README.md)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All services tested and working
- **Last Updated**: August 20, 2025

## 🎯 Current Status

### ✅ **All Services Working**
- **User Service**: Authentication, user management, balance operations
- **Order Service**: Order processing, trading operations, portfolio management
- **Inventory Service**: Asset management, public inventory data
- **Common Package**: Shared utilities, DAOs, and business logic
- **Exception Package**: Centralized error handling and domain exceptions

### 🚀 **Ready for Production**
- **Security**: JWT authentication and role-based access control
- **Integration**: All services communicating correctly via API Gateway
- **Testing**: Comprehensive test coverage with automated builds
- **Documentation**: Complete API documentation and usage guides

---

## 📁 Project Structure

```
services/
├── README.md                    # This file - main overview
├── build.sh                     # Universal build and test script
├── build.md                     # Detailed build documentation
├── Makefile                     # Build automation targets
├── user_service/                # Authentication and user management
├── order_service/               # Order processing and trading
├── inventory_service/           # Asset inventory management
├── common/                      # Shared utilities and business logic
└── exception/                   # Centralized exception handling
```

## 🏗️ Architecture Overview

### **Service Communication**
```
Frontend → API Gateway → Backend Services → DynamoDB
    ↓           ↓              ↓            ↓
  React    Authentication   FastAPI      Database
           Rate Limiting    Services     Storage
```

### **Service Responsibilities**
- **User Service**: User authentication, profile management, balance operations
- **Order Service**: Order creation, trading operations, portfolio management
- **Inventory Service**: Asset catalog, pricing data, public inventory access
- **Common Package**: Shared DAOs, utilities, and business logic
- **Exception Package**: Centralized error handling and domain exceptions

## 🛠️ Technology Stack

- **Python 3.11+**: Modern Python with type hints and async support
- **FastAPI**: High-performance web framework with automatic API documentation
- **Pydantic**: Data validation and serialization
- **Redis**: Distributed locking and caching
- **DynamoDB**: NoSQL database for scalable data storage
- **Pytest**: Testing framework with comprehensive coverage

## 🔐 Security Model

### **Authentication & Authorization**
- **JWT Tokens**: Secure, stateless authentication
- **Role-Based Access**: Public, customer, and admin roles
- **Password Security**: bcrypt-based password hashing
- **Audit Logging**: Security event tracking and monitoring

### **Data Protection**
- **Input Validation**: Pydantic-based request validation
- **SQL Injection Protection**: Parameterized queries and ORM usage
- **Rate Limiting**: API Gateway-based request throttling
- **Secure Headers**: CORS and security header configuration

## 💰 Business Logic

### **Order Processing**
- **Market Orders**: Buy/sell orders with balance validation
- **Portfolio Management**: Real-time balance updates and transaction history
- **Distributed Locking**: Atomic operations for consistency
- **Transaction Types**: Deposit, withdrawal, order payment, refunds

### **Asset Management**
- **Public Inventory**: Browseable asset catalog with real-time pricing
- **Asset Details**: Comprehensive asset information and metadata
- **Search & Filtering**: Advanced asset discovery capabilities

## 🧪 Testing

- **Test All**: `./build.sh --test-only`
- **Test Specific**: `./build.sh --test-only user_service`
- **Coverage**: `./build.sh --coverage`
- **Integration**: `./test-local.sh --services`

## 🚀 Development Workflow

```bash
# 1. Test specific service
./build.sh --test-only user_service

# 2. Make code changes
# 3. Re-test
./build.sh --test-only user_service

# 4. Build for deployment
./build.sh --build-only user_service
```

## 🔍 Troubleshooting

```bash
# Python version issues
python --version  # Should be 3.11+

# Virtual environment problems
source venv/bin/activate
pip install -r requirements.txt

# Test failures
./build.sh --test-only [service_name]
./build.sh --verbose [service_name]
```

## 📚 Related Documentation

- **[Services Design](../docs/design-docs/services-design.md)**: Architecture and design decisions
- **[Build Documentation](build.md)**: Detailed build and test procedures
- **[Individual Service READMEs](#quick-links)**: Service-specific documentation
- **[API Documentation](../gateway/README.md)**: Gateway and API endpoint information

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the individual service READMEs and design documents.