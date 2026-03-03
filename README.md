# 🔐 Cloud-Native Order Processor

> **Enterprise microservices platform** demonstrating production-ready security, monitoring, and resilience patterns

## 🎯 What is CNOP?

A production-ready microservices platform implementing enterprise cloud-native patterns with a security-first approach.

**Key Features:**
- 🔐 **Enterprise Security** - JWT authentication, rate limiting, IP blocking, circuit breakers
- 🏗️ **Microservices Architecture** - 7 services (user, order, inventory, auth, insights, gateway, frontend)
- 📊 **Comprehensive Monitoring** - Prometheus, Grafana, structured logging
- 🛡️ **Resilience Patterns** - Circuit breakers, retry logic, distributed locking
- 🐳 **Deployment** - Docker Compose for local/AWS; Kubernetes config available

## 🎬 Watch the Demo

**[▶ Watch on YouTube](https://www.youtube.com/watch?v=TNaPIE2jDG0)** — Video walkthrough of the Cloud-Native Order Processor platform.

## 🏗️ High-Level System Overview

**Architecture:**
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

| **Service** | **Purpose** | **Port** | **Security Features** | **Status** |
|-------------|-------------|----------|----------------------|------------|
| **Frontend** | User Interface | 3000 | JWT token management | ✅ Ready |
| **API Gateway** | Routing & Security | 8080 | Rate limiting, circuit breakers, CORS, **IP block (brute-force)** | ✅ Ready |
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
- **IP Block (SEC-011)** - Brute-force protection (5 failed logins → IP blocked); see [integration tests](integration_tests/incident/README.md)
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
- **STRIDE Threat Model** - Documented mitigations and test coverage; see [Threat Model](docs/security/THREAT_MODEL.md)
- **Attack Simulation** - OWASP ZAP baseline scan (65 PASS, 0 FAIL); see [ZAP Scan report](docker/zap-report.html)

## 📊 Monitoring & Observability

**Stack:** Prometheus (metrics), Grafana (dashboards), Loki (logs), Promtail (log collection). For metric definitions and PromQL, see [docs/METRICS.md](docs/METRICS.md).

## 🛡️ Resilience Patterns

**Fault Tolerance:**
- **Circuit Breakers** - Prevent cascade failures between services
- **Retry Logic** - Automatic retry for transient failures
- **Timeout Handling** - Request timeout and graceful degradation
- **Health Checks** - Service health monitoring and automatic recovery

**Data Consistency:**
- **Distributed Locking** - User-level locks for atomic operations (Redis-based)
- **Transaction Management** - Database transaction coordination
- **Audit Logging** - Comprehensive audit trail for security and compliance

## 🏗️ Data Architecture

- **DynamoDB** - Serverless NoSQL with single-table design (PynamoDB ORM)
- **Redis** - Caching, rate limiting, distributed locking

## 🔄 Service Integration

- **HTTP/REST** - Synchronous communication via API Gateway
- **Centralized Auth** - JWT validation through Auth Service
- **Shared Components** - Common package, exception handling (RFC 7807), structured logging

## 🐳 Deployment

- **Docker Compose** - Primary deployment method (local & AWS); see [Getting Started](#-getting-started)
- **Kubernetes** - Config available for K8s/EKS; see [kubernetes/README.md](kubernetes/README.md)

## 📚 Documentation

- **[Services](services/README.md)** | **[Docker](docker/README.md)** | **[Kubernetes](kubernetes/README.md)** | **[Deployment Guide](docs/deployment-guide.md)**
- **[Architecture](docs/design-docs/)** | **[Security](docs/design-docs/monitoring-design.md)** | **[Metrics](docs/METRICS.md)** | **[Testing](integration_tests/README.md)**

## 📌 Project Status (Feb 2026)

- ✅ **Core Services** - All 7 services operational
- ✅ **Security** - JWT auth, rate limiting, IP blocking, circuit breakers, STRIDE threat model, OWASP ZAP scan (65 PASS, 0 FAIL)
- ✅ **Monitoring** - Prometheus, Grafana, structured logging; see [METRICS.md](docs/METRICS.md)
- ✅ **Database** - DynamoDB (PynamoDB ORM) + Redis
- ✅ **Deployment** - Docker Compose (primary); Kubernetes config available
- ✅ **Documentation** - All READMEs synchronized (Feb 2026)

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

- Review [Services Overview](services/README.md) for architecture details
- Check [Deployment Guide](docs/deployment-guide.md) for development setup
- Run integration tests: `./integration_tests/run_all_tests.sh`

---

**🔐 Enterprise-grade microservices platform demonstrating production-ready security, monitoring, and resilience patterns**

**🛡️ Built with**: Python, FastAPI, Go, DynamoDB, Redis, Prometheus, Grafana, Loki, Docker (K8s config retained), and modern security patterns

**🔒 Questions?** Check the documentation or open an issue