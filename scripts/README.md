# Scripts Directory

This directory contains comprehensive scripts for building, testing, deploying, and managing the Cloud Native Order Processor system.

## 📋 Quick Start

```bash
# Start all services locally
./scripts/manage-services.sh start all

# Run full CI/CD pipeline locally
./scripts/test-local.sh --environment dev --all

# Quick build and deploy
./scripts/quick_build.sh
```

## 🚀 Service Management

### manage-services.sh

A comprehensive script to start, stop, restart, and monitor all services locally.

```bash
# Start all services
./scripts/manage-services.sh start all

# Check status
./scripts/manage-services.sh status

# Stop all services
./scripts/manage-services.sh stop all

# View logs
./scripts/manage-services.sh logs inventory-service
```

**Features:**
- ✅ **Frontend** (React/Vite) - Port 3000
- ✅ **User Service** (FastAPI) - Port 8000
- ✅ **Inventory Service** (FastAPI) - Port 8001
- Automatic dependency installation
- Virtual environment detection
- Process management with PID tracking
- Comprehensive logging
- Colored output for better readability

## 🧪 Testing & Validation

### test-local.sh

Mirrors the CI/CD pipeline locally for pre-push validation.

```bash
# Full pipeline (build → deploy → test → destroy)
./scripts/test-local.sh --environment dev --all

# Development cycle (keeps infrastructure running)
./scripts/test-local.sh --environment dev --dev-cycle

# App-only deployment (assumes infra exists)
./scripts/test-local.sh --environment dev --app-only
```

**Environments:**
- **`dev`** - Local FastAPI services (development)
- **`prod`** - EKS + Kubernetes (full infrastructure)

### test-integration.sh

Run integration tests against deployed infrastructure.

```bash
./scripts/test-integration.sh --environment dev
```

### build-test-frontend.sh

Build and test the frontend application.

```bash
./scripts/build-test-frontend.sh
```

## 🏗️ Build & Deploy

### quick_build.sh

Quick ECR build and push for immediate deployment.

```bash
./scripts/quick_build.sh
```

**What it does:**
- Creates ECR repository if needed
- Builds Docker image
- Pushes to ECR with timestamped and latest tags

### deploy.sh

Deploy infrastructure using Terraform.

```bash
./scripts/deploy.sh --environment dev
./scripts/deploy.sh --environment prod
```

**What it deploys:**
- **dev**: Local FastAPI services + DynamoDB
- **prod**: EKS + RDS + S3 + SNS/SQS

### deploy-app.sh

Deploy application to infrastructure.

```bash
./scripts/deploy-app.sh --environment dev
./scripts/deploy-app.sh --environment prod --skip-build
```

**What it does:**
- **dev**: Runs/Builds local FastAPI services
- **prod**: Builds Docker image, pushes to ECR, deploys to EKS

### deploy-docker.sh

Deploy using Docker Compose for local/development environments.

```bash
./scripts/deploy-docker.sh
```

### ecr_build_push.sh

Build and push Docker images to ECR.

```bash
./scripts/ecr_build_push.sh
```

## 🧹 Cleanup & Maintenance

### destroy.sh

Destroy all AWS resources created by Terraform.

```bash
./scripts/destroy.sh --environment dev --force
./scripts/destroy.sh --environment prod --force
```

**Important:** Always run with `--force` to avoid ongoing AWS charges!

### workspace-cleanup.sh

Emergency cleanup script for workspace.

```bash
./scripts/workspace-cleanup.sh
```

## 🔧 Infrastructure & Configuration

### validate-environment.sh

Validate environment setup and prerequisites.

```bash
./scripts/validate-environment.sh
```

### generate-k8s-config.sh

Generate Kubernetes configuration files.

```bash
./scripts/generate-k8s-config.sh
```

### full-cycle-local.sh

Complete local development cycle script.

```bash
./scripts/full-cycle-local.sh
```

## 📚 Shared Utilities

### shared/prerequisites-checker.sh

Check and validate system prerequisites.

```bash
./scripts/shared/prerequisites-checker.sh
```

## 📖 Documentation

### build-test-deploy.md

Complete guide for the full build → deploy → test → destroy cycle.

**Key workflows:**
- **Daily Development**: Deploy once, iterate on app
- **Pre-Push Validation**: Full pipeline testing
- **Production Simulation**: EKS-based testing

## 💰 Cost Management

### Cost Estimates:
- **dev environment**: ~$1-5/day when running
- **prod environment**: ~$10-30/day when running

### Cost Control:
```bash
# Always clean up when done
./scripts/destroy.sh --environment dev --force

# Emergency cleanup
./scripts/workspace-cleanup.sh
```

## 🔧 Prerequisites

### Required Tools:
- Terraform (>= 1.5.0)
- AWS CLI (>= 2.0.0)
- Docker (running daemon)
- Node.js and npm
- Python 3.11+
- jq (for JSON parsing)

### AWS Setup:
```bash
# Configure credentials
aws configure

# Verify access
aws sts get-caller-identity
```

## 🎯 Common Workflows

### Daily Development
```bash
# Start services locally
./scripts/manage-services.sh start all

# Or use Docker
./scripts/deploy-docker.sh
```

### Pre-Push Validation
```bash
# Full validation
./scripts/test-local.sh --environment dev --all

# Production simulation
./scripts/test-local.sh --environment prod --all
```

### Infrastructure Deployment
```bash
# Deploy infrastructure
./scripts/deploy.sh --environment dev

# Deploy application
./scripts/deploy-app.sh --environment dev

# Clean up when done
./scripts/destroy.sh --environment dev --force
```

### Quick Iteration
```bash
# App-only deployment (assumes infra exists)
./scripts/deploy-app.sh --environment dev --skip-build

# Or use development cycle
./scripts/test-local.sh --environment dev --dev-cycle
```

## 🐛 Troubleshooting

### Common Issues:

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

**Service startup issues:**
```bash
./scripts/manage-services.sh status
./scripts/manage-services.sh logs [service-name]
```

## 📋 Script Summary

| Script | Purpose | Use Case |
|--------|---------|----------|
| `manage-services.sh` | Local service management | Daily development |
| `test-local.sh` | CI/CD pipeline mirror | Pre-push validation |
| `deploy.sh` | Infrastructure deployment | Environment setup |
| `deploy-app.sh` | Application deployment | Code deployment |
| `destroy.sh` | Resource cleanup | Cost control |
| `quick_build.sh` | Fast ECR build | Quick iteration |
| `validate-environment.sh` | Environment validation | Setup verification |
| `workspace-cleanup.sh` | Emergency cleanup | Troubleshooting |

---

**Remember:** Always run `destroy.sh --force` when done to avoid unexpected AWS charges!

### Quick Start

```bash
# Make the script executable (if not already done)
chmod +x scripts/manage-services.sh

# Start all services
./scripts/manage-services.sh start all

# Check status
./scripts/manage-services.sh status

# Stop all services
./scripts/manage-services.sh stop all
```

### Usage

```bash
./scripts/manage-services.sh [COMMAND] [SERVICE]
```

### Commands

- `start` - Start a service or all services
- `stop` - Stop a service or all services
- `restart` - Restart a service or all services
- `status` - Show status of all services
- `logs` - Show logs for a specific service
- `help` - Show help message

### Services

- `all` - All services (frontend, user-service, inventory-service)
- `frontend` - React frontend application
- `user-service` - FastAPI user authentication service
- `inventory-service` - FastAPI inventory management service

### Examples

```bash
# Start all services
./scripts/manage-services.sh start all

# Start only frontend
./scripts/manage-services.sh start frontend

# Stop only user service
./scripts/manage-services.sh stop user-service

# Restart inventory service
./scripts/manage-services.sh restart inventory-service

# Check status of all services
./scripts/manage-services.sh status

# View frontend logs
./scripts/manage-services.sh logs frontend

# View inventory service logs
./scripts/manage-services.sh logs inventory-service
```

### Features

- **Automatic dependency installation** - Installs npm dependencies if missing
- **Virtual environment detection** - Automatically finds and activates Python virtual environments
- **Process management** - Tracks PIDs and ensures clean shutdown
- **Logging** - Captures all service logs in `logs/` directory
- **Status monitoring** - Shows running status with colored output
- **Port management** - Handles port conflicts automatically
- **Error handling** - Graceful error handling and recovery

### Log Files

All service logs are stored in the `logs/` directory:
- `logs/frontend.log` - Frontend development server logs
- `logs/user-service.log` - User service logs
- `logs/inventory-service.log` - Inventory service logs

### Ports

- **Frontend**: 3000 (or next available port)
- **User Service**: 8000
- **Inventory Service**: 8001

### Prerequisites

- Node.js and npm installed
- Python 3.11+ installed
- Virtual environments set up for Python services
- AWS credentials configured (for backend services)