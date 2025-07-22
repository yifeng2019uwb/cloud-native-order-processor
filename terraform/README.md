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
```

## Infrastructure Testing
```bash
# Run all infrastructure tests
./run-infrastructure-tests.sh

# Run specific test types
./run-infrastructure-tests.sh --test-type aws --verbose

# Test production environment
./run-infrastructure-tests.sh --environment prod
```

See [infrastructure-tests/README.md](infrastructure-tests/README.md) for detailed testing information.
