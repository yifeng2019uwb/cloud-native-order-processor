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

**Prerequisites**: Docker, Docker Compose, AWS CLI (for table creation; `pip install awscli` or `brew install awscli`)

- **Frontend**: http://localhost:3000
- **Gateway**: http://localhost:8080

### AWS deploy (requires AWS credentials)
- **Prerequisites**: Docker, Docker Compose, AWS credentials
- **Deploy All**: `./deploy.sh all deploy` (deploy all services with AWS DynamoDB)
- **Deploy Single**: `./deploy.sh [service_name] deploy` (deploy specific service)
- **Stop All**: `./deploy.sh all stop`

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
│   └── auth_service/         # Auth Service Dockerfile
├── standard/                 # Standard Dockerfile templates
│   └── Dockerfile.template   # Base template for services
├── docker-compose.yml        # Production configuration
├── docker-compose.dev.yml    # Development configuration
├── deploy.sh                 # Main deployment script
└── README.md                 # This file
```

## 🔗 Quick Links
- [Kubernetes Documentation](../kubernetes/README.md)
- [Terraform Documentation](../terraform/README.md)
- [Services Overview](../services/README.md)
- [Gateway Documentation](../gateway/README.md)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All services containerized and working
- **Last Updated**: January 8, 2025

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and code.