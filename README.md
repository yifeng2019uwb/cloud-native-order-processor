# 🔐 Cloud-Native Order Processor

> **Enterprise microservices platform** demonstrating production-ready security, monitoring, and resilience patterns

## 🎯 What is CNOP?

A comprehensive, production-ready microservices platform that demonstrates modern cloud-native architecture patterns with a **security-first approach**. Built for learning enterprise patterns while showcasing real-world trading platform capabilities.

**Key Features:**
- 🔐 **Enterprise Security** - JWT authentication, rate limiting, circuit breakers
- 🏗️ **Microservices Architecture** - 6 independent services with clear responsibilities
- 📊 **Comprehensive Monitoring** - Prometheus, Grafana, structured logging, security analytics
- 🛡️ **Resilience Patterns** - Circuit breakers, retry logic, distributed locking
- ☸️ **Production Deployment** - Kubernetes, Docker, AWS integration

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

## 🏗️ System Overview

| **Service** | **Purpose** | **Port** | **Security Features** | **Status** |
|-------------|-------------|----------|----------------------|------------|
| **Frontend** | User Interface | 3000 | JWT token management | ✅ Ready |
| **API Gateway** | Routing & Security | 8080 | Rate limiting, circuit breakers, CORS | ✅ Ready |
| **Auth Service** | JWT Validation | 8003 | Token validation, user context, security analytics | ✅ Ready |
| **User Service** | User Management | 8000 | Password hashing, audit logging | ✅ Ready |
| **Order Service** | Order Processing | 8002 | Distributed locking, atomic transactions | ✅ Ready |
| **Inventory Service** | Asset Management | 8001 | Public access, input validation | ✅ Ready |
| **Insights Service** | AI Portfolio Analysis | 8004 | Google Gemini LLM, in-memory caching | ✅ Ready |
| **Redis** | Cache & Coordination | Internal | Rate limiting, distributed locking, caching | ✅ Ready |

## 🔐 Security Architecture

**Enterprise Security Features:**
- **JWT Authentication** - Centralized token validation with Auth Service
- **Rate Limiting** - Per-IP and per-user request throttling
- **Circuit Breakers** - Service failure protection and resilience
- **Input Validation** - Comprehensive request validation and sanitization
- **Audit Logging** - Security event tracking and compliance
- **Distributed Locking** - Atomic operations across services
- **Security Headers** - CORS, security headers, and source validation

**Security Monitoring:**
- **Authentication Analytics** - Login patterns and failure analysis
- **Authorization Tracking** - Auth failures and token validation events
- **Rate Limit Monitoring** - Throttling events and abuse detection
- **Circuit Breaker States** - Service health and failure patterns
- **Security Event Correlation** - Cross-service security event tracking
- **OWASP ZAP** - Baseline vulnerability scan; see [OWASP ZAP Security Scan](docs/OWASP_ZAP_SCAN.md) for how to run and interpret results

## 📊 Monitoring & Observability

**Comprehensive Monitoring Stack:**
- **Prometheus** - Metrics collection and storage (port 9090)
- **Grafana** - Visualization and dashboards for metrics and logs (port 3001)
- **Loki** - Log aggregation and querying (port 3100)
- **Promtail** - Log collection agent (collects from Docker containers)

**Monitoring Categories:**
- **Security Monitoring** - Authentication, authorization, and security events
- **Gateway Monitoring** - Routing, rate limiting, and circuit breaker states
- **Service Performance** - Response times, error rates, and throughput
- **Business Intelligence** - Trading operations and user analytics
- **Infrastructure Health** - Kubernetes, AWS, and resource monitoring

**Key Metrics:**
- **Security KPIs** - Authentication success rate, security violations, audit compliance
- **Performance KPIs** - Response time percentiles, error rates, service availability
- **Business KPIs** - Order success rate, user activity, trading volume
- **Gateway KPIs** - Routing success rate, auth service integration, circuit breaker stability

## 🛡️ Resilience Patterns

**Fault Tolerance:**
- **Circuit Breakers** - Prevent cascade failures between services
- **Retry Logic** - Automatic retry for transient failures
- **Timeout Handling** - Request timeout and graceful degradation
- **Health Checks** - Service health monitoring and automatic recovery

**Data Consistency:**
- **Distributed Locking** - User-level locks for atomic operations (Redis-based)
- **Transaction Management** - Database transaction coordination
- **Atomic Operations** - Database operations with rollback support
- **Audit Logging** - Comprehensive audit trail for security and compliance

## 🏗️ Data Architecture

**Database Design:**
- **DynamoDB** - Serverless NoSQL with single-table design
- **PynamoDB ORM** - Type-safe database operations
- **Redis** - Caching, rate limiting, distributed locking, and session management
- **Atomic Operations** - Database operations with rollback support

**Data Models:**
- **User Entities** - Authentication, profiles, and account management
- **Order Entities** - Trading operations and order lifecycle
- **Asset Entities** - Inventory management and market data
- **Transaction Entities** - Audit trail and financial operations

## 🔄 Service Integration

**Inter-Service Communication:**
- **Synchronous HTTP/REST** - Direct API calls between services via API Gateway
- **Centralized Authentication** - JWT validation through Auth Service
- **API Gateway Routing** - Single entry point for all service requests
- **Redis-based Coordination** - Shared state for distributed locking and caching
- **Error Handling** - Consistent exception handling and error responses

**Shared Components:**
- **Common Package** - Shared utilities, data models, and security
- **Exception Handling** - Standardized error responses with RFC 7807
- **Structured Logging** - JSON logging with correlation IDs
- **Monitoring Integration** - Prometheus metrics and health checks

## 📚 Documentation

- **[Services Overview](services/README.md)** - Service architecture and development
- **[Insights Setup](docker/SETUP_INSIGHTS.md)** - AI insights service setup and end-to-end flow
- **[Common Package](services/common/README.md)** - Shared components and utilities
- **[Architecture](docs/design-docs/)** - System design and patterns
- **[Security](docs/design-docs/monitoring-design.md)** - Security monitoring and analytics
- **[OWASP ZAP Security Scan](docs/OWASP_ZAP_SCAN.md)** - How to run ZAP baseline scan and interpret the report
- **[Kubernetes](kubernetes/README.md)** - Container orchestration
- **[Testing](integration_tests/README.md)** - Testing strategy and implementation

## 🎯 Use Cases

**Perfect for:**
- Learning enterprise microservices architecture
- Understanding security-first design patterns
- JWT authentication implementation
- Monitoring and observability in production
- Resilience patterns and fault tolerance
- Kubernetes deployment and scaling

## ⚠️ Current Status

- ✅ **Core Services** - All 6 services operational (user, order, inventory, auth, insights, gateway)
- ✅ **Authentication** - JWT-based auth with centralized validation
- ✅ **Security** - Rate limiting, circuit breakers, audit logging
- ✅ **Monitoring** - Prometheus, Grafana, structured logging
- ✅ **Database** - DynamoDB with PynamoDB ORM and distributed locking
- ✅ **Deployment** - Docker, Kubernetes, and AWS integration

## 🚀 Getting Started

### Run Locally (one command, no AWS account needed)

```bash
./docker/deploy.sh local deploy
```

To stop and remove the local stack:

```bash
./docker/deploy.sh local destroy
```

**Prerequisites**: Docker and Docker Compose only. You do **not** need Python, Go, or AWS CLI—all services and table creation run inside Docker.

- **Frontend**: http://localhost:3000
- **Gateway API**: http://localhost:8080
- Uses LocalStack for DynamoDB (no AWS account or credentials required)

See [Docker README](docker/README.md) for more options (AWS deploy, stop, logs).

### Next Steps

1. **Architecture**: Review [Services Overview](services/README.md) for service architecture
2. **Security**: Check [Security Monitoring](docs/design-docs/monitoring-design.md) for security patterns
3. **Development**: Follow [Local Development Guide](docs/deployment-guide.md) for detailed setup
4. **Testing**: Use [Integration Tests](integration_tests/README.md) for testing (run `./integration_tests/run_all_tests.sh` for full suite)

---

**🔐 Enterprise-grade microservices platform demonstrating production-ready security, monitoring, and resilience patterns**

**🛡️ Built with**: Python, FastAPI, Go, DynamoDB, Redis, Prometheus, Grafana, Loki, Docker, Kubernetes, and modern security patterns

**🔒 Questions?** Check the documentation or open an issue