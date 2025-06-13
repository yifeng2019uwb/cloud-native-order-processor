# 🚀 Build, Test & Deploy Guide

Complete guide for building, testing, and deploying the Cloud Native Order Processor using our enhanced deployment scripts.

## 📋 Quick Start

```bash
# 1. Deploy infrastructure
./scripts/deploy.sh --environment dev --profile learning

# 2. Deploy application
./scripts/deploy-app.sh --environment dev --profile learning

# 3. Run integration tests
./scripts/test-integration.sh --environment dev

# 4. Clean up when done
./scripts/destroy.sh --environment dev --profile learning --auto-approve --force-cleanup
```

## 🛠️ Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `deploy.sh` | Deploy AWS infrastructure (Terraform) | Infrastructure deployment |
| `deploy-app.sh` | Deploy application (Docker + K8s) | Application deployment |
| `test-integration.sh` | Run integration tests | Testing deployed system |
| `destroy.sh` | Clean up all resources | Cost control & cleanup |
| `test-local.sh` | Orchestrate full workflows | Development automation |

## 🌍 Environments & Profiles

### **Environments:**
- **`dev`** - Development environment, flexible deployment options
- **`prod`** - Production simulation, full CI/CD workflow only

### **Profiles:**
- **`learning`** - Cost-optimized for learning (smallest instances)
- **`minimum`** - Minimal resources for basic functionality
- **`prod`** - Production-scale resources

### **Valid Combinations:**
```bash
# Development options
--environment dev --profile learning    # Cheapest option
--environment dev --profile minimum     # Basic functionality
--environment dev --profile prod        # Full-scale testing

# Production simulation
--environment prod --profile prod       # CI/CD simulation only
```

## 📦 Infrastructure Deployment (`deploy.sh`)

### **Purpose:**
Deploy AWS infrastructure using Terraform including VPC, EKS, RDS, S3, and supporting services.

### **Usage:**
```bash
./scripts/deploy.sh --environment {dev|prod} --profile {learning|minimum|prod} [OPTIONS]
```

### **Options:**
- `--environment {dev|prod}` - Target environment
- `--profile {learning|minimum|prod}` - Resource profile
- `--verbose` - Enable detailed output
- `--dry-run` - Plan only, don't apply changes
- `--help` - Show help message

### **Examples:**
```bash
# Deploy cost-optimized dev environment
./scripts/deploy.sh --environment dev --profile learning

# Test deployment plan without applying
./scripts/deploy.sh --environment dev --profile learning --dry-run

# Deploy with verbose output
./scripts/deploy.sh --environment dev --profile learning --verbose

# Production simulation
./scripts/deploy.sh --environment prod --profile prod
```

### **What It Does:**
1. ✅ Validates prerequisites (Terraform, AWS CLI, credentials)
2. ✅ Loads environment and profile configurations
3. ✅ Runs `terraform init`, `plan`, and `apply`
4. ✅ Deploys basic Kubernetes manifests
5. ✅ Shows infrastructure outputs and next steps

### **Duration:** 15-25 minutes (EKS cluster creation takes time)

## 🐳 Application Deployment (`deploy-app.sh`)

### **Purpose:**
Build Docker images, push to ECR, and deploy applications to EKS cluster.

### **Usage:**
```bash
./scripts/deploy-app.sh --environment {dev|prod} --profile {learning|minimum|prod} [OPTIONS]
```

### **Options:**
- `--environment {dev|prod}` - Target environment
- `--profile {learning|minimum|prod}` - Resource profile
- `--verbose` - Enable detailed output
- `--dry-run` - Plan only, don't deploy
- `--skip-build` - Skip Docker build, use existing images
- `--help` - Show help message

### **Examples:**
```bash
# Deploy application to dev environment
./scripts/deploy-app.sh --environment dev --profile learning

# Redeploy without rebuilding Docker images (faster)
./scripts/deploy-app.sh --environment dev --profile learning --skip-build

# Test deployment plan
./scripts/deploy-app.sh --environment dev --profile learning --dry-run
```

### **What It Does:**
1. ✅ Validates infrastructure is deployed
2. ✅ Builds and pushes Docker images to ECR
3. ✅ Updates EKS kubeconfig
4. ✅ Deploys applications to Kubernetes
5. ✅ Verifies deployment and shows service URLs

### **Duration:** 3-8 minutes

## 🧪 Integration Testing (`test-integration.sh`)

### **Purpose:**
Run comprehensive integration tests against deployed infrastructure and applications.

### **Usage:**
```bash
./scripts/test-integration.sh --environment {dev|prod} [OPTIONS]
```

### **Options:**
- `--environment {dev|prod}` - Target environment
- `--verbose` - Enable detailed output
- `--dry-run` - Show what tests would run
- `--help` - Show help message

### **Examples:**
```bash
# Run integration tests
./scripts/test-integration.sh --environment dev

# Run with detailed output
./scripts/test-integration.sh --environment dev --verbose

# Check what tests would run
./scripts/test-integration.sh --environment dev --dry-run
```

### **What It Tests:**
1. ✅ Infrastructure health checks
2. ✅ Application endpoint connectivity
3. ✅ Database connectivity
4. ✅ Message queue functionality
5. ✅ End-to-end order processing workflow

### **Duration:** 2-5 minutes

## 🧹 Resource Cleanup (`destroy.sh`)

### **Purpose:**
Aggressively clean up ALL AWS resources to prevent unexpected charges.

### **Usage:**
```bash
./scripts/destroy.sh --environment {dev|prod} --profile {learning|minimum|prod} [OPTIONS]
```

### **Options:**
- `--environment {dev|prod}` - Target environment
- `--profile {learning|minimum|prod}` - Resource profile
- `--verbose` - Enable detailed output
- `--dry-run` - Show what would be destroyed
- `--auto-approve` - Skip confirmation prompts
- `--force-cleanup` - Nuclear cleanup of ALL project resources
- `--help` - Show help message

### **Examples:**
```bash
# Standard cleanup with confirmation
./scripts/destroy.sh --environment dev --profile learning

# Aggressive cleanup without prompts
./scripts/destroy.sh --environment dev --profile learning --auto-approve --force-cleanup

# See what would be destroyed
./scripts/destroy.sh --environment dev --profile learning --dry-run
```

### **What It Does:**
1. ✅ Empties S3 buckets before deletion
2. ✅ Runs Terraform destroy
3. ✅ **Nuclear cleanup** - finds and destroys resources by tags
4. ✅ Multi-region verification
5. ✅ Shows detailed status table of remaining resources
6. ✅ Cost impact analysis

### **Duration:** 5-15 minutes

## 🔄 Development Workflows

### **Typical Development Day:**

#### **Morning Setup:**
```bash
# Deploy infrastructure once
./scripts/deploy.sh --environment dev --profile learning

# Deploy application
./scripts/deploy-app.sh --environment dev --profile learning
```

#### **During Development (Iterative):**
```bash
# Make code changes, then redeploy app (fast)
./scripts/deploy-app.sh --environment dev --profile learning --skip-build

# Test changes
./scripts/test-integration.sh --environment dev

# Fix bugs, redeploy
./scripts/deploy-app.sh --environment dev --profile learning --skip-build

# Test again
./scripts/test-integration.sh --environment dev
```

#### **End of Day:**
```bash
# Clean up everything to save costs
./scripts/destroy.sh --environment dev --profile learning --auto-approve --force-cleanup
```

### **Pre-Push Validation:**
```bash
# Quick validation before committing
./scripts/test-local.sh --deploy-test --environment dev --profile learning

# Full CI/CD simulation
./scripts/test-local.sh --ci-simulation --environment prod --profile prod
```

## 🎯 Advanced Usage with `test-local.sh`

The master orchestration script that combines all deployment scripts:

### **Granular Control:**
```bash
# Individual steps
./scripts/test-local.sh --deploy-only --environment dev --profile learning
./scripts/test-local.sh --app-deploy-only --environment dev
./scripts/test-local.sh --integration-only --environment dev
./scripts/test-local.sh --destroy-only --environment dev

# Full workflows
./scripts/test-local.sh --deploy-test --environment dev --profile learning
./scripts/test-local.sh --ci-simulation --environment prod --profile prod
```

### **Development Workflow Options:**
```bash
# Deploy and keep for development
./scripts/test-local.sh --deploy-test --keep-environment --environment dev

# Full development cycle
./scripts/test-local.sh --full-dev-cycle --environment dev --profile learning
```

## 💰 Cost Management

### **Cost-Optimized Profiles:**
- **`learning`** - ~$5-15/day when running
- **`minimum`** - ~$10-25/day when running
- **`prod`** - ~$50-100/day when running

### **Cost Control Best Practices:**
1. **Always destroy when done** - Use `--force-cleanup` flag
2. **Use learning profile** for experimentation
3. **Check billing dashboard** regularly
4. **Verify cleanup** - Script shows cost impact analysis

### **Emergency Cost Control:**
```bash
# Nuclear cleanup across all regions
./scripts/destroy.sh --environment dev --profile learning --force-cleanup --auto-approve
./scripts/destroy.sh --environment prod --profile prod --force-cleanup --auto-approve

# Check for any missed resources
aws resourcegroupstaggingapi get-resources --tag-filters Key=Project,Values=order-processor --region us-west-2
```

## 🔧 Prerequisites

### **Required Tools:**
- **Terraform** (>= 1.0)
- **AWS CLI** (>= 2.0)
- **Docker** (running daemon)
- **kubectl** (for K8s deployment)
- **jq** (for JSON parsing)

### **AWS Setup:**
```bash
# Configure AWS credentials
aws configure

# Verify access
aws sts get-caller-identity
```

### **Installation Check:**
```bash
# Run any script with --help to check prerequisites
./scripts/deploy.sh --help
```

## 🐛 Troubleshooting

### **Common Issues:**

#### **"EntityAlreadyExists" Errors:**
```bash
# Clean up conflicting resources
./scripts/destroy.sh --environment dev --profile learning --force-cleanup --auto-approve
```

#### **Terraform State Issues:**
```bash
cd terraform
terraform state list
terraform state rm <problematic-resource>
terraform destroy -auto-approve
```

#### **Docker Build Failures:**
```bash
# Check Docker daemon
docker info

# Skip build and use existing images
./scripts/deploy-app.sh --environment dev --profile learning --skip-build
```

#### **EKS Connection Issues:**
```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name <cluster-name>

# Test connection
kubectl get nodes
```
<!-- 
### **Cost Verification:**
```bash
# Check what's running and costing money
aws resourcegroupstaggingapi get-resources --tag-filters Key=Project,Values=order-processor

# Billing dashboard
aws ce get-cost-and-usage --time-period Start=2025-06-01,End=2025-06-12 --granularity DAILY --metrics UnblendedCost
``` -->

## 📚 Learning Path

### **Beginner:**
1. Start with `deploy.sh --dry-run` to understand what gets created
2. Use `learning` profile for cost control
3. Practice with single environment (`dev`)

### **Intermediate:**
1. Try full `test-local.sh` workflows
2. Experiment with different profiles
3. Practice iterative development patterns

### **Advanced:**
1. Simulate CI/CD with `prod` environment
2. Modify scripts for your specific needs
3. Add custom integration tests

## 🎉 Success Metrics

### **You've Successfully Learned When:**
- ✅ You can deploy infrastructure consistently
- ✅ You can iterate on applications quickly
- ✅ You understand cost implications of each resource
- ✅ You can clean up completely every time
- ✅ You're comfortable with infrastructure as code
- ✅ You can simulate production deployments

**Remember: Always clean up resources when done to avoid unexpected AWS charges!**

---

*This guide covers practical DevOps skills used in real industry environments while keeping costs minimal for learning.*