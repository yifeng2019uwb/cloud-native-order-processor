# Order Processor Gateway

A Go-based API gateway that acts as a reverse proxy for the order processor microservices with comprehensive authentication, authorization, and security features.

## Architecture Overview

```
Client Request → Gateway → Backend Services
     ↓              ↓           ↓
   Frontend    Authentication  User Service
   Mobile      Rate Limiting   Inventory Service
   API Client  Authorization   (Future services)
```

## Project Structure

```
gateway/
├── cmd/gateway/main.go           # Application entry point
├── internal/
│   ├── api/server.go            # HTTP server and routing
│   ├── config/config.go         # Configuration management
│   ├── middleware/
│   │   ├── middleware.go        # Basic middleware (CORS, Logger, Recovery)
│   │   ├── auth.go              # Authentication middleware ✅ COMPLETED
│   │   └── rate_limit.go        # Rate limiting middleware (TODO)
│   └── services/
│       ├── redis.go             # Redis operations
│       └── proxy.go             # Proxy service ✅ COMPLETED
├── pkg/
│   ├── constants/constants.go   # Route configurations and roles
│   ├── models/request.go        # Request/response models
│   ├── models/response.go       # Response models
│   └── utils/                   # Utility functions
└── test/                        # Integration tests
```

## Design Principles

### 1. **Layered Architecture**
- **Presentation Layer**: HTTP handlers and middleware
- **Business Logic Layer**: Proxy services and caching
- **Data Layer**: Redis for session/rate limiting

### 2. **Separation of Concerns**
- Configuration management separate from business logic
- Middleware for cross-cutting concerns
- Service layer for backend communication

### 3. **Security-First Design**
- JWT authentication with role-based access control
- Public vs protected route handling
- Proper error handling and logging
- Graceful degradation when services are unavailable

## Request Flow

```
1. Client Request
   ↓
2. Gateway (Port 8080)
   ↓
3. Middleware Stack:
   ├── CORS ✅
   ├── Logger ✅
   ├── Authentication ✅ (JWT validation)
   ├── Role Authorization ✅ (Role-based access)
   └── Recovery ✅
   ↓
4. Route Handler
   ↓
5. Proxy Service ✅ (Request forwarding)
   ↓
6. Backend Service
   ↓
7. Response Transformation ✅
   ↓
8. Client Response
```

## API Endpoints

### Public Endpoints (No Auth Required)
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/inventory/assets` - List inventory assets (public)
- `GET /api/v1/inventory/assets/:id` - Get specific asset (public)

### Protected Endpoints (Auth Required)
- `GET /api/v1/auth/me` - Get user profile
- `POST /api/v1/auth/logout` - User logout

### System Endpoints
- `GET /health` - Health check

## Security Model

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

// Public inventory routes
APIV1InventoryAssets: {AllowedRoles: []string{}} // Empty = any role
```

### **Authentication Flow**
1. **No Authorization Header**: User gets `public` role
2. **Invalid JWT Token**: Request rejected with 401 error
3. **Valid JWT Token**: User gets role from token claims
4. **Role Check**: Gateway validates user role against route requirements

## Configuration

Environment variables with defaults:

```bash
# Server Configuration
GATEWAY_PORT=8080
GATEWAY_HOST=0.0.0.0

# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Redis Configuration (for future rate limiting)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_SSL=false

# Backend Services
USER_SERVICE_URL=http://user-service:8000
INVENTORY_SERVICE_URL=http://inventory-service:8001
```

## Implementation Status

### ✅ Completed
- [x] Basic project structure
- [x] Configuration management
- [x] HTTP server setup
- [x] Basic middleware (CORS, Logger, Recovery)
- [x] Health check endpoint
- [x] Route definitions
- [x] **JWT Authentication middleware** ✅
- [x] **Role-based authorization** ✅
- [x] **Proxy logic implementation** ✅
- [x] **Request/response transformation** ✅
- [x] **Public vs protected route handling** ✅
- [x] **Error handling improvements** ✅
- [x] **Unit tests with coverage** ✅
- [x] **Docker configuration** ✅
- [x] **Kubernetes deployment** ✅
- [x] **Build script** (`gateway/build.sh`) ✅

### 🔄 In Progress
- [ ] Rate limiting implementation (Redis-based)
- [ ] Response caching
- [ ] Circuit breaker pattern

### 📋 Future Enhancements
- [ ] **Redis Integration**: Session management and caching
- [ ] **Advanced Security**: Rate limiting and token blacklisting
- [ ] **Monitoring Setup**: Prometheus and Grafana integration
- [ ] **Distributed Tracing**: Request tracing across services
- [ ] **Load Testing**: Performance and scalability testing

## Development

### Prerequisites
- Go 1.24+
- Redis (optional, for future rate limiting)

### Quick Start
```bash
# Build and test
./gateway/build.sh

# Run locally
./gateway/build.sh --build-only
./gateway/dev.sh run

# Test only
./gateway/build.sh --test-only
```

### Testing
```bash
# Run all tests
go test ./...

# Run with coverage
go test ./... -cover

# Run specific test
go test ./internal/middleware -v
```

### Docker Build
```bash
# Build Docker image
docker build -f docker/gateway/Dockerfile -t order-processor-gateway:latest .

# Run in Docker
docker run -p 8080:8080 order-processor-gateway:latest
```

## Current Working Features

### **✅ Authentication & Authorization**
- JWT token validation
- Role-based access control
- Public route handling (no auth required)
- Protected route enforcement
- Proper error responses

### **✅ Request Proxying**
- Intelligent routing to backend services
- Request body preservation
- Response transformation
- Error handling and logging

### **✅ Security Features**
- CORS handling
- Input validation
- Secure error messages
- Request logging

### **✅ Deployment Ready**
- Docker containerization
- Kubernetes deployment
- Health checks
- Environment configuration

## API Examples

### **Public Access (No Auth)**
```bash
# Browse inventory (public)
curl http://localhost:8080/api/v1/inventory/assets

# Register user (public)
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123", "first_name": "Test", "last_name": "User"}'
```

### **Protected Access (Auth Required)**
```bash
# Login to get JWT token
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'

# Use JWT token for protected endpoints
curl -H "Authorization: Bearer <JWT_TOKEN>" \
  http://localhost:8080/api/v1/auth/me
```

## Evolution Strategy

### Phase 1: Core Gateway ✅ COMPLETED
- ✅ JWT authentication
- ✅ Role-based authorization
- ✅ Request proxying
- ✅ Error handling

### Phase 2: Performance & Resilience (Current)
- Rate limiting with Redis
- Response caching
- Circuit breaker pattern
- Retry logic

### Phase 3: Observability (Future)
- Metrics collection
- Distributed tracing
- Advanced logging
- Health monitoring

### Phase 4: Advanced Features (Future)
- API versioning
- Request/response transformation
- Advanced caching strategies
- Load balancing

## Design Decisions

1. **Gin Framework**: Chosen for performance and middleware support
2. **JWT Authentication**: Stateless token-based authentication
3. **Role-Based Access**: Flexible authorization system
4. **Public Routes**: Support for unauthenticated access
5. **Graceful Degradation**: Continue working without Redis
6. **Security First**: Proper error handling and validation

This gateway provides a robust, secure, and scalable entry point for the order processor microservices with comprehensive authentication and authorization capabilities.