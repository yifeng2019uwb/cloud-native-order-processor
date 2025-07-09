# 🚀 Build, Test & Deploy Guide

Complete guide for the full build → deploy → test → destroy cycle for the Order Service.

## 📋 Quick Start

```bash
# Full automated cycle
./scripts/test-local.sh --environment dev --full-test

# Or manual steps
./scripts/deploy.sh --environment dev
./scripts/deploy-app.sh --environment dev
# ./scripts/test-integration.sh --environment dev
./scripts/destroy.sh --environment dev --force
```

## 🌍 Environments

- **`dev`** - Development with Lambda + API Gateway (cost-optimized)
- **`prod`** - Production with EKS + Kubernetes (full infrastructure)

## 🔄 Full Cycle Workflow

### **Automated Full Cycle**
```bash
# Complete pipeline with cleanup
./scripts/test-local.sh --environment dev --full-test

# Development cycle (keeps infrastructure running)
./scripts/test-local.sh --environment dev --dev-cycle
```

### **Manual Steps (for development iteration)**
```bash
# 1. Deploy infrastructure
./scripts/deploy.sh --environment dev

# 2. Deploy application
./scripts/deploy-app.sh --environment dev

# 3. Run integration tests
# ./scripts/test-integration.sh --environment dev

# 4. Clean up when done
./scripts/destroy.sh --environment dev --force
```

## 🛠️ Script Details

### **Infrastructure Deployment (`deploy.sh`)**
```bash
./scripts/deploy.sh --environment {dev|prod} [--verbose] [--dry-run]
```

**What it deploys:**
- **dev**: Lambda + API Gateway + DynamoDB
- **prod**: EKS + RDS + S3 + SNS/SQS

**Duration:** 15-25 minutes

### **Application Deployment (`deploy-app.sh`)**
```bash
./scripts/deploy-app.sh --environment {dev|prod} [--verbose] [--skip-build]
```

**What it does:**
- **dev**: Builds Lambda package and deploys to AWS Lambda
- **prod**: Builds Docker image, pushes to ECR, deploys to EKS

**Duration:** 3-8 minutes

### **Integration Testing (`test-integration.sh`)**
<!-- ```bash
./scripts/test-integration.sh --environment {dev|prod} [--verbose]
``` -->

**What it tests:**
- Infrastructure health checks
- Application endpoint connectivity
- Database connectivity
- End-to-end service workflow

**Duration:** 2-5 minutes

### **Cleanup (`destroy.sh`)**
```bash
./scripts/destroy.sh --environment {dev|prod} [--force] [--verbose]
```

**What it destroys:**
- All AWS resources created by Terraform
- Empties S3 buckets before deletion
- Removes leftover resources by tags

**Duration:** 5-15 minutes

## 📱 Development Workflows

### **Daily Development**
```bash
# Morning: Deploy once
./scripts/deploy.sh --environment dev

# During development: Redeploy app quickly
./scripts/deploy-app.sh --environment dev --skip-build

# Test changes
# ./scripts/test-integration.sh --environment dev

# End of day: Clean up
./scripts/destroy.sh --environment dev --force
```

### **Pre-Push Validation**
```bash
# Full validation
./scripts/test-local.sh --environment dev --full-test

# Production simulation (CI/CD style)
./scripts/test-local.sh --environment prod --full-test
```

## 💰 Cost Management

### **Cost Estimates:**
- **dev environment**: ~$1-5/day when running
- **prod environment**: ~$10-30/day when running

### **Cost Control:**
```bash
# Always clean up when done
./scripts/destroy.sh --environment dev --force

# Emergency cleanup
./scripts/workspace-cleanup.sh
```

## 🔧 Prerequisites

### **Required Tools:**
- Terraform (>= 1.5.0)
- AWS CLI (>= 2.0.0)
- Docker (running daemon)
- jq (for JSON parsing)

### **AWS Setup:**
```bash
# Configure credentials
aws configure

# Verify access
aws sts get-caller-identity
```

## 🐛 Troubleshooting

### **Common Issues:**

**Infrastructure conflicts:**
```bash
./scripts/destroy.sh --environment dev --force
```

**Terraform state issues:**
```bash
cd terraform
terraform destroy -auto-approve
```

**Docker build failures:**
```bash
./scripts/deploy-app.sh --environment dev --skip-build
```

**AWS credential issues:**
```bash
aws configure
aws sts get-caller-identity
```

## 🎯 Success Criteria

**You've successfully completed the cycle when:**
- ✅ Infrastructure deploys without errors
- ✅ Application deploys and responds to health checks
<!-- - ✅ Integration tests pass -->
- ✅ Resources clean up completely (no ongoing costs)

## 📚 Learning Path

1. **Start with**: `./scripts/test-local.sh --environment dev --full-test`
2. **Practice**: Manual steps for development iteration
3. **Advance to**: Production environment testing
4. **Master**: CI/CD pipeline integration

---

**Remember:** Always run `destroy.sh --force` when done to avoid unexpected AWS charges!