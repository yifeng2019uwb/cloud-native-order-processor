# 🏗️ Infrastructure

> Terraform configurations for deploying the Cloud Native Order Processor infrastructure across different environments

## 🚀 Quick Start
- **Prerequisites**: Terraform, AWS CLI, kubectl
- **Configure**: `aws configure` (set up AWS credentials)
- **Deploy Dev**: `./deploy.sh dev` (development environment)
- **Deploy Prod**: `./deploy.sh prod` (production environment)
- **Destroy**: `./deploy.sh destroy` (clean up resources)

## ✨ Key Features
- Multi-environment deployment (dev/prod)
- EKS cluster with managed node groups
- DynamoDB tables with proper IAM roles
- Container registry (ECR) for Docker images
- Monitoring stack (Prometheus, Grafana, Loki)

## 📁 Project Structure
```
terraform/
├── environments/
│   ├── dev/                   # Development environment
│   │   ├── main.tf           # Core infrastructure
│   │   ├── variables.tf      # Environment variables
│   │   └── outputs.tf        # Output values
│   └── prod/                  # Production environment
│       ├── main.tf           # Core infrastructure
│       ├── variables.tf      # Environment variables
│       └── outputs.tf        # Output values
├── modules/                   # Reusable Terraform modules
│   ├── eks/                  # EKS cluster module
│   ├── dynamodb/             # DynamoDB module
│   └── monitoring/           # Monitoring stack module
├── scripts/                   # Deployment scripts
│   └── deploy.sh             # Main deployment script
└── README.md                 # This file
```

## 🔗 Quick Links
- [Kubernetes Documentation](../kubernetes/README.md)
- [Docker Documentation](../docker/README.md)
- [Services Overview](../services/README.md)
- [Design Documentation](../docs/design-docs/kubernetes-design.md)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - Infrastructure deployed and working
- **Last Updated**: January 8, 2025

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and code.