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

**New centralized authentication architecture** with dedicated Auth Service:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Auth Service  │    │   Services      │
│   (React)       │◄──►│   (Go/Gin)      │◄──►│   (Python)     │    │   (FastAPI)     │
│                 │    │   - Routing     │    │   - JWT Val.    │    │   - User Mgmt   │
│                 │    │   - Proxy       │    │   - User Ctx    │    │   - Business    │
│                 │    │   - Security    │    │   - Security    │    │   - Data        │
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

**Key Patterns Demonstrated:**
- **Service Discovery**: API Gateway routing with Auth Service integration
- **Data Consistency**: Distributed transactions with atomic operations
- **Security**: Centralized authentication via dedicated Auth Service
- **Scalability**: Stateless services + independent Auth Service scaling
- **Network Security**: Backend services isolated from external access

## 🔐 Security Architecture

**New centralized authentication architecture with enhanced security:**
- 🔐 **Dedicated Auth Service**: JWT validation and user context extraction
- 🏗️ **Gateway Security**: Pure routing with security header injection
- 🛡️ **Network Security**: Kubernetes NetworkPolicies and IP whitelisting
- 📊 **Security Monitoring**: Essential authentication metrics and alerts
- 🔒 **Service Isolation**: Backend services only accessible via internal network

**Perfect for**: Learning enterprise security patterns, portfolio demonstration, security engineering practice

## 🛠️ System Overview

| **Component** | **Technology** | **Purpose** | **Status** | **Deployment** |
|---------------|----------------|-------------|------------|----------------|
| **Frontend** | React 18 + TypeScript | User Interface | ✅ Production | Docker, K8s |
| **API Gateway** | Go + Gin | Routing & Security | 🔄 Updating | Docker, K8s |
| **Auth Service** | Python + FastAPI | JWT Validation & User Context | 📋 Planned | Docker, K8s |
| **User Service** | Python + FastAPI | User Management | ✅ Production | Docker, K8s |
| **Order Service** | Python + FastAPI | Business Logic | ✅ Production | Docker, K8s |
| **Inventory Service** | Python + FastAPI | Asset Management | ✅ Production | Docker, K8s |
| **Database** | DynamoDB | Data Storage | ✅ Production | AWS |
| **Cache** | Redis | Session Management | ✅ Production | Docker, K8s |
| **Container** | Docker + K8s | Orchestration | ✅ Production | Local/Cloud |
| **Monitoring** | Prometheus + Grafana | Essential Auth Metrics | 📋 Planned | K8s |

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

## 🎮 Local Demo

**Available now:**
- Frontend: http://localhost:3000 (after running deploy script)
- Gateway: http://localhost:8080/health
- Complete system running locally with Docker

**Quick start:**
```bash
./scripts/deploy-docker.sh -bd all
# Then visit http://localhost:3000
```

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
# Run comprehensive security tests
./scripts/test-local.sh --environment dev --all

# Quick health checks
./scripts/smoke-test.sh

# API authentication testing
./scripts/cli-client.sh login
./scripts/cli-client.sh test
```

## ☸️ Kubernetes Learning

### **Local Kubernetes Setup**
```bash
# Check prerequisites first
./scripts/prerequisites-checker.sh

# Deploy with root deployment script
./deploy.sh all dev

# Check deployment status
kubectl get pods -n order-processor
kubectl get services -n order-processor

# Access services (automatic port forwarding)
./scripts/smoke-test.sh

# Manual port forwarding if needed
kubectl port-forward svc/frontend 30003:80 -n order-processor &
kubectl port-forward svc/gateway 30002:8080 -n order-processor &
kubectl port-forward svc/user-service 30004:8000 -n order-processor &
kubectl port-forward svc/inventory-service 30005:8001 -n order-processor &
kubectl port-forward svc/order-service 30006:8002 -n order-processor &
```

### **Kubernetes Concepts Demonstrated**
- **Deployments**: Multi-replica service deployments
- **Services**: ClusterIP, NodePort, LoadBalancer patterns
- **ConfigMaps/Secrets**: Configuration management
- **Namespaces**: Environment isolation
- **Kustomize**: Environment-specific configurations

## 📊 Monitoring

**Currently implemented:**
- ✅ Health checks on all services
- ✅ Structured JSON logging with correlation IDs
- ✅ Prometheus metrics collection setup

**Planned (Simplified Scope):**
- 📋 Essential authentication metrics (JWT success/failure, request duration)
- 📋 Basic security monitoring (rate limiting, failed logins)
- 📋 Simple dashboards for auth operations
- 📋 Basic alerting for authentication failures

**For detailed monitoring design:** See [Monitoring Design](docs/design-docs/monitoring-design.md) and [Monitoring Guide](monitoring/README.md).

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
- 📊 **Security Monitoring**: Essential authentication metrics and alerts

**For detailed learning outcomes, see:**
- **[Security Documentation](docs/design-docs/)** - Complete security patterns
- **[Architecture Decisions](docs/design-docs/)** - Technology choices and rationale

## 🚀 Current Development Focus

**🔥 HIGHEST PRIORITY: Centralized Authentication Architecture**
- **Phase 1**: Create dedicated Auth Service for JWT validation
- **Phase 2**: Update Gateway to use Auth Service for authentication
- **Phase 3**: Remove JWT validation from backend services
- **Phase 4**: Implement network security controls

**📊 HIGH PRIORITY: Essential Authentication Monitoring**
- **Week 1**: Basic Auth Service metrics (JWT success/failure)
- **Week 2**: Gateway authentication tracking
- **Week 3**: Essential security monitoring
- **Week 4**: Basic dashboards and alerting

**🌐 HIGH PRIORITY: Frontend Authentication Retesting**
- Retest complete authentication flow after Auth Service implementation
- Validate protected routes and error handling
- Ensure seamless user experience

## ⚠️ Current Limitations

**This is a learning project, so:**
- 🏠 **Local Focus**: Primarily designed for local development and learning
- 💰 **Cost Conscious**: Uses cost-effective AWS services (DynamoDB vs RDS)
- 📚 **Learning Priority**: Code quality and learning over production optimization
- 🔐 **Security Focus**: Enterprise security patterns over advanced features

## 🚀 Getting Started

1. **Quick Demo**: Follow the [Quick Start](#-quick-start) above
2. **Detailed Setup**: [Local Development Guide](docs/deployment-guide.md)
3. **New Auth Architecture**: [Centralized Authentication Design](docs/centralized-authentication-architecture.md)
4. **Security Implementation**: [Security Documentation](docs/design-docs/)
5. **Kubernetes Setup**: [Kubernetes Guide](kubernetes/README.md)
6. **API Testing**: [Integration Tests](integration_tests/README.md)

---

**🔐 This project demonstrates comprehensive security architecture suitable for enterprise environments**

**🛡️ Perfect for**: Security engineering roles, secure development practices, enterprise architecture

**🔒 Questions about security implementation?** Check the [Security Documentation](docs/design-docs/) or open an issue

*Built with security-first principles and enterprise-ready patterns*