# Cloud-Native Order Processor - Services

## 🏗️ Architecture Overview

This project implements a **microservices architecture** with four main components:

1. **API Gateway** (Go/Gin) - Entry point, authentication, rate limiting ✅ **PRODUCTION READY**
2. **User Service** (FastAPI) - Authentication, user management, balance management ✅ **PRODUCTION READY**
3. **Order Service** (FastAPI) - Order processing, trading operations 🔄 **IN DEVELOPMENT**
4. **Inventory Service** (FastAPI) - Asset management, public inventory data ✅ **PRODUCTION READY**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   User Service  │
│   (React)       │◄──►│   (Go/Gin)      │◄──►│   (FastAPI)     │
│                 │    │   ✅ PRODUCTION  │    │   ✅ PRODUCTION  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Order Service   │    │ Inventory       │
                       │ (FastAPI)       │    │ Service         │
                       │ 🔄 IN DEV       │    │ (FastAPI)       │
                       └─────────────────┘    │ ✅ PRODUCTION    │
                                              └─────────────────┘
```

## 🔐 Security Model ✅ **COMPLETED**

### **Centralized Security Management** ✅ **COMPLETED**
- **PasswordManager**: bcrypt-based password hashing and verification ✅
- **TokenManager**: JWT token creation, verification, and management ✅
- **AuditLogger**: Security event logging and audit trails ✅
- **Service Integration**: All services using centralized security components ✅

### **Public Access (No Auth Required)** ✅ **WORKING**
- **Inventory Service**: Browse assets, view details ✅ **WORKING**
- **Health Checks**: Service status endpoints ✅ **WORKING**

### **Authenticated Access (JWT Required)** ✅ **WORKING**
- **User Service**: Login, registration, profile management, balance operations ✅ **WORKING**
- **Order Service**: Order creation, management, cancellation 🔄 **IN DEVELOPMENT**
- **API Gateway**: All authenticated endpoints ✅ **WORKING**

### **Exception Handling** ✅ **COMPLETED**
- **Domain-Specific Exceptions**: All DAOs properly raise specific exceptions ✅
- **Consistent Error Patterns**: Unified exception handling across services ✅
- **Error Propagation**: Proper error flow from DAOs to controllers ✅
- **Test Coverage**: Comprehensive exception testing ✅

## 💰 Order-Balance Integration ✅ **COMPLETED**

### **Market Order Flow** ✅ **DESIGNED**
```
Market Buy Order:
1. User creates order → Order Service validates balance
2. If sufficient balance → Create order + ORDER_PAYMENT transaction
3. Update user balance (deduct funds)
4. Return success/fail to user

Market Sell Order:
1. User creates order → Order Service creates order
2. When order executes → Create ORDER_PAYMENT transaction (receive funds)
3. Update user balance (add funds)
4. Return success/fail to user
```

### **Balance Management** ✅ **COMPLETED**
- **Automatic balance creation** on user registration ✅
- **Transaction history** for all balance changes ✅
- **Real-time balance updates** for order operations ✅
- **Balance validation** before order creation ✅
- **Distributed locking** for atomic operations ✅
- **Insufficient balance error handling** ✅

### **Transaction Types** ✅ **IMPLEMENTED**
- `DEPOSIT` - User adds money to account ✅
- `WITHDRAW` - User takes money out ✅
- `ORDER_PAYMENT` - Money spent/received from orders ✅
- `ORDER_REFUND` - Money returned from cancelled orders ✅
- `SYSTEM_ADJUSTMENT` - System corrections ✅

### **JWT Flow** ✅ **WORKING**
```
1. User → User Service: POST /login (username/password)
2. User Service → User: JWT token
3. User → Gateway: Request with Authorization: Bearer <JWT>
4. Gateway → Backend Service: Forward request with JWT validation
```

## 📦 Services

### **1. User Service** (`services/user_service/`) ✅ **PRODUCTION READY**

**Purpose**: User authentication, management, and balance operations

**Key Features**:
- ✅ JWT token generation and validation
- ✅ User registration and login
- ✅ Password authentication (centralized via PasswordManager)
- ✅ User profile management
- ✅ **Balance management** (deposits, withdrawals, transactions) ✅ **COMPLETED**
- ✅ **Account balance tracking** with transaction history ✅ **COMPLETED**
- ✅ **Distributed locking** for atomic operations ✅ **COMPLETED**
- ✅ **Insufficient balance error handling** ✅ **COMPLETED**
- ✅ Secure exception handling with domain-specific exceptions ✅ **COMPLETED**
- ✅ CloudWatch logging (Lambda ready)
- ✅ **AWS DynamoDB integration** ✅ **WORKING**
- ✅ **Fresh AWS credentials** ✅ **WORKING**

**API Endpoints** ✅ **ALL WORKING**:
```
POST /auth/register        - User registration ✅
POST /auth/login           - User authentication ✅
GET  /auth/me              - Get user profile ✅
PUT  /auth/profile         - Update user profile ✅
POST /auth/logout          - User logout ✅
GET  /balance              - Get user balance ✅
POST /balance/deposit      - Deposit funds ✅
POST /balance/withdraw     - Withdraw funds ✅
GET  /balance/transactions - Transaction history ✅
GET  /health               - Health check ✅
```

**Technology Stack**:
- **Framework**: FastAPI
- **Database**: DynamoDB (via common package) ✅ **WORKING**
- **Authentication**: JWT (via TokenManager) ✅ **COMPLETED**
- **Password Hashing**: bcrypt (via PasswordManager) ✅ **COMPLETED**
- **Deployment**: Lambda/Kubernetes ready ✅ **WORKING**

### **2. Order Service** (`services/order_service/`) 🔄 **IN DEVELOPMENT**

**Purpose**: Order processing and trading operations

**Key Features**:
- 🔄 **Market order processing** (buy/sell)
- 🔄 **Order lifecycle management** (creation, execution, completion)
- 🔄 **Balance validation** before order creation
- 🔄 **Order-balance integration** with automatic transactions
- 🔄 **Order history and tracking**
- 🔄 **Secure exception handling**
- 🔄 **AWS DynamoDB integration** via common package
- 🔄 **Fresh AWS credentials**

**API Endpoints**:
```
POST /orders                    - Create new order 🔄
GET  /orders/{id}              - Get order details 🔄
GET  /orders                    - List user orders 🔄
PUT  /orders/{id}/cancel        - Cancel order 🔄
GET  /orders/{id}/status        - Get order status 🔄
GET  /health                    - Health check ✅
```

**Technology Stack**:
- **Framework**: FastAPI
- **Database**: DynamoDB (via common package)
- **Integration**: User service (balance validation)
- **Deployment**: Lambda/Kubernetes ready

### **3. Inventory Service** (`services/inventory_service/`) ✅ **PRODUCTION READY**

**Purpose**: Asset inventory management

**Key Features**:
- ✅ Public asset browsing (no auth required) ✅ **WORKING**
- ✅ Asset details and metadata ✅ **WORKING**
- ✅ Filtering and pagination ✅ **WORKING**
- ✅ Metrics collection ✅ **WORKING**
- ✅ Secure exception handling with AssetNotFoundException ✅ **COMPLETED**
- ✅ Data initialization on startup ✅ **WORKING**
- ✅ **98+ cryptocurrency assets** ✅ **WORKING**
- ✅ **Real-time price data** via CoinGecko API ✅ **WORKING**
- ✅ **AWS DynamoDB integration** ✅ **WORKING**
- ✅ **Fresh AWS credentials** ✅ **WORKING**

**API Endpoints** ✅ **ALL WORKING**:
```
GET  /inventory/assets           - List all assets (public) ✅
GET  /inventory/assets/{id}      - Get asset details (public) ✅
GET  /health                     - Health check ✅
GET  /metrics                    - Service metrics ✅
```

**Technology Stack**:
- **Framework**: FastAPI
- **Database**: DynamoDB (via common package) ✅ **WORKING**
- **External API**: CoinGecko integration ✅ **WORKING**
- **Metrics**: Custom metrics collection ✅ **WORKING**

### **4. Common Package** (`services/common/`) ✅ **PRODUCTION READY**

**Purpose**: Shared utilities, components, and order-balance integration

**Components**:
- **Database**: DynamoDB connection and DAOs ✅ **WORKING**
- **AWS**: STS client for role assumption ✅ **WORKING**
- **Entities**: Shared data models (User, Order, Balance, Inventory) ✅ **WORKING**
- **Health**: Redis health checks ✅ **WORKING**
- **Examples**: Usage examples and tests ✅ **WORKING**
- **Order-Balance Integration**: Balance validation and transaction management ✅ **WORKING**
- **Security Management**: PasswordManager, TokenManager, AuditLogger ✅ **COMPLETED**
- **Exception Handling**: Domain-specific exceptions for all DAOs ✅ **COMPLETED**

**Security Components** ✅ **COMPLETED**:
- **PasswordManager**: bcrypt-based password hashing and verification
- **TokenManager**: JWT token creation, verification, and management
- **AuditLogger**: Security event logging and audit trails
- **Service Integration**: All services using centralized security components

**Exception Handling** ✅ **COMPLETED**:
- **UserNotFoundException**: When user lookup returns None
- **BalanceNotFoundException**: When balance lookup returns None
- **TransactionNotFoundException**: When transaction lookup returns None
- **AssetNotFoundException**: When asset lookup returns None
- **OrderNotFoundException**: When order lookup returns None

## 🚀 Development Workflow

### **Current State** ✅ **ALL WORKING**
- ✅ User Service: JWT authentication implemented ✅ **PRODUCTION READY**
- ✅ Inventory Service: Public asset browsing implemented ✅ **PRODUCTION READY**
- ✅ Common Package: Shared utilities and database access ✅ **PRODUCTION READY**
- ✅ Testing: Comprehensive unit tests with coverage ✅ **WORKING**
- ✅ Deployment: Lambda and Kubernetes ready ✅ **WORKING**
- ✅ **API Gateway Integration**: ✅ **PRODUCTION READY**
- ✅ **AWS Credentials**: Fresh credentials deployed ✅ **WORKING**
- ✅ **Build Scripts**: Component-level build scripts ✅ **WORKING**
- ✅ **Security Manager Integration**: ✅ **COMPLETED**
- ✅ **Exception Handling Refactor**: ✅ **COMPLETED**
- ✅ **Balance Management**: ✅ **COMPLETED**
- ✅ **End-to-End Testing**: ✅ **COMPLETED**

### **Build Scripts** ✅ **WORKING**
```bash
# Build and test all services
./services/build.sh

# Build only
./services/build.sh --build-only

# Test only
./services/build.sh --test-only

# Verbose output
./services/build.sh -v
```

### **Completed Phases** ✅ **COMPLETED**
1. **✅ API Gateway Integration**: ✅ **COMPLETED**
   - ✅ Real proxy implementation
   - ✅ JWT validation middleware
   - ✅ Rate limiting with Redis (planned)
   - ✅ Service discovery

2. **✅ Security Manager Integration**: ✅ **COMPLETED**
   - ✅ PasswordManager implementation
   - ✅ TokenManager implementation
   - ✅ AuditLogger implementation
   - ✅ Service integration

3. **✅ Exception Handling Refactor**: ✅ **COMPLETED**
   - ✅ Domain-specific exceptions
   - ✅ Consistent error patterns
   - ✅ Proper error propagation
   - ✅ Comprehensive testing

4. **✅ Balance Management**: ✅ **COMPLETED**
   - ✅ Deposit/withdraw APIs
   - ✅ Transaction history
   - ✅ Atomic operations
   - ✅ Error handling

5. **✅ End-to-End Testing**: ✅ **COMPLETED**
   - ✅ All APIs verified working
   - ✅ Gateway integration tested
   - ✅ Error scenarios tested
   - ✅ Production readiness verified

### **Current Phase** 🔄 **IN PROGRESS**
- **🔄 Order Service Development**: 🔄 **IN PROGRESS**
   - 🔄 Order creation with balance validation
   - 🔄 Order execution and completion
   - 🔄 Order cancellation and refunds
   - 🔄 API endpoint implementation

### **Future Enhancements**
- **Limit Order Processing**: Advanced order types and hold mechanisms
- **Payment Integration**: External payment processing for deposits/withdrawals
- **Advanced Security**: OAuth2, API keys, audit logging
- **Performance**: Caching, connection pooling, load balancing
- **Monitoring**: Distributed tracing, advanced metrics

## 🛠️ Quick Start

### **Prerequisites**
- Python 3.8+
- Go 1.24+
- Redis (for rate limiting)
- AWS credentials (for DynamoDB) ✅ **CONFIGURED**

### **Local Development**

1. **Start User Service**:
```bash
cd services/user_service
python -m venv .venv-user_service
source .venv-user_service/bin/activate  # or .venv-user_service\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 8000
```

2. **Start Inventory Service**:
```bash
cd services/inventory_service
python -m venv .venv-inventory_service
source .venv-inventory_service/bin/activate
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 8001
```

3. **Start Order Service** (when implemented):
```bash
cd services/order_service
python -m venv .venv-order_service
source .venv-order_service/bin/activate
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 8002
```

4. **Start API Gateway**:
```bash
cd gateway
./gateway/build.sh --build-only
./gateway/dev.sh run
```

### **Using Build Scripts**

**All Services**:
```bash
# Build and test all services
./services/build.sh

# Test only
./services/build.sh --test-only
```

**Individual Services**:
```bash
# User Service
cd services/user_service
./build.sh

# Order Service
cd services/order_service
./build.sh

# Inventory Service
cd services/inventory_service
./build.sh
```

### **Testing**

**User Service**:
```bash
cd services/user_service
pytest tests/ -v --cov=src
```

**Order Service**:
```bash
cd services/order_service
pytest tests/ -v --cov=src
```

**Inventory Service**:
```bash
cd services/inventory_service
pytest tests/ -v --cov=src
```

**API Gateway**:
```bash
cd gateway
./gateway/build.sh --test-only
```

## 🔗 Service Integration ✅ **WORKING**

### **Authentication Flow** ✅ **WORKING**
```
1. Frontend → User Service: POST /auth/login
   Body: {"username": "user", "password": "pass"}

2. User Service → Frontend: JWT Token
   Response: {"access_token": "jwt_token", "token_type": "bearer"}

3. Frontend → Gateway: GET /api/v1/auth/me
   Headers: {"Authorization": "Bearer jwt_token"}

4. Gateway → User Service: Forward request with JWT validation
```

### **Public Access Flow** ✅ **WORKING**
```
1. Frontend → Gateway: GET /api/v1/inventory/assets
   (No Authorization header)

2. Gateway → Inventory Service: Forward request
   (No authentication required for public endpoints)
```

### **Balance Management Flow** ✅ **WORKING**
```
1. User → Gateway: POST /api/v1/auth/balance/deposit
   Headers: {"Authorization": "Bearer jwt_token"}
   Body: {"amount": 1000.00}

2. Gateway → User Service: Forward request with JWT validation

3. User Service → DynamoDB: Create transaction and update balance

4. User Service → User: Success response with transaction details
```

## 📊 Monitoring & Observability

### **Health Checks** ✅ **WORKING**
- **User Service**: `GET /health` ✅
- **Order Service**: `GET /health` ✅
- **Inventory Service**: `GET /health` ✅
- **API Gateway**: `GET /health` ✅

### **Metrics** ✅ **WORKING**
- **User Service**: Request/response metrics ✅
- **Order Service**: Order processing metrics 🔄 (when implemented)
- **Inventory Service**: Asset retrieval metrics ✅
- **API Gateway**: Rate limiting, proxy metrics ✅

### **Logging** ✅ **WORKING**
- **Structured Logging**: JSON format for all services ✅
- **Request Tracing**: Request ID correlation ✅
- **CloudWatch**: Lambda deployment ready ✅
- **Security Events**: Audit logging via AuditLogger ✅

## 🔧 Configuration

### **Environment Variables** ✅ **WORKING**
```bash
# Database
DYNAMODB_TABLE_PREFIX=dev_
DYNAMODB_REGION=us-east-1

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Redis (for rate limiting)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Service URLs
USER_SERVICE_URL=http://localhost:8000
INVENTORY_SERVICE_URL=http://localhost:8001

# AWS Credentials (Fresh) ✅ **WORKING**
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_ROLE_ARN=<your-role-arn>
```

## 🚀 Deployment ✅ **WORKING**

### **Local Development**
- Use `dev.sh` scripts for each service ✅
- Hot reload enabled for development ✅
- Local Redis for rate limiting ✅

### **Production** ✅ **WORKING**
- **Lambda**: Serverless deployment ready ✅
- **Kubernetes**: Container deployment ready ✅
- **Docker**: Container images available ✅
- **Terraform**: Infrastructure as Code ✅

### **Deployment Scripts** ✅ **WORKING**
```bash
# Deploy all services to Kubernetes
./scripts/deploy.sh --type k8s --environment dev

# Build and deploy specific service
./services/build.sh --build-only
kubectl apply -k kubernetes/dev/
```

## 📝 API Documentation

### **User Service**
- **Swagger UI**: `http://localhost:8000/docs` ✅
- **ReDoc**: `http://localhost:8000/redoc` ✅

### **Order Service**
- **Swagger UI**: `http://localhost:8002/docs` 🔄 (when implemented)
- **ReDoc**: `http://localhost:8002/redoc` 🔄 (when implemented)

### **Inventory Service**
- **Swagger UI**: `http://localhost:8001/docs` ✅
- **ReDoc**: `http://localhost:8001/redoc` ✅

### **API Gateway**
- **Health Check**: `http://localhost:8080/health` ✅
- **Proxy Endpoints**: Configured for service routing ✅

## 🧪 API Testing ✅ **COMPLETED**

### **✅ User Service APIs** ✅ **VERIFIED WORKING**
- **User Registration**: `POST /auth/register` ✅
- **User Login**: `POST /auth/login` ✅
- **User Profile**: `GET /auth/me` ✅
- **User Logout**: `POST /auth/logout` ✅
- **Get Balance**: `GET /balance` ✅
- **Deposit Funds**: `POST /balance/deposit` ✅
- **Withdraw Funds**: `POST /balance/withdraw` ✅
- **Transaction History**: `GET /balance/transactions` ✅
- **Insufficient Balance Error**: Proper error handling ✅

### **✅ Inventory Service APIs** ✅ **VERIFIED WORKING**
- **Get All Assets**: `GET /inventory/assets` (98+ assets) ✅
- **Get Specific Asset**: `GET /inventory/assets/BTC` ✅
- **Health Check**: `GET /health` ✅

### **✅ Gateway Routing** ✅ **VERIFIED WORKING**
- **User Service Routing**: `GET /api/v1/auth/me` ✅
- **Inventory Service Routing**: `GET /api/v1/inventory/assets` ✅
- **Health Check**: `GET /health` ✅

### **✅ Exception Handling** ✅ **VERIFIED WORKING**
- **Domain-Specific Exceptions**: All DAOs properly raise specific exceptions ✅
- **Error Propagation**: Consistent error handling across services ✅
- **Business Logic Validation**: Proper insufficient balance handling ✅

## 🤝 Contributing

1. **Code Style**: Follow PEP 8 (Python) and Go standards
2. **Testing**: Maintain >80% test coverage
3. **Documentation**: Update README and API docs
4. **Security**: Follow secure coding practices
5. **Exception Handling**: Use domain-specific exceptions
6. **Security Integration**: Use centralized security components

## 📞 Support

For questions or issues:
1. Check the service-specific README files
2. Review the API documentation
3. Check the test coverage reports
4. Review the deployment guides

## 🎯 Current Status Summary

### **✅ Production Ready Services**
- **User Service**: Complete authentication and balance system ✅ **PRODUCTION READY**
- **Inventory Service**: Public asset browsing with 98+ assets ✅ **PRODUCTION READY**
- **API Gateway**: JWT validation and proxying ✅ **PRODUCTION READY**
- **Common Package**: Shared utilities and security management ✅ **PRODUCTION READY**

### **🔄 In Development**
- **Order Service**: Order processing and balance integration 🔄 **IN DEVELOPMENT**

### **✅ Infrastructure & Deployment**
- **AWS Integration**: Fresh credentials working ✅
- **Deployment**: Kubernetes deployment working ✅
- **Docker**: All services containerized ✅

### **✅ Build and Test Automation**
- **Component Build Scripts**: All services have dedicated build scripts ✅
- **CI/CD Pipeline**: GitHub Actions working ✅
- **Local Testing**: Comprehensive test coverage ✅
- **End-to-End Testing**: All APIs verified working ✅

### **✅ Security and Authentication**
- **JWT Authentication**: Working end-to-end ✅
- **Public vs Protected Routes**: Properly configured ✅
- **Role-Based Access**: Implemented and working ✅
- **Centralized Security**: PasswordManager, TokenManager, AuditLogger ✅
- **Exception Handling**: Domain-specific exceptions ✅

### **✅ Recent Major Achievements**
- **Security Manager Integration**: Complete centralized security management ✅
- **Exception Handling Refactor**: Domain-specific exceptions for all DAOs ✅
- **Balance Management**: Complete deposit/withdraw functionality ✅
- **Transaction History**: Full transaction tracking and audit trail ✅
- **End-to-End Testing**: All APIs verified working in deployed environment ✅

---

**Core services are production-ready with comprehensive security, authentication, balance management, and end-to-end testing completed. Order Service is in active development with balance integration!** 🚀