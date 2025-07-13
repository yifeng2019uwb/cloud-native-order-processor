# 🚀 Cloud-Native Order Service

A comprehensive cloud-native microservice built for learning modern DevOps, infrastructure automation, and scalable system design. This project demonstrates real-world practices used in production environments while maintaining cost-effective development patterns.

## 📋 Project Overview

**Current Focus:** User Authentication Service with JWT-based security
**Architecture:** Cloud-native microservices with infrastructure as code
**Learning Goals:** Master Terraform, FastAPI, Docker, Kubernetes, and AWS services

### 🎯 What This Project Teaches

- **Infrastructure as Code** with Terraform
- **Containerization** with Docker and Kubernetes
- **CI/CD Pipelines** with GitHub Actions
- **Cloud Security** with AWS IAM, JWT, and encryption
- **Database Design** with DynamoDB and PostgreSQL
- **API Development** with FastAPI and async Python
- **Testing Strategies** with unit, integration, and load testing
- **Cost Management** and resource optimization

## 🏗️ Architecture

### **Current Implementation**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Development   │    │   Production    │    │     Testing     │
│                 │    │                 │    │                 │
│ EKS + K8s       │    │ EKS + K8s       │    │ Unit + E2E      │
│ DynamoDB        │    │ PostgreSQL + RDS│    │ Coverage Reports│
│ Local testing   │    │ Auto-scaling    │    │ CI/CD pipeline  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Services Architecture**
```
services/
├── common/           # Shared models, DAOs, utilities
│   ├── src/
│   │   ├── models/   # Pydantic data models
│   │   └── database/ # Database access layer
│   └── tests/        # Unit tests with coverage
└── order-service/    # Main service (User Auth MVP)
    ├── src/          # FastAPI application
    └── tests/        # Service-specific tests
```

## 🚀 Quick Start

### **Prerequisites**
- Python 3.11+
- AWS CLI configured
- Terraform ≥ 1.5.0
- Docker Desktop
- Git

### **Local Development**
```bash
# 1. Clone and setup
git clone <repository-url>
cd cloud-native-order-processor

# 2. Run full development cycle
./scripts/test-local.sh --environment dev --full-test

# 3. Or run individual steps
./scripts/deploy.sh --environment dev        # Deploy infrastructure
./scripts/deploy-app.sh --environment dev    # Deploy application
./scripts/test-integration.sh --environment dev  # Run tests
./scripts/destroy.sh --environment dev --force   # Clean up
```

### **Run Tests Only**
```bash
cd services/common
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/test_models/ -v --cov=src/models
```

## 🔧 Development Workflow

### **Daily Development**
```bash
# Morning: Deploy infrastructure once
./scripts/deploy.sh --environment dev

# During development: Quick app updates
./scripts/deploy-app.sh --environment dev --skip-build

# Test changes
./scripts/test-integration.sh --environment dev

# End of day: Clean up resources
./scripts/destroy.sh --environment dev --force
```

### **Pre-Push Validation**
```bash
# Full validation pipeline
./scripts/test-local.sh --environment dev --full-test

# Production simulation
./scripts/test-local.sh --environment prod --full-test
```

## 🧪 Testing Strategy

### **Test Pyramid**
- **Unit Tests**: Models, DAOs, business logic (fast, isolated)
- **Integration Tests**: API endpoints, database connections
- **End-to-End Tests**: Complete user workflows
- **Load Tests**: Performance and scalability validation

### **Coverage Goals**
- Unit Tests: >90% coverage on core business logic
- Integration Tests: All API endpoints and database operations
- Security Tests: Authentication, authorization, input validation

## 🛠️ Technology Stack

### **Backend Services**
- **Framework**: FastAPI (Python 3.11)
- **Authentication**: JWT with bcrypt password hashing
- **Validation**: Pydantic models with strict typing
- **Testing**: pytest with async support and coverage

### **Infrastructure**
- **IaC**: Terraform for all AWS resources
- **Containers**: Docker with multi-stage builds
- **Orchestration**: Kubernetes (EKS) for production
- **Containerization**: Docker with multi-stage builds

### **Data Layer**
- **Development**: DynamoDB (cost-effective, NoSQL)
- **Production**: PostgreSQL (ACID compliance, complex queries)
- **Caching**: Redis for session management and rate limiting
- **Files**: S3 for static assets and backup storage

### **DevOps & Monitoring**
- **CI/CD**: GitHub Actions with automated testing
- **Secrets**: AWS Secrets Manager and Kubernetes secrets
- **Monitoring**: CloudWatch for AWS services
- **Cost Control**: Automated resource cleanup and tagging

## 📦 Project Structure

```
cloud-native-order-processor/
├── .github/workflows/        # CI/CD pipelines
├── config/                   # Environment configurations
├── scripts/                  # Deployment and utility scripts
├── services/                 # Microservices code
│   ├── common/              # Shared libraries
│   └── order-service/       # Main service implementation
├── terraform/               # Infrastructure as code
├── docker/                  # Container configurations
├── kubernetes/              # K8s manifests and configs
└── docs/                    # Additional documentation
```

## 🎯 Roadmap & Learning Plan

### **Phase 1: Foundation (Current)** ✅
- [x] User authentication service with JWT
- [x] Unit testing with coverage reports
- [x] Terraform infrastructure automation
- [x] CI/CD pipeline with GitHub Actions
- [x] Docker containerization

### **Phase 2: Core Services (Next 2-4 weeks)**
- [ ] Trading/order management endpoints
- [ ] Integration testing suite
- [ ] Kubernetes deployment with EKS
- [ ] Database schema design and migrations
- [ ] API rate limiting and caching

### **Phase 3: Production Features (Month 2-3)**
- [ ] Comprehensive security implementation
- [ ] Monitoring and alerting setup
- [ ] Load testing and performance optimization
- [ ] Multi-environment deployment (staging/prod)
- [ ] Database backup and disaster recovery

### **Phase 4: Advanced Features (Month 3-6)**
- [ ] Scheduled trading (crypto DCA strategies)
- [ ] Real-time price feeds and WebSocket support
- [ ] Compliance features (tax reporting, GDPR)
- [ ] Mobile API optimization
- [ ] Advanced analytics and reporting

### **Phase 5: Scale & Optimization (Month 6+)**
- [ ] Multi-region deployment
- [ ] Service mesh implementation
- [ ] Advanced monitoring (Prometheus/Grafana)
- [ ] Cost optimization strategies
- [ ] Open source contribution preparation

## 💰 Cost Management

### **Development Costs**
- **Daily usage**: ~$1-5/day when actively developing
- **Monthly estimate**: ~$20-50/month with regular cleanup
- **Cost control**: Automated resource destruction after testing

### **Best Practices**
- Always run `destroy.sh --force` after development sessions
- Use `dev` environment for daily work (EKS + DynamoDB)
- Reserve `prod` environment for final validation only
- Monitor AWS billing dashboard regularly

## 🤝 Contributing

This is a personal learning project, but feedback and suggestions are welcome!

### **Areas for Feedback**
- Architecture and design patterns
- Security implementations
- Performance optimizations
- Testing strategies
- Documentation improvements

## 📚 Learning Resources

### **Technologies Used**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

### **Inspiration & Patterns**
- Microservices patterns from industry leaders
- Cloud-native design principles
- DevOps best practices from major tech companies

## 🔐 Security Considerations

- JWT tokens with secure secret management
- Password hashing with bcrypt and salt
- AWS IAM roles with least privilege access
- Secrets stored in AWS Secrets Manager
- Container security scanning in CI/CD
- Input validation with Pydantic models

## 📄 License

This project is for educational purposes. Feel free to learn from the code and architecture patterns.

---

**Built with ❤️ for learning modern cloud-native development**

*Remember: Always clean up AWS resources when done to avoid unexpected charges!*