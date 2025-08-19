# 🚀 Deployment Guide

## 🎯 **Overview**

Complete deployment guide for the Cloud Native Order Processor system across different environments: local development, Docker, and Kubernetes.

## 🚀 **Quick Start**

### **Prerequisites**
- Docker and Docker Compose
- Kubernetes (Kind for local development)
- AWS CLI configured
- Node.js 18+ and Python 3.11+

## 🐳 **Docker Deployment (Development)**

### **1. Local Development (Recommended)**
```bash
# Clone and setup
git clone <repository-url>
cd cloud-native-order-processor

# Use the new deployment script (recommended)
./scripts/deploy-docker.sh -bd all

# Access services
# Frontend: http://localhost:3000
# Gateway: http://localhost:8080
# User Service: http://localhost:8000
# Inventory Service: http://localhost:8001
# Order Service: http://localhost:8002
```

### **2. Build + Deploy Specific Service**
```bash
# Build + Deploy all services
./scripts/deploy-docker.sh -bd all

# Build + Deploy specific service
./scripts/deploy-docker.sh -bd frontend-dev
```

### **3. Component Development**
```bash
# Build and test individual components
./frontend/build.sh              # Frontend build & test
./gateway/build.sh               # Gateway build & test
./services/build.sh              # Services build & test

# Or use Makefile shortcuts
make build                       # Build all components
make test                        # Test all components
make deploy-k8s                  # Deploy to Kubernetes
```

## ☸️ **Kubernetes Deployment (Production)**

### **1. Local Kubernetes (Kind)**
```bash
# Deploy to local Kubernetes
./scripts/deploy.sh --type k8s --environment dev

# Access services
# Frontend: http://localhost:30004
# Gateway: http://localhost:30000
```

### **2. Production Kubernetes**
```bash
# Deploy to production Kubernetes
./scripts/deploy.sh --type k8s --environment prod

# Configure kubectl for EKS
aws eks update-kubeconfig --region us-west-2 --name order-processor-prod
```

## 🔧 **Environment Configuration**

### **Environment Variables**
```bash
# Development
export TF_VAR_environment=dev
export TF_VAR_aws_region=us-west-2

# Production
export TF_VAR_environment=prod
export TF_VAR_aws_region=us-west-2
export TF_VAR_cluster_size=3
```

### **Service URLs**
```bash
# Override service URLs if needed
export USER_SERVICE_URL="http://localhost:8000"
export INVENTORY_SERVICE_URL="http://localhost:8001"
export ORDER_SERVICE_URL="http://localhost:8002"

# Environment (optional - defaults to 'dev')
export ENVIRONMENT="dev"
```

## 🏗️ **Infrastructure Deployment**

### **1. Terraform Deployment**
```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Deploy dev environment
terraform apply -var="environment=dev"

# Deploy production infrastructure
terraform apply -var="environment=prod"
```

### **2. Infrastructure Testing**
```bash
# Run comprehensive infrastructure tests
./run-infrastructure-tests.sh

# Test specific components
./run-infrastructure-tests.sh --test-type aws --verbose

# Production environment testing
./run-infrastructure-tests.sh --environment prod
```

## 📊 **Monitoring Deployment**

### **1. Deploy Monitoring Stack**
```bash
# Create monitoring namespace
kubectl create namespace monitoring

# Deploy Prometheus stack
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring

# Verify deployment
kubectl get pods -n monitoring
kubectl get services -n monitoring
```

### **2. Access Monitoring Interfaces**
```bash
# Port forward Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

# Port forward Prometheus
kubectl port-forward svc/monitoring-kube-prometheus-stack-prometheus -n monitoring 9090:9090

# Access in browser
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
```

### **3. Get Grafana Credentials**
```bash
# Get admin password
kubectl get secret --namespace monitoring monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

# Default login: admin / <password from above>
```

## 🔐 **Security Configuration**

### **1. AWS Credentials**
```bash
# Configure AWS CLI
aws configure

# Verify access
aws sts get-caller-identity

# Set up AWS secrets for Kubernetes
./kubernetes/dev/setup-aws-secrets.sh
```

### **2. JWT Configuration**
```bash
# Set JWT secret
export JWT_SECRET_KEY="your-secret-key"
export JWT_ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES="30"
```

### **3. Database Configuration**
```bash
# DynamoDB configuration
export AWS_REGION="us-west-2"
export DYNAMODB_TABLE_NAME="order-processor-table"
```

## 🧪 **Testing Deployment**

### **1. Health Checks**
```bash
# Check service health
curl http://localhost:8000/health  # User Service
curl http://localhost:8001/health  # Inventory Service
curl http://localhost:8002/health  # Order Service
curl http://localhost:8080/health  # API Gateway
```

### **2. Integration Tests**
```bash
# Run all integration tests
cd integration_tests
./run_all_tests.sh all

# Run specific service tests
./run_all_tests.sh user      # User service only
./run_all_tests.sh inventory # Inventory service only
./run_all_tests.sh order     # Order service only
./run_all_tests.sh smoke     # Health checks only
```

### **3. Performance Tests**
```bash
# Load testing with Apache Bench
ab -n 1000 -c 10 http://localhost:8080/health

# Memory profiling
python -m memory_profiler script.py
```

## 🔄 **Maintenance & Updates**

### **1. Regular Tasks**
```bash
# Update service versions
./scripts/update-services.sh

# Monitor resource usage
kubectl top pods -n order-processor
kubectl top nodes

# Check service logs
kubectl logs -n order-processor
```

### **2. Upgrade Procedures**
```bash
# Test changes in development first
./scripts/deploy.sh --type k8s --environment dev

# Review changes
terraform plan -var="environment=prod"

# Apply production updates
terraform apply -var="environment=prod"
```

### **3. Rollback Procedures**
```bash
# Rollback deployment
kubectl rollout undo deployment/[deployment-name] -n order-processor

# Check rollback status
kubectl rollout status deployment/[deployment-name] -n order-processor
```

## 🚨 **Troubleshooting**

### **1. Common Issues**
```bash
# Service not starting
kubectl describe pod [pod-name] -n order-processor

# Check service logs
kubectl logs [pod-name] -n order-processor

# Verify service endpoints
kubectl get endpoints -n order-processor
```

### **2. Debug Commands**
```bash
# Check pod events
kubectl describe pod [pod-name] -n order-processor

# Test service connectivity
kubectl exec -it [pod-name] -n order-processor -- curl http://[service-name]:[port]/health

# Check resource usage
kubectl top pods -n order-processor
```

## 📚 **Additional Resources**

- **Infrastructure**: [Terraform README](../terraform/README.md)
- **Monitoring**: [Monitoring README](../monitoring/README.md)
- **Kubernetes**: [Kubernetes README](../kubernetes/README.md)
- **Testing**: [Integration Tests README](../integration_tests/README.md)

## 🎯 **Deployment Checklist**

### **Pre-Deployment**
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] AWS credentials verified
- [ ] Infrastructure ready

### **Deployment**
- [ ] Services deployed successfully
- [ ] Health checks passing
- [ ] Integration tests running
- [ ] Monitoring stack deployed

### **Post-Deployment**
- [ ] All endpoints accessible
- [ ] Performance metrics normal
- [ ] Error rates acceptable
- [ ] Documentation updated
