# 🏗️ Services Architecture

> **Microservices platform** demonstrating enterprise patterns with security-first design

## 🎯 Overview

A comprehensive microservices platform showcasing production-ready patterns including centralized authentication, distributed locking, comprehensive monitoring, and enterprise security features.

## 🏗️ System Architecture

**High-Level Architecture:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Auth Service  │    │   Services      │
│   (React)       │◄──►│   (Go/Gin)      │◄──►│   (FastAPI)     │    │   (FastAPI)     │
│                 │    │   - Routing     │    │   - JWT Val.    │    │   - User Mgmt   │
│                 │    │   - Rate Limit  │    │   - User Ctx    │    │   - Order Mgmt  │
│                 │    │   - Circuit Br. │    │   - Security    │    │   - Inventory   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                                              │
                                │                                              │
                                ▼                                              │
                       ┌─────────────────┐                                    │
                       │   Request       │                                    │
                       │   Forwarding    │────────────────────────────────────┘
                       │   & Response    │
                       │   Handling      │
                       └─────────────────┘
```

## 🔄 Service Communication

**Request Flow:**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │    │   Frontend  │    │ API Gateway │    │Auth Service │
│             │    │             │    │             │    │             │
│ 1. Request  │───►│ 2. Send     │───►│ 3. Route    │───►│ 4. Validate │
│             │    │ Request     │    │ + Rate Limit│    │ JWT Token   │
│             │    │             │    │ + Circuit Br│    │ + User Ctx  │
│ 8. Response │◄───│ 7. Display  │◄───│ 6. Forward  │◄───│ 5. Extract  │
│             │    │ Response    │    │ Response    │    │ User Context│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                              │
                                                              ▼
                                                   ┌─────────────┐
                                                   │Backend      │
                                                   │ Services    │
                                                   │             │
                                                   │ 5. Process  │
                                                   │ Request     │
                                                   │             │
                                                   │ 6. Return   │
                                                   │ Response    │
                                                   └─────────────┘
```

**Order Processing Flow:**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │    │Order Service│    │Transaction  │    │   Database  │
│             │    │             │    │ Manager     │    │   (DynamoDB)│
│ 1. Create   │───►│ 2. Validate │───►│ 3. Acquire  │───►│ 4. Atomic   │
│ Order       │    │ Order Data  │    │ Lock        │    │ Operations  │
│             │    │             │    │             │    │             │
│ 5. Order    │◄───│ 6. Process  │◄───│ 7. Execute  │◄───│ 8. Update   │
│ Confirmed   │    │ Order       │    │ Transaction │    │ Balances    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 🔧 Service Responsibilities

### **Auth Service**
- **Responsibilities**:
  - Validates JWT tokens from incoming requests
  - Extracts user context
  - Provides authentication middleware for other services
  - Handles token expiration and refresh logic

### **User Service**
- **Responsibilities**:
  - User registration and authentication
  - Profile management and account operations
  - Balance management (deposits, withdrawals)
  - User data validation and security

### **Order Service**
- **Responsibilities**:
  - Order creation and processing
  - Portfolio management and calculations
  - Order lifecycle management
  - Trading operations coordination

### **Inventory Service**
- **Responsibilities**:
  - Asset catalog management
  - Market data integration
  - Asset information and pricing
  - Public asset browsing

### **Insights Service**
- **Responsibilities**:
  - AI-powered portfolio analysis and insights
  - Portfolio data aggregation from multiple services
  - LLM integration for generating actionable insights
  - Portfolio performance analysis and recommendations

### **API Gateway**
- **Responsibilities**:
  - Request routing and load balancing
  - Authentication and authorization
  - Rate limiting and circuit breaking
  - Security header management

## 🔐 Security Architecture

**Authentication:**
- JWT-based token authentication
- Centralized token validation through Auth Service
- Stateless authentication design

**Authorization:**
- JWT-required routes (authenticated vs public endpoints)
- Service-to-service authentication

**Security Features:**
- Rate limiting and throttling
- Circuit breaker patterns
- Input validation and sanitization
- Audit logging and security monitoring
- Distributed locking for atomic operations

## 🏗️ Data Architecture

**Database Design:**
- **DynamoDB** - Serverless NoSQL with single-table design
- **PynamoDB ORM** - Type-safe database operations
- **Redis** - Caching and session management
- **Atomic Operations** - Distributed locking and transaction support

**Data Models:**
- **User Entities** - Authentication, profiles, and account management
- **Order Entities** - Trading operations and order lifecycle
- **Asset Entities** - Inventory management and market data
- **Transaction Entities** - Audit trail and financial operations

## 🔄 Service Integration

**Inter-Service Communication:**
- **Synchronous**: HTTP/REST API calls between services
- **Authentication**: Centralized JWT validation through Auth Service
- **Data Consistency**: Distributed transactions with locking
- **Error Handling**: Consistent exception handling across services

**Shared Components:**
- **Common Package** - Shared utilities, data models, and security
- **Exception Handling** - Standardized error responses with RFC 7807
- **Structured Logging** - JSON logging with correlation IDs
- **Monitoring Integration** - Prometheus metrics and health checks

## 📊 Monitoring & Observability

**Monitoring Stack:**
- **Prometheus** - Metrics collection and storage
- **Grafana** - Visualization and dashboards
- **Loki** - Log aggregation and querying
- **AlertManager** - Intelligent alerting and notifications

**Metrics:** See [docs/METRICS.md](../docs/METRICS.md) for metric definitions and PromQL.

## 🛡️ Resilience Patterns

**Fault Tolerance:**
- Circuit breakers for service failure protection
- Retry logic for transient failures
- Timeout handling and graceful degradation
- Health checks and automatic recovery

**Data Consistency:**
- Distributed locking for atomic operations
- Transaction management with rollback support
- Event sourcing for audit trails
- Atomic database operations

## 🚀 Deployment Architecture

**Containerization:**
- **Docker** - From repo root: `./docker/deploy.sh local deploy` (local, no AWS) or `./docker/deploy.sh all deploy` / `./docker/deploy.sh <service> deploy` (dev/AWS). All services containerized.
- **Kubernetes** - Config retained; see [Kubernetes](../kubernetes/README.md) and [Deployment Guide](../docs/deployment-guide.md) for K8s deploy.

**AWS Integration:**
- **DynamoDB** - Serverless database with AWS integration
- **IAM Roles** - Service account permissions and role assumption
- **Security** - Secure credential management and access control

## 📚 Documentation

- **[Common Package](common/README.md)** - Shared components and utilities
- **[Docker](../docker/README.md)** - Docker Compose deploy (primary)
- **[Deployment Guide](../docs/deployment-guide.md)** - Docker, K8s, AWS
- **[Architecture](../docs/design-docs/)** - System design and patterns
- **[Metrics](../docs/METRICS.md)** - Application metrics (plan + PromQL)
- **[Security](../docs/design-docs/monitoring-design.md)** - Security monitoring and analytics
- **[Kubernetes](../kubernetes/README.md)** - K8s config (retained)
- **[Testing](../integration_tests/README.md)** - Testing strategy and implementation

## 📌 Status (Feb 2026)

- ✅ **Core Services** - All services operational (user, order, inventory, auth, insights, gateway)
- ✅ **Authentication** - JWT-based auth with centralized validation
- ✅ **Security** - Rate limiting, circuit breakers, audit logging
- ✅ **Monitoring** - Prometheus, Grafana, structured logging; see [METRICS.md](../docs/METRICS.md)
- ✅ **Database** - DynamoDB with PynamoDB ORM and distributed locking
- ✅ **Deployment** - Docker (local: `./docker/deploy.sh local deploy`; dev/AWS: `./docker/deploy.sh all deploy` or per-service); K8s deploy via [kubernetes/README.md](../kubernetes/README.md)
- 🔄 **Insights Service** - Backend complete; frontend integration optional/paused

---

**🔐 Enterprise-grade microservices platform demonstrating production-ready security, monitoring, and resilience patterns**

**🛡️ Built with**: Python, FastAPI, Go, DynamoDB, Prometheus, Grafana, Docker, Kubernetes, and modern security patterns