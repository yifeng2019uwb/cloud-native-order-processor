# 🐳 Docker

> Docker configurations for running the entire Cloud Native Order Processor application stack

## 🚀 Quick Start

### Local try-it (no AWS account needed) ⭐
For testers and learners: download the repo, have Docker, run one command.

```bash
# From project root:
./docker/deploy.sh local deploy
./docker/deploy.sh local destroy    # Stop and remove local stack
```

**Prerequisites**: Docker and Docker Compose only. You do **not** need Python, Go, or AWS CLI—all services and DynamoDB table creation run in containers.

- **Frontend**: http://localhost:3000
- **Gateway**: http://localhost:8080

### AWS deploy (requires AWS credentials)
- **Prerequisites**: Docker, Docker Compose, AWS credentials
- **Deploy All**: `./docker/deploy.sh all deploy` (deploy all services with AWS DynamoDB)
- **Deploy Single**: `./docker/deploy.sh [service_name] deploy` (deploy specific service)
- **Stop All**: `./docker/deploy.sh all stop`

## ✨ Key Features
- Multi-service architecture with Docker Compose
- Production and development configurations
- Simplified port configuration (only Gateway exposed externally)
- Common package integration across services
- Security improvements with non-root users

## 📁 Project Structure
```
docker/
├── services/                  # Service-specific Dockerfiles
│   ├── frontend/             # Frontend Dockerfile
│   ├── gateway/              # Gateway Dockerfile
│   ├── user_service/         # User Service Dockerfile
│   ├── order_service/        # Order Service Dockerfile
│   ├── inventory_service/    # Inventory Service Dockerfile
│   ├── auth_service/         # Auth Service Dockerfile
│   └── insights-service/     # Insights Service Dockerfile
├── standard/                 # Standard Dockerfile templates
│   └── Dockerfile.template   # Base template for services
├── docker-compose.yml        # Production configuration
├── docker-compose.dev.yml    # Development configuration
├── docker-compose.local.yml  # Local development configuration
├── deploy.sh                 # Main deployment script
├── SETUP_INSIGHTS.md         # Insights service setup guide
└── README.md                 # This file
```

## 🔗 Quick Links
- [Kubernetes Documentation](../kubernetes/README.md)
- [Terraform Documentation](../terraform/README.md)
- [Services Overview](../services/README.md)
- [Gateway Documentation](../gateway/README.md)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All services containerized and working
- **Last Updated**: February 2026

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and code.