# 🏗️ Infrastructure

> Terraform configurations for deploying the Cloud Native Order Processor infrastructure across different environments

## 🚀 Quick Start
- **Prerequisites**: Terraform, AWS CLI, kubectl
- **Configure**: `aws configure` (set up AWS credentials)
- **Deploy Dev**: `./apply.sh dev` (development environment)
- **Deploy Prod**: `./apply.sh prod` (production environment)
- **Destroy**: `./destroy.sh` (clean up resources)

## ✨ Key Features
- Multi-environment deployment (dev/prod)
- EKS cluster with managed node groups
- DynamoDB tables with proper IAM roles
- Container registry (ECR) for Docker images
- Monitoring stack (Prometheus, Grafana, Loki)

## 📁 Project Structure
```
terraform/
├── apply.sh                  # Deploy infrastructure
├── destroy.sh                # Tear down infrastructure
├── dynamodb.tf               # DynamoDB tables (users, orders, inventory)
├── iam.tf                    # IAM roles and policies
├── eks.tf                    # EKS cluster (prod only)
├── ecr.tf                    # ECR repositories (prod only)
├── vpc.tf                    # VPC networking (prod only)
├── redis.tf                  # ElastiCache Redis (prod only)
├── s3.tf                     # S3 buckets
├── messaging.tf              # SQS/SNS
├── locals.tf                 # Naming conventions and constants
├── variables.tf              # Input variables
├── outputs.tf                # Output values
├── main.tf                   # Provider configuration
├── config/                   # Environment configs
└── infrastructure-tests/     # Infrastructure tests
```

## 🔗 Quick Links
- [Kubernetes Documentation](../kubernetes/README.md)
- [Docker Documentation](../docker/README.md)
- [Services Overview](../services/README.md)
- [Design Documentation](../docs/design-docs/kubernetes-design.md)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - Infrastructure deployed and working
- **Last Updated**: February 2026

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and code.