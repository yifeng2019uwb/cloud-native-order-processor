# 🏗️ Cloud-Native Order Processor

> **Learning project** implementing **industry-standard microservices** with production-ready architecture and cost-conscious design

🏗️ **[Quick Start](#-quick-start)** | 📚 **[Documentation](docs/README.md)** | ☸️ **[Kubernetes](kubernetes/README.md)**

---

## 🎯 Project Overview

**Industry-standard microservices architecture** demonstrating cloud-native patterns:
- 🏗️ **Production-Ready Architecture**: Microservices, API Gateway, proper security
- 🔐 **Enterprise Security**: JWT, RBAC, audit logging, input validation
- ☸️ **Kubernetes Native**: Production manifests, local development
- 💰 **Cost-Conscious Design**: AWS optimization, efficient resource usage
- 🚀 **DevOps Automation**: Comprehensive testing, CI/CD, deployment

**Built for**: Learning modern development practices, portfolio demonstration, hands-on microservices experience

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

## 🐳 Docker Deployment

> **✅ Available** - Ready for local development and testing

**Quick Start with Docker:**
- **Single Command**: `./scripts/deploy-docker.sh -bd all`
- **Access Services**: Frontend (3000), Gateway (8080), Services (8000-8002)
- **Full Stack**: Complete system running in containers
- **Development Ready**: Hot reload, debugging, testing

**Docker Compose Status**: Production ready with health checks and proper networking

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
- **IAM**: Service roles and policies
- **Local Development**: Uses real AWS services with personal credentials

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

## 🎯 Learning Outcomes

### **Skills Demonstrated**
✅ **Microservices Design**: Service decomposition, API design, inter-service communication
✅ **Security Implementation**: Authentication, authorization, secure coding practices
✅ **Container Orchestration**: Docker, Kubernetes, service discovery
✅ **Infrastructure as Code**: Terraform modules, environment management
✅ **Testing Strategies**: Unit, integration, security testing
✅ **DevOps Automation**: Build scripts, deployment automation, CI/CD concepts

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

**📚 This project demonstrates learning modern cloud-native development practices**

**💡 Perfect for**: Understanding microservices, practicing DevOps, portfolio projects

**❓ Questions?** Check the [Documentation](docs/README.md) or open an issue

*Built as a hands-on learning experience with modern development practices*