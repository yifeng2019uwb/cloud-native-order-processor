# 🚪 API Gateway

> High-performance Go-based API gateway with JWT authentication, role-based authorization, and intelligent request routing to backend microservices

## 🚀 Quick Start

### Prerequisites
- Go 1.24+
- Redis (optional, for future rate limiting)

### Build & Test
```bash
# Build and test
./build.sh

# Build only
./build.sh --build-only

# Test only
./build.sh --test-only

# Run locally
./dev.sh run
```

### Docker Deployment
```bash
# Build and run
docker build -f docker/gateway/Dockerfile -t order-processor-gateway:latest .
docker run -p 8080:8080 order-processor-gateway:latest
```

## ✨ Key Features

- **JWT Authentication**: Secure token-based authentication with role extraction
- **Role-Based Access Control**: Flexible authorization for public, customer, and admin roles
- **Intelligent Routing**: Automatic request routing to appropriate backend services
- **Security First**: CORS, input validation, and secure error handling
- **Production Ready**: Comprehensive testing and deployment configurations

## 🔗 Quick Links

- [Design Documentation](../docs/design-docs/gateway-design.md)
- [API Endpoints](#api-endpoints)
- [Security Model](#security-model)
- [Deployment Guide](#deployment)

## 📊 Status

- **Current Status**: ✅ **PRODUCTION READY** - All core features implemented and tested
- **Last Updated**: August 20, 2025
- **Backend Integration**: ✅ All routing issues resolved, all endpoints working

## 🎯 Current Status

### ✅ **All Systems Working Perfectly**
- **Authentication**: JWT validation and role-based access control
- **Routing**: All endpoints properly routed to backend services
- **Security**: CORS, input validation, and secure error handling
- **Performance**: Fast request processing and response transformation
- **Testing**: Comprehensive unit and integration test coverage

### 🚀 **Ready for Production**
- **No Known Issues**: All functionality tested and working
- **Comprehensive Security**: Authentication, authorization, and input validation
- **Scalable Architecture**: Stateless design supports horizontal scaling
- **Monitoring Ready**: Health checks and comprehensive logging

---

## 📁 Project Structure

```
gateway/
├── cmd/gateway/main.go           # Application entry point
├── internal/
│   ├── api/server.go            # HTTP server and routing
│   ├── config/config.go         # Configuration management
│   ├── middleware/
│   │   ├── middleware.go        # Basic middleware (CORS, Logger, Recovery)
│   │   ├── auth.go              # Authentication middleware
│   │   └── rate_limit.go        # Rate limiting middleware (planned)
│   └── services/
│       ├── redis.go             # Redis operations
│       └── proxy.go             # Proxy service
├── pkg/
│   ├── constants/constants.go   # Route configurations and roles
│   ├── models/request.go        # Request/response models
│   └── models/response.go       # Response models
└── test/                        # Integration tests
```

## 🛠️ Technology Stack

- **Go 1.24+**: High-performance programming language
- **Gin Framework**: Fast HTTP web framework with middleware support
- **JWT**: JSON Web Token authentication
- **Redis**: Session management and rate limiting (planned)

## 🔐 Security Model

### **Role-Based Access Control**
- **`public`**: Unauthenticated users (no JWT token)
- **`customer`**: Authenticated users with JWT token
- **`admin`**: Administrative users (future)

### **Route Configuration**
```go
// Public routes (no auth required)
APIV1AuthLogin:    {AllowedRoles: []string{"public"}}
APIV1AuthRegister: {AllowedRoles: []string{"public"}}

// Protected routes (any authenticated user)
APIV1AuthMe:       {AllowedRoles: []string{}} // Empty = any role
APIV1AuthLogout:   {AllowedRoles: []string{}} // Empty = any role
```

## 🔗 API Endpoints

### **Public Endpoints (No Auth Required)**
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/inventory/assets` - List inventory assets
- `GET /api/v1/inventory/assets/:id` - Get specific asset

### **Protected Endpoints (Auth Required)**
- `GET /api/v1/auth/profile` - Get user profile
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/orders` - List user orders
- `POST /api/v1/orders` - Create order
- `GET /api/v1/portfolio/:username` - Get portfolio
- `GET /api/v1/assets/balances` - Get asset balances

### **System Endpoints**
- `GET /health` - Health check

## 🚀 Deployment

### **Kubernetes Deployment**
```bash
# Deploy to Kubernetes
kubectl apply -k kubernetes/dev/

# Port forward for access
kubectl port-forward svc/gateway 30000:8080 -n order-processor
```

### **Environment Configuration**
```bash
# Server Configuration
GATEWAY_PORT=8080
GATEWAY_HOST=0.0.0.0

# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Backend Services
USER_SERVICE_URL=http://user-service:8000
INVENTORY_SERVICE_URL=http://inventory-service:8001
ORDER_SERVICE_URL=http://order-service:8002
```

## 🧪 Testing

```bash
# Run all tests
go test ./...

# Run with coverage
go test ./... -cover

# Run specific test
go test ./internal/middleware -v
```

## 📈 Performance

- **Fast Request Processing**: Minimal middleware overhead
- **Efficient Routing**: Intelligent route pattern matching
- **Connection Pooling**: Backend connection reuse
- **Horizontal Scaling**: Stateless design supports multiple instances

## 🔮 Future Enhancements

### **Phase 2: Performance & Resilience**
- **Rate Limiting**: Redis-based request throttling
- **Response Caching**: Intelligent response caching
- **Circuit Breaker**: Backend service failure handling

### **Phase 3: Observability**
- **Metrics Collection**: Prometheus integration
- **Distributed Tracing**: Request tracing across services
- **Advanced Logging**: Structured logging and correlation

---

**🎯 This gateway provides a robust, secure, and scalable entry point for the order processor microservices with comprehensive authentication and authorization capabilities.**