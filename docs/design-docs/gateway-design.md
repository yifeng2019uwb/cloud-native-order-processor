# 🚪 API Gateway Design

## 🎯 **Problem Statement**

The system needs a centralized entry point that can:
- Route requests to appropriate backend microservices
- Provide unified authentication and authorization
- Handle security concerns (CORS, rate limiting, input validation)
- Provide a consistent API interface for frontend clients

## 🔍 **Options Considered**

### **Option A: Simple Reverse Proxy (Nginx/Traefik)**
- **Pros**: Simple, fast, battle-tested
- **Cons**: Limited business logic, no authentication, static configuration
- **Decision**: ❌ **Rejected** - Insufficient for complex authentication needs

### **Option B: API Gateway Framework (Kong, Tyk)**
- **Pros**: Feature-rich, enterprise-grade, plugins available
- **Cons**: Complex setup, resource overhead, learning curve
- **Decision**: ❌ **Rejected** - Overkill for current scale, adds complexity

### **Option C: Custom Go Gateway (Chosen)**
- **Pros**: Full control, lightweight, Go ecosystem integration, custom business logic
- **Cons**: More development time, custom implementation
- **Decision**: ✅ **Chosen** - Perfect balance of control and performance

## 🏗️ **Final Decision**

**Custom Go-based API Gateway using Gin framework**

### **Why This Approach?**
- **Performance**: Go's high-performance HTTP handling
- **Flexibility**: Custom authentication and routing logic
- **Integration**: Native Go ecosystem integration
- **Maintainability**: Full control over implementation
- **Scalability**: Lightweight and horizontally scalable

## 🔧 **Implementation Details**

### **Architecture Pattern**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Backend       │
│   (React)       │◄──►│   (Go/Gin)      │◄──►│   Services      │
│                 │    │   - Auth        │    │   - User        │
│                 │    │   - Proxy       │    │   - Inventory   │
│                 │    │   - Security    │    │   - Orders      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Core Components**
1. **HTTP Server**: Gin-based server with middleware stack
2. **Authentication**: JWT validation via Auth Service (centralized)
3. **Routing**: Intelligent request routing to backend services
4. **Proxy Service**: Request forwarding with circuit breaker protection
5. **Security**: ✅ CORS, ✅ Rate limiting, ✅ Security headers injection

### **Request Flow**
```
1. Client Request
   ↓
2. Gateway (Port 8080)
   ↓
3. Middleware Stack:
   ├── CORS ✅
   ├── Logger ✅
   ├── Recovery ✅
   ├── Authentication (JWT validation via Auth Service) ✅
   ├── Rate Limiting (Redis-based) ✅
   └── Role Authorization (Role-based access) ✅
   ↓
4. Route Handler
   ↓
5. Proxy Service (Request forwarding)
   ↓
6. Backend Service
   ↓
7. Response Transformation
   ↓
8. Client Response
```

## 🔐 **Security Design**

### **Authentication Strategy**
- **JWT Tokens**: Stateless token-based authentication
- **Token Validation**: ✅ **Centralized via Auth Service** (Phase 2 implementation)
  - Gateway delegates JWT validation to Auth Service
  - No JWT secret distribution (only Auth Service has secrets)
  - Token expiration and signature verification handled by Auth Service
- **Role Extraction**: User roles embedded in JWT claims, extracted by Auth Service

### **Authorization Model**
- **Role-Based Access Control (RBAC)**:
  - `public`: Unauthenticated users (no JWT token)
  - `customer`: Authenticated users with JWT token
  - `admin`: Administrative users (future)

### **Route Protection**
```go
// Public routes (no auth required)
APIV1AuthLogin:    {AllowedRoles: []string{"public"}}
APIV1AuthRegister: {AllowedRoles: []string{"public"}}

// Protected routes (any authenticated user)
APIV1AuthMe:       {AllowedRoles: []string{}} // Empty = any role
APIV1AuthLogout:   {AllowedRoles: []string{}} // Empty = any role
```

### **Security Middleware Stack**
Gateway implements a middleware stack that processes requests in order:
1. **CORS Middleware** - Handles cross-origin requests (single entry point)
2. **Logger Middleware** - Request logging and correlation
3. **Recovery Middleware** - Panic recovery and error handling
4. **Auth Middleware** - JWT validation via Auth Service (centralized)
5. **Rate Limiting Middleware** - Redis-based request throttling (1000 req/min per IP)

### **Security Headers Injection**
Gateway injects security headers into requests forwarded to backend services:
- `X-Source: gateway` - Identifies request source
- `X-Auth-Service: auth-service` - Indicates Auth Service validation
- `X-User-ID` - User identifier from JWT
- `X-User-Role` - User role from JWT
- `X-Authenticated: true/false` - Authentication status
- `X-Request-ID` - Request correlation ID for tracing

**Purpose**: Backend services can validate request source and receive user context without handling JWT tokens.

### **Secret Management**
**Architecture Design**:
- Gateway does not store or manage JWT secrets
- Gateway delegates all JWT validation to Auth Service via HTTP call
- Gateway only requires `AuthService` URL for validation, not secrets
- Auth Service manages its own JWT secret independently

**Design Rationale**:
- Eliminates JWT secret distribution (only Auth Service needs the secret)
- Reduces attack surface and simplifies secret management
- Centralizes token validation logic

## 🚀 **Routing Strategy**

### **Service Mapping**
- **User Service**: `/api/v1/auth/*` endpoints
- **Inventory Service**: `/api/v1/inventory/*` endpoints
- **Order Service**: `/api/v1/orders/*`, `/api/v1/assets/*`, `/api/v1/portfolio/*` endpoints

### **Dynamic Route Handling**
- **Pattern Matching**: Intelligent route pattern recognition
- **Parameter Extraction**: Dynamic path parameter handling
- **Service Discovery**: Automatic routing to correct backend service

## 📊 **Performance Considerations**

### **Optimizations**
- **Middleware Efficiency**: Minimal overhead in request processing
- **Connection Pooling**: Reuse backend connections
- **Response Caching**: Future Redis-based response caching
- **Load Balancing**: Ready for horizontal scaling

### **Scalability**
- **Horizontal Scaling**: Stateless design supports multiple instances
- **Resource Management**: Efficient memory and CPU usage
- **Connection Limits**: Configurable connection pooling

## 🧪 **Testing Strategy**

### **Unit Tests**
- **Middleware Testing**: Authentication and authorization logic
- **Routing Testing**: Route matching and service discovery
- **Proxy Testing**: Request forwarding and transformation

### **Integration Tests**
- **End-to-End Testing**: Complete request flow validation
- **Backend Integration**: Service communication testing
- **Error Scenarios**: Failure handling and recovery


## 🔮 **Future Enhancements**

### **Phase 2: Performance & Resilience** ✅ **Mostly Complete**
- ✅ **Rate Limiting**: Redis-based request throttling
- ✅ **Circuit Breaker**: Backend service failure handling
- ⚪ **Response Caching**: Intelligent response caching (future)
- ⚪ **Retry Logic**: Automatic retry for failed requests (future)

### **Phase 3: Observability** ✅ **Complete**
- ✅ **Metrics Collection**: Prometheus integration
- ✅ **Structured Logging**: JSON logging with correlation IDs
- ✅ **Health Monitoring**: Health check endpoints
- ⚪ **Distributed Tracing**: Request tracing across services (future)

### **Phase 4: Advanced Features**
- **API Versioning**: Multi-version API support
- **Request Transformation**: Advanced request/response modification
- **Advanced Caching**: Multi-layer caching strategies
- **Load Balancing**: Intelligent traffic distribution

## 📝 **Design Decisions Log**

| Date | Component | Decision | Why | Impact | Status |
|------|-----------|----------|-----|---------|---------|
| 8/17 | Framework | Gin over Echo | Better middleware support | Medium | ✅ Done |
| 8/17 | Auth | JWT over Sessions | Stateless, scalable | High | ✅ Done |
| 8/17 | Routing | Custom proxy over library | Full control over logic | Medium | ✅ Done |
| 8/17 | Security | RBAC over ABAC | Simpler, sufficient for current needs | Low | ✅ Done |
| - | Auth | Auth Service Integration | Centralized JWT validation | High | ✅ Done |
| - | Security | Gateway CORS only | Single entry point architecture | Medium | ✅ Done |

## 🔗 **Related Documentation**

- **[System Architecture](./system-architecture.md)**: Overall system design
- **[Technology Stack](./technology-stack.md)**: Technology choices and rationale
- **[Gateway README](../gateway/README.md)**: Implementation and usage guide

---

**🎯 This gateway design provides a robust, secure, and scalable entry point for the order processor microservices with comprehensive authentication and authorization capabilities.**
