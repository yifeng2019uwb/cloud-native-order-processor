# Cloud-Native Order Processor - Services

## 🏗️ Architecture Overview

This project implements a **microservices architecture** with three main components:

1. **API Gateway** (Go/Gin) - Entry point, authentication, rate limiting
2. **User Service** (FastAPI) - Authentication, user management, JWT tokens
3. **Inventory Service** (FastAPI) - Asset management, public inventory data

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   User Service  │
│   (React)       │◄──►│   (Go/Gin)      │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Inventory       │
                       │ Service         │
                       │ (FastAPI)       │
                       └─────────────────┘
```

## 🔐 Security Model

### **Public Access (No Auth Required)**
- **Inventory Service**: Browse assets, view details
- **Health Checks**: Service status endpoints

### **Authenticated Access (JWT Required)**
- **User Service**: Login, registration, profile management
- **Inventory Service**: Order placement (future feature)
- **API Gateway**: All authenticated endpoints

### **JWT Flow**
```
1. User → User Service: POST /login (username/password)
2. User Service → User: JWT token
3. User → Gateway: Request with Authorization: Bearer <JWT>
4. Gateway → Backend Service: Forward request with JWT validation
```

## 📦 Services

### **1. User Service** (`services/user_service/`)

**Purpose**: User authentication and management

**Key Features**:
- ✅ JWT token generation and validation
- ✅ User registration and login
- ✅ Password authentication
- ✅ User profile management
- ✅ Secure exception handling
- ✅ CloudWatch logging (Lambda ready)

**API Endpoints**:
```
POST /login              - User authentication
POST /register           - User registration
GET  /profile            - Get user profile
PUT  /profile            - Update user profile
POST /logout             - User logout
GET  /health             - Health check
```

**Technology Stack**:
- **Framework**: FastAPI
- **Database**: DynamoDB (via common package)
- **Authentication**: JWT (PyJWT)
- **Deployment**: Lambda/Kubernetes ready

### **2. Inventory Service** (`services/inventory_service/`)

**Purpose**: Asset inventory management

**Key Features**:
- ✅ Public asset browsing (no auth required)
- ✅ Asset details and metadata
- ✅ Filtering and pagination
- ✅ Metrics collection
- ✅ Secure exception handling
- ✅ Data initialization on startup

**API Endpoints**:
```
GET  /inventory/assets           - List all assets (public)
GET  /inventory/assets/{id}      - Get asset details (public)
POST /inventory/orders           - Place order (authenticated - future)
GET  /health                     - Health check
GET  /metrics                    - Service metrics
```

**Technology Stack**:
- **Framework**: FastAPI
- **Database**: DynamoDB (via common package)
- **External API**: CoinGecko integration
- **Metrics**: Custom metrics collection

### **3. Common Package** (`services/common/`)

**Purpose**: Shared utilities and components

**Components**:
- **Database**: DynamoDB connection and DAOs
- **AWS**: STS client for role assumption
- **Entities**: Shared data models
- **Health**: Redis health checks
- **Examples**: Usage examples and tests

## 🚀 Development Workflow

### **Current State**
- ✅ User Service: JWT authentication implemented
- ✅ Inventory Service: Public asset browsing implemented
- ✅ Common Package: Shared utilities and database access
- ✅ Testing: Comprehensive unit tests with coverage
- ✅ Deployment: Lambda and Kubernetes ready

### **Next Phase (Tomorrow)**
1. **API Gateway Integration**:
   - Real proxy implementation
   - JWT validation middleware
   - Rate limiting with Redis
   - Service discovery

2. **End-to-End Testing**:
   - Gateway → User Service authentication
   - Gateway → Inventory Service proxying
   - Rate limiting validation
   - Error handling verification

### **Future Enhancements**
- **Order Processing**: Add order placement to inventory service
- **Payment Integration**: Payment processing for orders
- **Advanced Security**: OAuth2, API keys, audit logging
- **Performance**: Caching, connection pooling, load balancing
- **Monitoring**: Distributed tracing, advanced metrics

## 🛠️ Quick Start

### **Prerequisites**
- Python 3.8+
- Go 1.24+
- Redis (for rate limiting)
- AWS credentials (for DynamoDB)

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

3. **Start API Gateway**:
```bash
cd gateway
./dev.sh install
./dev.sh run
```

### **Testing**

**User Service**:
```bash
cd services/user_service
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
./dev.sh test
```

## 🔗 Service Integration

### **Authentication Flow**
```
1. Frontend → User Service: POST /login
   Body: {"username": "user", "password": "pass"}

2. User Service → Frontend: JWT Token
   Response: {"access_token": "jwt_token", "token_type": "bearer"}

3. Frontend → Gateway: GET /inventory/assets
   Headers: {"Authorization": "Bearer jwt_token"}

4. Gateway → Inventory Service: Forward request with JWT validation
```

### **Public Access Flow**
```
1. Frontend → Gateway: GET /inventory/assets
   (No Authorization header)

2. Gateway → Inventory Service: Forward request
   (No authentication required for public endpoints)
```

## 📊 Monitoring & Observability

### **Health Checks**
- **User Service**: `GET /health`
- **Inventory Service**: `GET /health`
- **API Gateway**: `GET /health`

### **Metrics**
- **User Service**: Request/response metrics
- **Inventory Service**: Asset retrieval metrics
- **API Gateway**: Rate limiting, proxy metrics

### **Logging**
- **Structured Logging**: JSON format for all services
- **Request Tracing**: Request ID correlation
- **CloudWatch**: Lambda deployment ready

## 🔧 Configuration

### **Environment Variables**
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
```

## 🚀 Deployment

### **Local Development**
- Use `dev.sh` scripts for each service
- Hot reload enabled for development
- Local Redis for rate limiting

### **Production**
- **Lambda**: Serverless deployment ready
- **Kubernetes**: Container deployment ready
- **Docker**: Container images available
- **Terraform**: Infrastructure as Code

## 📝 API Documentation

### **User Service**
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### **Inventory Service**
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

### **API Gateway**
- **Health Check**: `http://localhost:8080/health`
- **Proxy Endpoints**: Configured for service routing

## 🤝 Contributing

1. **Code Style**: Follow PEP 8 (Python) and Go standards
2. **Testing**: Maintain >80% test coverage
3. **Documentation**: Update README and API docs
4. **Security**: Follow secure coding practices

## 📞 Support

For questions or issues:
1. Check the service-specific README files
2. Review the API documentation
3. Check the test coverage reports
4. Review the deployment guides

---

**Next Steps**: Tomorrow we'll integrate the API Gateway with real JWT validation and Redis rate limiting! 🚀