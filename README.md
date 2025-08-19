# 🔐 Cloud-Native Order Processor

> **Security-first microservices platform** demonstrating enterprise authentication, authorization, and secure architecture patterns

🔐 **[Security Architecture](#-security-architecture)** | 🏗️ **[Quick Start](#-quick-start)** | ☸️ **[Kubernetes](kubernetes/README.md)**

---

## 🎯 Security-Focused Learning Project

**Comprehensive security implementation across all layers**:
- 🔐 **Authentication & Authorization**: JWT + RBAC with centralized security management
- 🛡️ **API Gateway Security**: Request validation, rate limiting, secure routing
- 🔒 **Input Validation**: Comprehensive Pydantic validation with domain exceptions
- 📊 **Audit Logging**: Security event tracking across all microservices
- 🚪 **Secure Communication**: TLS, secure headers, CORS policies
- 🏗️ **Infrastructure Security**: Kubernetes security policies, secrets management

**Perfect for**: Security engineering learning, secure coding practices, enterprise security patterns

## 🏗️ System Architecture

**Generic microservices pattern** applicable to any domain:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Services      │
│   (React)       │◄──►│   (Go/Gin)      │◄──►│   (FastAPI)     │
│                 │    │   - Auth        │    │   - User Mgmt   │
│                 │    │   - Proxy       │    │   - Business    │
│                 │    │   - Security    │    │   - Data        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Infrastructure│
                       │   - DynamoDB    │
                       │   - Redis       │
                       │   - Kubernetes  │
                       └─────────────────┘
```

**Key Patterns Demonstrated:**
- **Service Discovery**: API Gateway routing
- **Data Consistency**: Distributed transactions
- **Security**: Centralized authentication
- **Scalability**: Stateless services + database

## 🔐 Security Architecture

### **Current Security Implementation**

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Security      │  │   Security      │  │   Security      │
│   Layers        │  │   Components    │  │   Patterns      │
│                 │  │                 │  │                 │
│ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │
│ │API Gateway  │ │  │ │JWT + bcrypt │ │  │ │Defense in   │ │
│ │Security     │ │  │ │Centralized  │ │  │ │Depth        │ │
│ │Rate Limiting│ │  │ │Auth Mgmt    │ │  │ │Zero Trust   │ │
│ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │
│                 │  │                 │  │                 │
│ ┌─────────────┐ │  │ ┌─────────────┐ │  │                 │
│ │Service      │ │  │ │RBAC +       │ │  │                 │
│ │Security     │ │  │ │Input        │ │  │                 │
│ │Validation   │ │  │ │Validation   │ │  │                 │
│ └─────────────┘ │  │ └─────────────┘ │  │                 │
│                 │  │                 │  │                 │
│ ┌─────────────┐ │  │ ┌─────────────┐ │  │                 │
│ │Data         │ │  │ │Audit        │ │  │                 │
│ │Security     │ │  │ │Logging +    │ │  │                 │
│ │Encryption   │ │  │ │Compliance   │ │  │                 │
│ └─────────────┘ │  │ └─────────────┘ │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### **Security Components Implemented**

| **Security Layer** | **Implementation** | **Status** | **Enterprise Ready** |
|-------------------|-------------------|------------|---------------------|
| **Authentication** | JWT with bcrypt, secure token mgmt | ✅ Complete | Ready for OAuth2/OIDC |
| **Authorization** | RBAC with centralized policies | ✅ Complete | Ready for ABAC/OPA |
| **Input Validation** | Pydantic models + domain exceptions | ✅ Complete | Ready for WAF integration |
| **Audit Logging** | Comprehensive security event tracking | ✅ Complete | Ready for SIEM integration |
| **API Security** | Gateway-level protection + rate limiting | ✅ Complete | Ready for advanced threats |
| **Secrets Management** | Environment-based configuration | ✅ Complete | Ready for Vault/K8s secrets |
| **Network Security** | Service isolation + secure communication | ✅ Complete | Ready for service mesh |

## 🛠️ Technology Choices

| **Component** | **Technology** | **Why Chosen** | **Production Ready** |
|---------------|----------------|----------------|----------------------|
| **Frontend** | React 18 + TypeScript | Modern frontend with type safety | ✅ |
| **Gateway** | Go + Gin | Performance and simplicity | ✅ |
| **Services** | Python + FastAPI | Rapid development, great docs | ✅ |
| **Database** | DynamoDB | Serverless, cost-effective | ✅ |
| **Cache** | Redis | Session management, distributed locks | ✅ |
| **Container** | Docker + Kubernetes | Industry standard orchestration | ✅ |
| **Monitoring** | Prometheus + Grafana | Cloud-native observability | 🔄 |

## 📊 Service Overview

| **Service** | **Purpose** | **Status** | **Key Features** |
|-------------|-------------|------------|------------------|
| **User Service** | Authentication & User Management | ✅ Production | JWT, RBAC, balance management |
| **Order Service** | Business Logic & Transactions | ✅ Production | Portfolio, trading operations |
| **Inventory Service** | Asset Management & Data | ✅ Production | Real-time pricing, public access |
| **API Gateway** | Routing & Security | ✅ Production | Authentication, rate limiting |
| **Frontend** | User Interface | ✅ Production | React dashboard, responsive design |

## 🚀 Quick Start

### **Prerequisites**
- Docker and Docker Compose
- Kubernetes (Kind for local development)
- AWS CLI configured
- Node.js 18+ and Python 3.11+

### **Deployment Options**

| **Environment** | **Method** | **Use Case** | **Complexity** | **Commands** |
|-----------------|------------|--------------|----------------|--------------|
| **Local Dev** | Docker Compose | Quick start, development | Low | `./scripts/deploy-docker.sh -bd all` |
| **Local K8s** | Kind cluster | Learning, realistic | Medium | `kind create cluster` + `./scripts/deploy.sh --type k8s --environment dev` |
| **Production** | EKS + AWS | Production deployment | High | `./scripts/deploy.sh --type k8s --environment prod` |

### **Start Everything Locally**
```bash
# Clone the repository
git clone https://github.com/yifeng2019uwb/cloud-native-order-processor
cd cloud-native-order-processor

# Option 1: Docker Compose (Simplest)
./scripts/deploy-docker.sh -bd all

# Option 2: Local Kubernetes (More realistic)
kind create cluster --config kubernetes/kind-config.yaml
./scripts/deploy.sh --type k8s --environment dev
```

### **Verify Everything Works**
```bash
# Check all services are healthy
curl http://localhost:8080/health
curl http://localhost:8000/health  # User Service
curl http://localhost:8001/health  # Inventory Service
curl http://localhost:8002/health  # Order Service

# Access the application
# Frontend: http://localhost:3000
# Gateway: http://localhost:8080
```

## 🎮 Live Demo

> **🚧 In Progress** - Working on public deployment

**What you'll be able to see:**
- **Frontend Interface**: Modern React dashboard
- **API Documentation**: Interactive Swagger/OpenAPI docs
- **Service Health**: Real-time system status
- **Performance Metrics**: Response times, throughput

**Demo Link**: Coming soon

**Current Status**: Local development complete, working on public deployment

## 🐳 Docker Deployment

> **✅ Available** - Ready for local development and testing

**Quick Start with Docker:**
- **Single Command**: `./scripts/deploy-docker.sh -bd all`
- **Access Services**: Frontend (3000), Gateway (8080), Services (8000-8002)
- **Full Stack**: Complete system running in containers
- **Development Ready**: Hot reload, debugging, testing

**Docker Compose Status**: Production ready with health checks and proper networking

## 🚀 Quick Security Demo

### **Authentication Flow**
```bash
# 1. Clone and setup
git clone https://github.com/yifeng2019uwb/cloud-native-order-processor
cd cloud-native-order-processor
./scripts/deploy-docker.sh -bd all

# 2. Test authentication security
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "SecurePass123!"}'

# 3. Verify JWT security
curl -X GET http://localhost:8080/api/v1/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. Test authorization (should get 401/403)
curl -X GET http://localhost:8080/api/v1/orders \
  -H "Authorization: Bearer invalid_token"
```

### **Security Validation**
```bash
# Test input validation
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "x", "password": "weak"}'
# Returns: 422 with detailed validation errors

# Test SQL injection protection
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin'\''--", "password": "anything"}'
# Safely handled by parameterized queries
```

## 🔐 Security Implementation

### **What's Implemented**
- **Authentication**: JWT tokens with bcrypt password hashing
- **Authorization**: Role-based access control (public, customer, admin)
- **Input Validation**: Pydantic models with comprehensive validation
- **Audit Logging**: Security events tracked across all services
- **Secrets Management**: Environment-based configuration

### **Security Testing**
```bash
# Run security-focused tests
cd services && ./build.sh --test-only
```

## ☸️ Kubernetes Learning

### **Local Kubernetes Setup**
```bash
# Create local cluster
kind create cluster --name order-processor

# Deploy with our defined script
./scripts/deploy.sh --type k8s --environment dev

# Check deployment
kubectl get pods -n order-processor
kubectl get services -n order-processor

# Port forward to access services
kubectl port-forward svc/frontend 3000:80 -n order-processor
kubectl port-forward svc/gateway 8080:8080 -n order-processor
```

### **Kubernetes Concepts Demonstrated**
- **Deployments**: Multi-replica service deployments
- **Services**: ClusterIP, NodePort, LoadBalancer patterns
- **ConfigMaps/Secrets**: Configuration management
- **Namespaces**: Environment isolation
- **Kustomize**: Environment-specific configurations

## 📊 Observability (Work in Progress)

### **Monitoring Stack**
```bash
# Deploy monitoring to Kubernetes
kubectl create namespace monitoring
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring

# Access Grafana
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
# Default: admin/prom-operator
```

### **Current Monitoring**
- ✅ **Health Checks**: All services expose `/health` endpoints
- ✅ **Structured Logging**: JSON logs with correlation IDs
- ✅ **Basic Metrics**: Response times, error rates
- 🔄 **Dashboards**: Grafana dashboards in development
- 📋 **Alerting**: AlertManager configuration planned

## 🔧 Development Workflow

### **Component Development**
```bash
# Build and test individual components
./frontend/build.sh          # Frontend: npm ci, build, test
./gateway/build.sh           # Gateway: go build, test
./services/build.sh          # Services: venv, pip install, pytest

# Full development cycle
./scripts/test-local.sh --environment dev --dev-cycle
```

### **Integration Testing**
```bash
# Comprehensive integration tests
cd integration_tests
./run_all_tests.sh all      # All services
./run_all_tests.sh user     # User service only
./run_all_tests.sh smoke    # Health checks only
```

## 💰 AWS Integration

### **Current AWS Usage**
- **DynamoDB**: User data, orders, assets (pay-per-use)
- **IAM**: Service roles and policies with assume role for production
- **Local Development**: Uses real AWS services with personal credentials
- **Production Security**: Kubernetes service accounts with IAM assume role

### **Cost Considerations**

| **Service** | **Current Choice** | **Alternative** | **Cost Impact** | **Why This Choice** |
|-------------|-------------------|-----------------|-----------------|---------------------|
| **Database** | DynamoDB (pay-per-use) | RDS PostgreSQL | $5-10/month vs $20-50/month | Serverless, no server management |
| **Kubernetes** | Local Kind cluster | AWS EKS | $0 vs $75/month | Learning without cloud costs |
| **Compute** | Local Docker | AWS Lambda | $0 vs $0.20/million requests | Full control, no cold starts |
| **Storage** | DynamoDB single-table | Multiple tables | $5-10/month vs $15-30/month | Efficient design, minimal RCU/WCU |

### **AWS Setup**
```bash
# Configure AWS credentials
aws configure
aws sts get-caller-identity

# Deploy infrastructure with our script
./scripts/deploy.sh --type infra --environment dev

# Or manually with Terraform
cd terraform
terraform init
terraform apply -var="environment=dev"
```

### **Production IAM Assume Role (Kubernetes)**

**Secure AWS Access Pattern for Production Deployments:**

Our Terraform configuration automatically sets up IAM assume role for Kubernetes service accounts, providing:

**Security Benefits:**
- 🔐 **No Hardcoded Credentials**: Services use temporary AWS credentials
- 🛡️ **Principle of Least Privilege**: Only necessary DynamoDB permissions
- 🔄 **Automatic Rotation**: Credentials automatically refreshed
- 🏗️ **Production Ready**: Enterprise-grade AWS access pattern

**Deployment:**
```bash
# Deploy with IAM assume role configured
./scripts/deploy.sh --type infra --environment prod
kubectl apply -f kubernetes/deployment.yaml
```

## 📚 Documentation Structure

### **Learning Documentation**
- **[Architecture Decisions](docs/design-docs/)** - Why I chose each technology
- **[Build Process](services/build.md)** - How the build automation works
- **[Integration Tests](integration_tests/README.md)** - API testing approach
- **[Kubernetes Setup](kubernetes/README.md)** - Container orchestration learning

### **Implementation Guides**
- **[Local Development](docs/deployment-guide.md)** - Getting started locally
- **[Security Implementation](docs/design-docs/security-architecture.md)** - Security patterns used
- **[Testing Strategy](docs/testing/)** - Testing approach and coverage

## 🎯 Security Learning Outcomes

### **Enterprise Security Patterns Demonstrated**
✅ **Defense in Depth**: Multiple security layers from gateway to database
✅ **Centralized Security**: Reusable security components across microservices
✅ **Secure by Design**: Security built into architecture, not bolted on
✅ **Zero Trust Principles**: Every request authenticated and authorized
✅ **Audit & Compliance**: Comprehensive security event logging
✅ **Secure Communication**: TLS, secure headers, input validation

### **Ready for Enterprise Security Integration**
✅ **SIEM Integration**: Structured audit logs ready for security operations
✅ **Identity Providers**: JWT architecture ready for OAuth2/OIDC
✅ **Policy Engines**: Authorization system ready for OPA integration
✅ **Service Mesh**: Microservice communication ready for mTLS
✅ **Secrets Management**: Configuration ready for enterprise vaults
✅ **Threat Detection**: Monitoring stack ready for security analytics

### **Technologies Learned**
- **Backend**: Python FastAPI, Go web services, DynamoDB patterns
- **Frontend**: React with TypeScript, modern build tools
- **Infrastructure**: Kubernetes, Docker, Terraform
- **Observability**: Prometheus, Grafana, structured logging
- **Security**: JWT, RBAC, secure configuration management

## ⚠️ Current Limitations

**This is a learning project, so:**
- 🏠 **Local Focus**: Primarily designed for local development
- 💰 **Cost Conscious**: Avoids expensive AWS services like EKS
- 🔄 **Work in Progress**: Some features like advanced monitoring are still being implemented
- 📚 **Learning Priority**: Code quality and learning over production optimization

## 🚀 Getting Started

1. **Quick Demo**: Follow the [Quick Start](#-quick-start)
2. **Understand the Code**: Read the [Architecture Decisions](docs/design-docs/)
3. **Explore Components**: Check individual [Component READMEs](services/README.md)
4. **Try Kubernetes**: Follow the [Kubernetes Guide](kubernetes/README.md)

---

**🔐 This project demonstrates comprehensive security architecture suitable for enterprise environments**

**🛡️ Perfect for**: Security engineering roles, secure development practices, enterprise architecture

**🔒 Questions about security implementation?** Check the [Security Documentation](docs/design-docs/) or open an issue

*Built with security-first principles and enterprise-ready patterns*