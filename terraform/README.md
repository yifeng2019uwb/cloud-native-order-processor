# Order Processor Infrastructure

## Overview
- **Dev Environment**: Local FastAPI services + DynamoDB (no Lambda/API Gateway)
- **Prod Environment**: EKS + Kubernetes + RDS (full-scale, ~$80/month)

## Usage
```bash
# Deploy dev (Local FastAPI)
terraform apply -var="environment=dev"

# Deploy prod (Kubernetes)
terraform apply -var="environment=prod"
