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

## ☸️ **Kubernetes Deployment**

### **1. Local Kubernetes (Kind)**
```bash
# Deploy to local Kubernetes
./kubernetes/deploy.sh dev

# Access services
# Frontend: http://localhost:30004
# Gateway: http://localhost:30000
```

### **2. AWS EKS Production Deployment**

#### **Complete AWS EKS Deployment (Recommended)**
```bash
# Deploy everything: infrastructure + images + services
./scripts/aws-eks-deploy.sh

# This will:
# 1. Deploy AWS infrastructure (EKS, VPC, DynamoDB, ECR, LoadBalancer, Redis)
# 2. Build and push Docker images to ECR
# 3. Deploy services to EKS cluster
# 4. Create Kubernetes secrets automatically
```

#### **Step-by-Step AWS EKS Deployment**
```bash
# Step 1: Deploy AWS infrastructure only
./scripts/aws-eks-deploy.sh --infrastructure-only

# Step 2: Build and push Docker images only
./scripts/aws-eks-deploy.sh --images-only

# Step 3: Deploy to Kubernetes only (requires infrastructure and images)
./scripts/aws-eks-deploy.sh --k8s-only

# Step 4: Build and push specific services only
./scripts/aws-eks-deploy.sh --services user-service order-service
```

#### **AWS EKS Configuration**
```bash
# Configure kubectl for EKS (done automatically by script)
aws eks update-kubeconfig --region us-west-2 --name order-processor-prod-cluster

# Get LoadBalancer URL for integration tests
kubectl get services -n order-processor
# Look for gateway LoadBalancer EXTERNAL-IP

# Set environment variable for integration tests
export GATEWAY_HOST="your-loadbalancer-url.elb.us-west-2.amazonaws.com"
```

#### **Integration Testing on AWS EKS**
```bash
# Run integration tests against AWS deployment
cd integration_tests
export GATEWAY_HOST="your-loadbalancer-url.elb.us-west-2.amazonaws.com"
./run_all_tests.sh
```

#### **AWS EKS Cleanup**
```bash
# Destroy all AWS resources
./scripts/aws-eks-deploy.sh --destroy

# This will:
# 1. Delete EKS cluster and all associated resources
# 2. Delete VPC, subnets, and security groups
# 3. Delete DynamoDB tables
# 4. Delete ECR repositories
# 5. Delete LoadBalancer and Redis
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

### **1. Terraform Deployment (Automated)**

#### **Using Terraform Scripts (Recommended)**
```bash
# Deploy production infrastructure
cd terraform
./apply.sh prod

# Deploy development infrastructure
./apply.sh dev

# Destroy infrastructure
./destroy.sh prod
```

#### **Manual Terraform Deployment**
```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="environment=prod"

# Deploy production infrastructure
terraform apply -var="environment=prod"

# Deploy development infrastructure
terraform apply -var="environment=dev"
```

#### **Infrastructure Components**
```bash
# What gets deployed:
# - EKS cluster (t3.small instances, 2-3 nodes)
# - VPC with public/private subnets
# - DynamoDB tables (users, orders, inventory)
# - ECR repositories for Docker images
# - Application LoadBalancer for external access
# - ElastiCache Redis cluster
# - IAM roles and policies for EKS service accounts
# - Security groups and network ACLs
```

### **2. AWS EKS Architecture**

#### **Infrastructure Overview**
```
┌─────────────────────────────────────────────────────────────┐
│                    AWS EKS Cluster                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Node Group    │  │   Node Group    │  │ Node Group  │  │
│  │   (t3.small)    │  │   (t3.small)    │  │ (t3.small)  │  │
│  │                 │  │                 │  │             │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────┐ │  │
│  │ │User Service │ │  │ │Inventory    │ │  │ │Gateway   │ │  │
│  │ │             │ │  │ │Service      │ │  │ │          │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────┘ │  │
│  │                 │  │                 │  │             │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────┐ │  │
│  │ │Order Service│ │  │ │Auth Service │ │  │ │System    │ │  │
│  │ │             │ │  │ │             │ │  │ │Pods      │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────┘ │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ LoadBalancer    │
                    │ (External IP)   │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Internet      │
                    └─────────────────┘
```

#### **Security Architecture**
```bash
# IAM Roles for Service Accounts (IRSA)
# - Each service pod gets AWS permissions via IAM roles
# - OIDC provider links Kubernetes service accounts to AWS IAM roles
# - No hardcoded AWS credentials in pods

# Network Security
# - Private subnets for application pods
# - Public subnets only for LoadBalancer
# - Security groups restrict traffic between components

# Data Security
# - DynamoDB encryption at rest
# - Redis encryption in transit (optional)
# - Secrets managed via Kubernetes secrets
```

### **3. Infrastructure Testing**
```bash
# Run comprehensive infrastructure tests
./run-infrastructure-tests.sh

# Test specific components
./run-infrastructure-tests.sh --test-type aws --verbose

# Production environment testing
./run-infrastructure-tests.sh --environment prod

# AWS EKS specific tests
kubectl get nodes
kubectl get pods -n order-processor
kubectl get services -n order-processor
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

#### **AWS EKS Specific Issues**
```bash
# Pods stuck in Pending state
kubectl describe pod [pod-name] -n order-processor
# Check for: "Insufficient pods" or "No nodes available"

# Image pull errors
kubectl describe pod [pod-name] -n order-processor
# Check for: "ImagePullBackOff" or "ErrImagePull"
# Solution: Verify ECR repository exists and image is pushed

# IAM/OIDC authentication errors
kubectl logs [pod-name] -n order-processor
# Check for: "InvalidIdentityToken" or "AccessDenied"
# Solution: Verify OIDC provider and IAM role trust policy

# LoadBalancer not getting external IP
kubectl get services -n order-processor
# Check for: EXTERNAL-IP in <pending> state
# Solution: Wait 2-3 minutes for AWS to provision LoadBalancer
```

#### **General Kubernetes Issues**
```bash
# Service not starting
kubectl describe pod [pod-name] -n order-processor

# Check service logs
kubectl logs [pod-name] -n order-processor

# Verify service endpoints
kubectl get endpoints -n order-processor
```

### **2. Debug Commands**

#### **AWS EKS Debug Commands**
```bash
# Check cluster status
aws eks describe-cluster --name order-processor-prod-cluster --region us-west-2

# Check node group status
aws eks describe-nodegroup --cluster-name order-processor-prod-cluster --nodegroup-name order-processor-prod-nodes --region us-west-2

# Check IAM role trust policy
aws iam get-role --role-name order-processor-prod-k8s-sa-role

# Check OIDC provider
aws iam get-open-id-connect-provider --open-id-connect-provider-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):oidc-provider/oidc.eks.us-west-2.amazonaws.com/id/$(aws eks describe-cluster --name order-processor-prod-cluster --region us-west-2 --query cluster.identity.oidc.issuer --output text | cut -d'/' -f5)

# Check ECR repositories
aws ecr describe-repositories --region us-west-2
```

#### **General Debug Commands**
```bash
# Check pod events
kubectl describe pod [pod-name] -n order-processor

# Test service connectivity
kubectl exec -it [pod-name] -n order-processor -- curl http://[service-name]:[port]/health

# Check resource usage
kubectl top pods -n order-processor
kubectl top nodes

# Check AWS permissions
aws sts get-caller-identity
```

### **3. Common Solutions**

#### **Pod Capacity Issues**
```bash
# If getting "Too many pods" error:
# 1. Check current pod count per node
kubectl get pods -o wide --all-namespaces

# 2. Scale up node group (if using t3.micro)
aws eks update-nodegroup-config --cluster-name order-processor-prod-cluster --nodegroup-name order-processor-prod-nodes --scaling-config minSize=2,maxSize=5,desiredSize=3 --region us-west-2

# 3. Or upgrade to larger instances
# Edit terraform/eks.tf: instance_types = ["t3.small"]
```

#### **IAM Permission Issues**
```bash
# Fix AWS Console access
kubectl patch configmap aws-auth -n kube-system --patch '{"data":{"mapUsers":"- userarn: arn:aws:iam::ACCOUNT_ID:user/USERNAME\n  username: USERNAME\n  groups:\n  - system:masters"}}'

# Fix service account permissions
kubectl annotate serviceaccount order-processor-sa -n order-processor eks.amazonaws.com/role-arn=arn:aws:iam::ACCOUNT_ID:role/order-processor-prod-k8s-sa-role
```

#### **Network Connectivity Issues**
```bash
# Test LoadBalancer connectivity
curl -v http://your-loadbalancer-url.elb.us-west-2.amazonaws.com/health

# Check security groups
aws ec2 describe-security-groups --filters "Name=group-name,Values=*order-processor*" --region us-west-2

# Test internal service connectivity
kubectl exec -it [pod-name] -n order-processor -- nslookup gateway-service
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
- [ ] AWS credentials verified (`aws sts get-caller-identity`)
- [ ] Infrastructure ready
- [ ] ECR repositories created
- [ ] IAM roles and policies configured

### **AWS EKS Deployment**
- [ ] Terraform infrastructure deployed (`./terraform/apply.sh prod`)
- [ ] Docker images built and pushed to ECR (`./scripts/aws-eks-deploy.sh --images-only`)
- [ ] Kubernetes services deployed (`./scripts/aws-eks-deploy.sh --k8s-only`)
- [ ] LoadBalancer has external IP
- [ ] All pods running (`kubectl get pods -n order-processor`)
- [ ] Service endpoints accessible (`kubectl get services -n order-processor`)

### **Integration Testing**
- [ ] Gateway URL obtained from LoadBalancer
- [ ] Environment variable set (`export GATEWAY_HOST="your-loadbalancer-url"`)
- [ ] Integration tests passing (`./run_all_tests.sh`)
- [ ] Smoke tests passing
- [ ] Service health checks passing

### **Post-Deployment**
- [ ] All endpoints accessible
- [ ] Performance metrics normal
- [ ] Error rates acceptable
- [ ] Documentation updated
- [ ] AWS resources cleanup plan ready (`./scripts/aws-eks-deploy.sh --destroy`)
