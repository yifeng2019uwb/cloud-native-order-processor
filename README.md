# 🚀 Cloud-Native Order Processor

> A comprehensive, production-ready cloud-native microservice platform demonstrating scalable, distributed architecture with security-first design. Built with modern technologies including Go, Python FastAPI, React, Kubernetes, and AWS infrastructure.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Kubernetes (Kind for local development)
- AWS CLI configured
- Node.js 18+ and Python 3.11+

### Installation
```bash
# Clone and setup
git clone <repository-url>
cd cloud-native-order-processor

# Deploy with Docker (recommended)
./scripts/deploy-docker.sh -bd all
```

### Basic Usage
```bash
# Access services
# Frontend: http://localhost:3000
# Gateway: http://localhost:8080
# User Service: http://localhost:8000
# Inventory Service: http://localhost:8001
# Order Service: http://localhost:8002
```

### Example
```bash
# Quick health check
curl http://localhost:8080/health
```

## ✨ Key Features

- **Complete Trading Platform**: 7 fully functional pages with real-time data
- **Microservices Architecture**: Go Gateway, Python FastAPI services, React frontend
- **Production Ready**: All services working perfectly with comprehensive testing
- **Security First**: JWT authentication, role-based access, centralized security management
- **Cloud Native**: Kubernetes deployment, AWS integration, containerized services

## 🔗 Quick Links

- 📚 [Documentation Hub](./docs/README.md) - **Start Here** - Central documentation for all users
- 📊 [Project Status](./docs/project-status.md) - Current progress and roadmap
- 🏗️ [System Architecture](./docs/design-docs/system-architecture.md) - Technical architecture details
- 🚀 [Deployment Guide](./docs/deployment-guide.md) - Complete deployment instructions
- 🛠️ [Technology Stack](./docs/design-docs/technology-stack.md) - Detailed technology information
- 📋 [Backlog](./BACKLOG.md) - Task backlog and priorities
- 📝 [Daily Work Log](./DAILY_WORK_LOG.md) - Progress tracking

## 📊 Status

**Current Status**: ✅ **PRODUCTION READY** - All core features complete and working perfectly
**Last Updated**: August 20, 2025

## ⚠️ Common Issues

### Issue 1: Port Conflicts
**Symptoms**: Services won't start, port already in use errors
**Solution**: Check and free up ports 3000, 8000, 8001, 8002, 8080

### Issue 2: AWS Credentials
**Symptoms**: DynamoDB connection errors, AWS permission denied
**Solution**: Run `aws configure` and verify credentials with `aws sts get-caller-identity`

### Issue 3: Kubernetes Deployment
**Symptoms**: Pods stuck in pending or crash loop
**Solution**: Check resource limits and run `kubectl describe pod [pod-name] -n order-processor`

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the documentation files linked above.