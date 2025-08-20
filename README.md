# 🔐 Cloud-Native Order Processor

> **Personal project exploring enterprise security patterns in microservices** - JWT + RBAC, IAM role assumption, and defense-in-depth architecture

🔐 **[Security Architecture](#-security-architecture)** | 🚀 **[Quick Start](#-quick-start)** | ☸️ **[Kubernetes](kubernetes/README.md)**

---

## 🎯 Security-Focused Learning Project

**Exploring enterprise security patterns in microservices**:
- 🔐 **JWT + RBAC**: Centralized authentication and role-based access control
- 🛡️ **IAM Role Assumption**: Secure AWS access without hardcoded credentials
- 🔒 **Defense-in-Depth**: Multiple security layers from gateway to database
- 📊 **Security Monitoring**: Audit logging and compliance tracking

**Built for**: Learning enterprise security practices, portfolio demonstration

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

**Modern security patterns in microservices:**
- 🔐 **Authentication & Authorization**: JWT + RBAC with centralized security
- 🏗️ **Infrastructure Security**: Kubernetes + AWS IAM role assumption
- 🛡️ **API Security**: Gateway-level validation and protection
- 📊 **Security Monitoring**: Audit logging and compliance tracking

**Perfect for**: Learning secure development, portfolio demonstration, security engineering practice

## 🛠️ System Overview

| **Component** | **Technology** | **Purpose** | **Status** | **Deployment** |
|---------------|----------------|-------------|------------|----------------|
| **Frontend** | React 18 + TypeScript | User Interface | ✅ Production | Docker, K8s |
| **API Gateway** | Go + Gin | Routing & Security | ✅ Production | Docker, K8s |
| **User Service** | Python + FastAPI | Authentication & RBAC | ✅ Production | Docker, K8s |
| **Order Service** | Python + FastAPI | Business Logic | ✅ Production | Docker, K8s |
| **Inventory Service** | Python + FastAPI | Asset Management | ✅ Production | Docker, K8s |
| **Database** | DynamoDB | Data Storage | ✅ Production | AWS |
| **Cache** | Redis | Session Management | ✅ Production | Docker, K8s |
| **Container** | Docker + K8s | Orchestration | ✅ Production | Local/Cloud |
| **Monitoring** | Prometheus + Grafana | Observability | 🔄 In Progress | K8s |

**Deployment**: Docker Compose (local dev) | Kind cluster (local K8s) | EKS (production)

## 🚀 Quick Start

### **Prerequisites**
- Docker and Docker Compose
- Kubernetes (Kind for local development)
- AWS CLI configured
- Node.js 18+ and Python 3.11+

### **Start Everything Locally**

**Quick commands:**
```bash
# Clone and start with Docker
git clone https://github.com/yifeng2019uwb/cloud-native-order-processor
cd cloud-native-order-processor
./scripts/deploy-docker.sh -bd all
```

**For detailed setup and verification, see:**
- **[Local Development Guide](docs/deployment-guide.md)** - Complete setup instructions
- **[Kubernetes Setup](kubernetes/README.md)** - Local K8s deployment
- **[Service Health Checks](docs/deployment-guide.md#verification)** - How to verify everything works

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

**Test the security implementation:**
```bash
# Start the system
./scripts/deploy-docker.sh -bd all

# Test authentication and authorization
curl http://localhost:8080/health
```

**For comprehensive security testing, see:**
- **[Security Testing Guide](docs/design-docs/security-architecture.md)** - Complete security validation
- **[API Testing](integration_tests/README.md)** - Authentication and authorization tests
- **[Security Patterns](docs/design-docs/)** - Detailed security implementation

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

**For detailed development workflow, see:**
- **[Development Guide](docs/deployment-guide.md)** - Complete development workflow
- **[Build Process](services/build.md)** - Build automation details
- **[Testing Strategy](integration_tests/README.md)** - Testing approach and commands

## 💰 AWS Integration

**AWS services used:**
- **DynamoDB**: User data, orders, assets
- **IAM**: Service roles with assume role for production
- **Infrastructure**: Terraform-managed with IAM role assumption

**For detailed setup, see:**
- **[AWS Configuration](docs/deployment-guide.md)** - Complete setup guide
- **[Terraform Infrastructure](terraform/README.md)** - Infrastructure details

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

**Security engineering skills demonstrated:**
- 🔐 **Enterprise Security**: JWT, RBAC, IAM role assumption, defense-in-depth
- 🏗️ **Microservices Security**: Secure inter-service communication and validation
- 🛡️ **Infrastructure Security**: Kubernetes policies and AWS security patterns
- 📊 **Security Monitoring**: Audit logging and compliance tracking

**For detailed learning outcomes, see:**
- **[Security Documentation](docs/design-docs/)** - Complete security patterns
- **[Architecture Decisions](docs/design-docs/)** - Technology choices and rationale

## ⚠️ Current Limitations

**This is a learning project, so:**
- 🏠 **Local Focus**: Primarily designed for local development
- 💰 **Cost Conscious**: Avoids expensive AWS services like EKS
- 🔄 **Work in Progress**: Some features like advanced monitoring are still being implemented
- 📚 **Learning Priority**: Code quality and learning over production optimization

## 🚀 Getting Started

1. **Quick Demo**: Follow the [Quick Start](#-quick-start) above
2. **Detailed Setup**: [Local Development Guide](docs/deployment-guide.md)
3. **Security Implementation**: [Security Documentation](docs/design-docs/)
4. **Kubernetes Setup**: [Kubernetes Guide](kubernetes/README.md)
5. **API Testing**: [Integration Tests](integration_tests/README.md)

---

**🔐 This project demonstrates comprehensive security architecture suitable for enterprise environments**

**🛡️ Perfect for**: Security engineering roles, secure development practices, enterprise architecture

**🔒 Questions about security implementation?** Check the [Security Documentation](docs/design-docs/) or open an issue

*Built with security-first principles and enterprise-ready patterns*