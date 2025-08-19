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
2. **Authentication**: JWT validation and role-based access control
3. **Routing**: Intelligent request routing to backend services
4. **Proxy Service**: Request forwarding and response transformation
5. **Security**: CORS, input validation, rate limiting (planned)

### **Request Flow**
```
1. Client Request
   ↓
2. Gateway (Port 8080)
   ↓
3. Middleware Stack:
   ├── CORS
   ├── Logger
   ├── Authentication (JWT validation)
   ├── Role Authorization (Role-based access)
   └── Recovery
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
- **Token Validation**: Signature verification and expiration checking
- **Role Extraction**: User roles embedded in JWT claims

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

### **Phase 2: Performance & Resilience**
- **Rate Limiting**: Redis-based request throttling
- **Response Caching**: Intelligent response caching
- **Circuit Breaker**: Backend service failure handling
- **Retry Logic**: Automatic retry for failed requests

### **Phase 3: Observability**
- **Metrics Collection**: Prometheus integration
- **Distributed Tracing**: Request tracing across services
- **Advanced Logging**: Structured logging and correlation
- **Health Monitoring**: Comprehensive health checks

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

## 🔗 **Related Documentation**

- **[System Architecture](./system-architecture.md)**: Overall system design
- **[Technology Stack](./technology-stack.md)**: Technology choices and rationale
- **[Gateway README](../gateway/README.md)**: Implementation and usage guide

---

**🎯 This gateway design provides a robust, secure, and scalable entry point for the order processor microservices with comprehensive authentication and authorization capabilities.**
