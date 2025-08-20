# Cloud Native Order Processor - Scripts Directory

This directory contains utility scripts for development, testing, deployment, and management of the Cloud Native Order Processor system.

## 📁 Available Scripts

### 1. **`test-local.sh`** - Local Testing & CI/CD Mirror
**Purpose**: Comprehensive local testing script that mirrors CI/CD pipeline functionality.

**Features:**
- Full pipeline testing (build → deploy → app → test → destroy)
- Component-level testing (frontend, gateway, services)
- Environment support (dev/prod)
- Development cycle workflows
- Dry-run mode for validation

**Usage:**
```bash
# Full pipeline testing
./scripts/test-local.sh --environment dev --all

# Development cycle (deploy → app → test, keep infra)
./scripts/test-local.sh --environment dev --dev-cycle

# Component-specific testing
./scripts/test-local.sh --frontend
./scripts/test-local.sh --gateway
./scripts/test-local.sh --services

# Individual job testing
./scripts/test-local.sh --environment dev --build
./scripts/test-local.sh --environment dev --deploy
./scripts/test-local.sh --environment dev --test
```

**Examples:**
```bash
# Daily development workflow
./scripts/test-local.sh --environment dev --dev-cycle

# Pre-push validation
./scripts/test-local.sh --environment dev --all

# Component testing only
./scripts/test-local.sh --frontend
```

### 2. **`smoke-test.sh`** - Quick Health Checks
**Purpose**: Rapid health checks for all services with automatic port forwarding setup.

**Features:**
- Service connectivity testing
- Health endpoint validation
- Automatic Kubernetes port forwarding
- Test result summary
- Service status reporting

**Usage:**
```bash
./scripts/smoke-test.sh
```

**What it tests:**
- Frontend accessibility
- Gateway health
- User Service health
- Inventory Service health
- Order Service health
- Service connectivity

### 3. **`cli-client.sh`** - API Testing Client
**Purpose**: Command-line client for testing APIs and demonstrating authentication flows.

**Features:**
- Authentication token management
- API endpoint testing
- Automatic port forwarding setup
- Token persistence
- Comprehensive API examples

**Usage:**
```bash
./scripts/cli-client.sh

# Available commands:
# - login: Authenticate and get token
# - logout: Clear stored token
# - status: Check authentication status
# - test: Run API tests
# - help: Show available commands
```

**Authentication Flow:**
```bash
# Login and get token
./scripts/cli-client.sh login

# Test authenticated endpoints
./scripts/cli-client.sh test

# Check token status
./scripts/cli-client.sh status
```

### 4. **`prerequisites-checker.sh`** - Environment Validation
**Purpose**: Validates that all required tools and dependencies are available.

**Features:**
- Tool availability checking
- Docker runtime validation
- Kubernetes connectivity testing
- Comprehensive environment validation

**Usage:**
```bash
# Check all prerequisites
./scripts/prerequisites-checker.sh

# Check specific components
./scripts/prerequisites-checker.sh tools
./scripts/prerequisites-checker.sh docker
./scripts/prerequisites-checker.sh k8s
```

**Required Tools:**
- Docker
- kubectl
- Go
- Python3
- Node.js
- npm

### 5. **`config-loader.sh`** - Configuration Management
**Purpose**: Loads and validates configuration for different environments.

**Features:**
- Environment-specific config loading
- Configuration validation
- Default value management
- Environment variable handling

**Usage:**
```bash
source scripts/config-loader.sh
load_config "dev"
```

### 6. **`docker-utils.sh`** - Docker Operations
**Purpose**: Provides Docker-related utility functions for building and managing containers.

**Features:**
- Docker daemon checks
- Image building
- Container lifecycle management
- Health checks
- Resource cleanup

**Usage:**
```bash
source scripts/docker-utils.sh

# Check Docker environment
check_docker_running
check_docker_daemon

# Build and run containers
build_docker_image "./frontend" "frontend" "latest"
run_docker_container "frontend" "frontend-app" "3000:80"
```

### 7. **`k8s-utils.sh`** - Kubernetes Operations
**Purpose**: Provides Kubernetes utility functions for deployment and management.

**Features:**
- Cluster connectivity checks
- Namespace management
- Manifest application
- Deployment monitoring
- Pod health checks
- Service management

**Usage:**
```bash
source scripts/k8s-utils.sh

# Check Kubernetes environment
check_kubectl
check_k8s_cluster

# Deploy resources
create_namespace "order-processor"
apply_k8s_manifests "kubernetes/dev/" "order-processor"
wait_for_rollout "user-service" "order-processor"
```

### 8. **`logging.sh`** - Logging Utilities
**Purpose**: Provides consistent logging functions across all scripts.

**Features:**
- Color-coded log levels
- Timestamp formatting
- Configurable log levels
- Section headers
- Progress indicators

**Usage:**
```bash
source scripts/logging.sh

log_info "Starting deployment..."
log_success "Component deployed successfully"
log_warning "Resource usage is high"
log_error "Deployment failed"
log_step "Building component..."
```

### 9. **`update-aws-credentials.sh`** - AWS Credential Management
**Purpose**: Manages AWS credentials and updates Kubernetes secrets.

**Features:**
- AWS credential validation
- Kubernetes secret updates
- Service pod restarts
- Credential rotation

**Usage:**
```bash
./scripts/update-aws-credentials.sh
```

## 🚀 Root Deployment Script

**`deploy.sh`** (in project root) is the main deployment orchestrator:

```bash
# Deploy all components
./deploy.sh all dev

# Deploy specific components
./deploy.sh frontend dev
./deploy.sh gateway dev
./deploy.sh services dev
./deploy.sh monitoring dev

# Production deployment
./deploy.sh all prod
```

**Deployment Order:**
1. Infrastructure (K8s, networking)
2. Monitoring (Prometheus, Grafana, Loki)
3. Services (user, inventory, order)
4. Gateway (API gateway)
5. Frontend (React application)

## 🧪 Testing Workflow

### **Quick Health Check**
```bash
# Run smoke tests
./scripts/smoke-test.sh
```

### **Full Local Testing**
```bash
# Run complete test suite
./scripts/test-local.sh --environment dev --all
```

### **API Testing**
```bash
# Test APIs with CLI client
./scripts/cli-client.sh login
./scripts/cli-client.sh test
```

### **Component Testing**
```bash
# Test specific components
./scripts/test-local.sh --frontend
./scripts/test-local.sh --gateway
./scripts/test-local.sh --services
```

## 🔧 Development Workflow

### **Daily Development**
```bash
# 1. Check prerequisites
./scripts/prerequisites-checker.sh

# 2. Run development cycle
./scripts/test-local.sh --environment dev --dev-cycle

# 3. Quick health checks
./scripts/smoke-test.sh
```

### **Pre-Push Validation**
```bash
# Full validation
./scripts/test-local.sh --environment dev --all
```

### **Component Updates**
```bash
# Update and test specific component
./scripts/test-local.sh --frontend
./scripts/test-local.sh --gateway
./scripts/test-local.sh --services
```

## 📊 Port Configuration

**Development Ports:**
- Frontend: http://localhost:30003
- Gateway: http://localhost:30002
- Grafana: http://localhost:30001
- User Service: http://localhost:30004
- Inventory Service: http://localhost:30005
- Order Service: http://localhost:30006

## 🐛 Troubleshooting

### **Common Issues**

1. **Port forwarding errors**: Run `./scripts/smoke-test.sh` to auto-setup
2. **Authentication failures**: Use `./scripts/cli-client.sh login` to refresh tokens
3. **Service connectivity**: Check prerequisites with `./scripts/prerequisites-checker.sh`
4. **Deployment issues**: Use `./deploy.sh` for proper deployment order

### **Debug Mode**

Enable verbose output:
```bash
./scripts/test-local.sh --environment dev --all -v
```

### **Environment Issues**

Check environment setup:
```bash
./scripts/prerequisites-checker.sh all
```

## 📚 Best Practices

1. **Always run prerequisites check** before major operations
2. **Use smoke tests** for quick health validation
3. **Follow deployment order** when using `deploy.sh`
4. **Test components individually** before full deployment
5. **Use development cycle** for iterative development
6. **Validate with full test suite** before pushing changes

## 🔗 Related Documentation

- **[Main README](../README.md)** - Project overview and architecture
- **[Deployment Guide](../docs/deployment-guide.md)** - Detailed deployment instructions
- **[Kubernetes Setup](../kubernetes/README.md)** - Kubernetes configuration
- **[Integration Tests](../integration_tests/README.md)** - API testing documentation

---

**💡 Tip**: Start with `./scripts/prerequisites-checker.sh` to ensure your environment is ready, then use `./scripts/smoke-test.sh` for quick health checks during development.