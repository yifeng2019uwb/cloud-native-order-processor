# Order Processor Gateway

A Go-based API gateway that acts as a reverse proxy for the order processor microservices.

## Architecture Overview

```
Client Request → Gateway → Backend Services
     ↓              ↓           ↓
   Frontend    Rate Limiting   User Service
   Mobile      Authentication  Inventory Service
   API Client  Caching         (Future services)
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
│   │   ├── auth.go              # Authentication middleware (TODO)
│   │   └── rate_limit.go        # Rate limiting middleware (TODO)
│   └── services/
│       ├── redis.go             # Redis operations
│       └── proxy.go             # Proxy service (TODO)
├── pkg/
│   ├── models/request.go        # Request/response models
│   └── utils/response.go        # Response utilities
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

### 3. **Fail-Safe Design**
- Graceful degradation when Redis is unavailable
- Circuit breaker pattern for backend services
- Proper error handling and logging

## Request Flow

```
1. Client Request
   ↓
2. Gateway (Port 8080)
   ↓
3. Middleware Stack:
   ├── CORS
   ├── Logger
   ├── Rate Limiting (Redis) ← TODO
   ├── Authentication ← TODO
   └── Recovery
   ↓
4. Route Handler
   ↓
5. Proxy Service ← TODO
   ↓
6. Backend Service
   ↓
7. Response Transformation ← TODO
   ↓
8. Client Response
```

## API Endpoints

### Public Endpoints (No Auth Required)
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

### Protected Endpoints (Auth Required) ← TODO
- `GET /api/v1/auth/profile` - Get user profile
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/inventory/assets` - List inventory assets
- `GET /api/v1/inventory/assets/:id` - Get specific asset

### System Endpoints
- `GET /health` - Health check

## Configuration

Environment variables with defaults:

```bash
# Server Configuration
GATEWAY_PORT=8080
GATEWAY_HOST=0.0.0.0

# Redis Configuration
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
- [x] Redis service structure
- [x] Proxy service structure

### 🔄 In Progress
- [ ] Rate limiting implementation
- [ ] Authentication middleware
- [ ] Proxy logic implementation
- [ ] Response caching
- [ ] Circuit breaker pattern

### 📋 TODO
- [ ] JWT token validation
- [ ] Session management
- [ ] Request/response transformation
- [ ] Error handling improvements
- [ ] Metrics and monitoring
- [ ] Integration tests
- [ ] Docker configuration
- [ ] Kubernetes deployment

## Development

### Prerequisites
- Go 1.24+
- Redis (optional, for full functionality)

### Running Locally
```bash
cd gateway
go mod tidy
go run cmd/gateway/main.go
```

### Testing
```bash
go test ./...
```

## Evolution Strategy

### Phase 1: Basic Proxy (Current)
- Simple request forwarding
- Basic health checks
- Configuration management

### Phase 2: Security & Performance
- Authentication middleware
- Rate limiting
- Response caching

### Phase 3: Resilience
- Circuit breaker pattern
- Retry logic
- Advanced error handling

### Phase 4: Observability
- Metrics collection
- Distributed tracing
- Advanced logging

## Design Decisions

1. **Gin Framework**: Chosen for performance and middleware support
2. **Redis**: For session management and rate limiting
3. **Layered Architecture**: For maintainability and testability
4. **Graceful Degradation**: Continue working without Redis
5. **TODO Comments**: Clear markers for future implementation

This design allows for incremental development while maintaining a clear path for evolution and scaling.