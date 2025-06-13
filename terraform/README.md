# Order Processor Infrastructure

## Overview
- **Dev Environment**: Lambda + API Gateway + RDS (cheap, ~$15/month)
- **Prod Environment**: EKS + Kubernetes + RDS (full-scale, ~$80/month)

## Usage
```bash
# Deploy dev (Lambda)
terraform apply -var="environment=dev"

# Deploy prod (Kubernetes)
terraform apply -var="environment=prod"
