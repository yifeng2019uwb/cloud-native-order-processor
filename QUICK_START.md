# 🚀 Quick Start Guide - Cloud Native Order Processor

## 🎯 What is this?
**📊 Current Status: PRODUCTION READY** ✅

**Last Updated: 8/17/2025**
- ✅ **All Backend Issues Resolved**: Gateway routing, parameter mismatches, redundant endpoints
- ✅ **All APIs Working Perfectly**: No 500 errors, all endpoints responding correctly
- ✅ **System Status**: Production-ready with comprehensive testing
- ✅ **Ready for Development**: Backend is stable, can focus on new features

A **multi-asset trading platform** built with microservices architecture, featuring:
- **Security-first design** with JWT authentication, RBAC, and audit logging
- **Multi-asset portfolio management** with real-time balance tracking
- **Cloud-native architecture** using AWS DynamoDB, Redis, and Kubernetes
- **Production-ready quality** with 96%+ test coverage

## 🛠️ Tech Stack
- **Backend**: Python FastAPI, Go API Gateway
- **Database**: AWS DynamoDB (3 tables: Users, Orders, Assets)
- **Caching**: Redis for sessions and token blacklist
- **Containerization**: Docker (Kubernetes in development)
- **Security**: JWT, RBAC, encryption, audit logging
- **Testing**: pytest, integration tests, chaos engineering

## ⚡ Quick Start (5 minutes)

### Prerequisites
```bash
# Required tools
- Python 3.11+
- Go 1.24+
- Docker & Docker Compose
- AWS CLI (configured)
# kubectl (for local K8s) - Coming soon!

# Note: Build scripts automatically handle:
# - Virtual environment creation
# - Dependency installation
# - Package setup
```

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/cloud-native-order-processor
cd cloud-native-order-processor

# That's it! Build scripts handle all dependencies automatically
```

### 2. Local Development
```bash
# Start all services (recommended)
./scripts/test-local.sh --environment dev --dev-cycle

# Or start components individually
./scripts/test-local.sh --frontend
./scripts/test-local.sh --gateway
./scripts/test-local.sh --services

# Services will be available at:
# - Frontend: http://localhost:3000
# - Gateway: http://localhost:8080
# - User Service: http://localhost:8000
# - Order Service: http://localhost:8001
# - Inventory Service: http://localhost:8002
```

### 3. Test the API
```bash
# Health check
curl http://localhost:8080/health

# Register user
curl -X POST http://localhost:8080/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "securepass123"}'

# Login
curl -X POST http://localhost:8080/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "securepass123"}'
```

### 4. Run Tests
```bash
# Run all tests (recommended)
./scripts/test-local.sh --environment dev --all

# Run component tests
./scripts/test-local.sh --frontend
./scripts/test-local.sh --gateway
./scripts/test-local.sh --services

# Run individual service tests
cd services
./build.sh                    # Test all services
./build.sh common             # Test common package only
./build.sh order_service      # Test order service only
./build.sh user_service       # Test user service only
./build.sh --test-only common # Test only (skip build)
./build.sh -v order_service   # Verbose output

# Run gateway tests
cd gateway
./build.sh

# Run frontend tests
cd frontend
./build.sh

# Run integration tests
./scripts/test-integration.sh --environment dev

# Run smoke tests
./scripts/smoke-test.sh
```

## 🏗️ Architecture Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │   Gateway   │    │   Services  │
│  (React)    │◄──►│    (Go)     │◄──►│  (FastAPI)  │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                                         ┌─────────────┐    ┌─────────────┐
                     │    Redis    │    │  DynamoDB   │
                     │  (Sessions) │    │ (3 Tables:  │
                     └─────────────┘    │Users,Orders,│
                                        │   Assets)   │
                                        └─────────────┘
```

## 🔐 Security Features

- **JWT Authentication** with token blacklist
- **Role-Based Access Control** (RBAC)
- **Audit logging** for all operations
- **Input validation** and sanitization
- **Encryption** at rest and in transit
- **Rate limiting** and request validation

## 📊 Key Features

### Multi-Asset Portfolio Management
```python
# Get user's portfolio
GET /api/v1/orders/portfolio/{username}

# Response includes:
{
  "total_value": "125000.00",
  "assets": [
    {
      "asset_id": "AAPL",
      "quantity": "100.0",
      "current_price": "150.00",
      "total_value": "15000.00"
    }
  ]
}
```

### Real-time Balance Tracking
```python
# Atomic balance updates
POST /api/v1/orders/buy
{
  "username": "user123",
  "asset_id": "AAPL",
  "quantity": "10",
  "price": "150.00"
}
```

## 🧪 Testing Strategy

- **Unit Tests**: 96%+ coverage across all services
- **Integration Tests**: End-to-end API testing
- **Performance Tests**: Load testing with realistic scenarios
- **Security Tests**: Penetration testing and vulnerability scanning
- **Chaos Engineering**: Failure injection and recovery testing

### **Comprehensive Scripts**
Professional-grade scripts that handle everything automatically:

- **`test-local.sh`** - Full CI/CD pipeline mirror (build → deploy → test → destroy)
- **`test-integration.sh`** - End-to-end integration testing
- **`smoke-test.sh`** - Quick health checks
- **`deploy.sh`** - Universal deployment (infrastructure, services, K8s)
- **`cli-client.sh`** - API testing client

### **Individual Component Scripts**
Each component has its own build script for granular control:

- **`services/build.sh`** - Python services (creates venv, installs deps, runs tests)
- **`gateway/build.sh`** - Go gateway (installs deps, builds, tests)
- **`frontend/build.sh`** - React app (installs deps, builds, tests)

## 🚀 Deployment

### Local Development (Current)
```bash
# Start all services
./scripts/test-local.sh --environment dev --dev-cycle

# Deploy infrastructure and services
./scripts/deploy.sh --type k8s --environment dev
```

### Kubernetes Deployment (Coming Soon)
```bash
# Full production deployment - In development
# ./scripts/deploy.sh --type k8s --environment prod

# Local Kubernetes setup - In development
# kind create cluster --config kubernetes/kind-config.yaml
# kubectl apply -k kubernetes/dev/
```

## 📈 Performance & Scalability

- **DynamoDB**: Auto-scaling, pay-per-use
- **Redis**: In-memory caching for sessions
- **Docker**: Containerized services for easy deployment
- **API Gateway**: Rate limiting and load balancing
- **Kubernetes**: Horizontal pod autoscaling (Coming Soon)

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Write tests** for your changes
4. **Run the test suite**: `python -m pytest`
5. **Submit a pull request**

### Development Guidelines
- Maintain 90%+ test coverage
- Follow the existing code style
- Add documentation for new features
- Include integration tests for API changes
- Use the provided scripts for testing and deployment

## 📚 Documentation

- **Architecture**: `docs/architecture.md`
- **API Documentation**: Available at `/docs` when services are running
- **Database Design**: `services/common/docs/DATABASE_DESIGN.md`
- **Planning**: `services/order_service/PLANNING.md`

## 🎯 What Makes This Special?

### Security-First Design
- Every component built with security in mind
- Comprehensive audit logging
- Token blacklist for secure logout
- Input validation and sanitization

### Production-Ready Quality
- 96%+ test coverage
- Comprehensive error handling
- Performance monitoring
- Chaos engineering practices

### Cost-Optimized Architecture
- DynamoDB 3-table design for cost efficiency and data separation
- Serverless-first approach
- Optimized for personal project scale
- Pay-per-use pricing model

## 🔗 Quick Links

- **GitHub**: [Repository Link]
- **Live Demo**: [Demo URL]
- **API Docs**: [Swagger UI]
- **Architecture**: [Architecture Docs]

---

**Ready to explore?** Clone the repo and run `./scripts/test-local.sh --environment dev --dev-cycle` to see it in action! 🚀

*Questions? Open an issue or reach out on LinkedIn!*