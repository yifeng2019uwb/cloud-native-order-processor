# 🏗️ Order Processor Infrastructure

## 🎯 **Infrastructure Overview**

This directory contains Terraform configurations for deploying the Cloud Native Order Processor infrastructure across different environments.

## 🚀 **Environment Strategy**

### **Development Environment** 🏠
- **Purpose**: Local development and testing
- **Components**: Local FastAPI services + DynamoDB
- **Cost**: Minimal (~$5-10/month for DynamoDB)
- **Deployment**: Local Kubernetes (Kind) or Docker Compose

### **Production Environment** ☁️
- **Purpose**: Full-scale production deployment
- **Components**: EKS + Kubernetes + DynamoDB + Monitoring
- **Cost**: ~$80/month for full infrastructure
- **Deployment**: AWS EKS with production-grade monitoring

## 🏗️ **Infrastructure Components**

### **Core Infrastructure**
- **VPC**: Custom VPC with public/private subnets
- **EKS Cluster**: Managed Kubernetes cluster
- **DynamoDB**: Serverless database for user data and orders
- **ECR**: Container registry for Docker images
- **IAM**: Service accounts and role-based access control

### **Monitoring & Observability**
- **Prometheus**: Metrics collection and storage
- **Grafana**: Dashboards and visualization
- **Loki**: Log aggregation and querying
- **AlertManager**: Alert routing and notification

### **Security & Compliance**
- **VPC Security Groups**: Network-level security
- **IAM Policies**: Least-privilege access control
- **Secrets Management**: Secure credential storage
- **Network Policies**: Kubernetes network security

## 🚀 **Quick Start**

### **1. Prerequisites**
```bash
# Install required tools
brew install terraform awscli kubectl

# Configure AWS credentials
aws configure

# Verify access
aws sts get-caller-identity
```

### **2. Deploy Development Environment**
```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Deploy dev environment
terraform apply -var="environment=dev"

# Access services
# Local services will be available on standard ports
```

### **3. Deploy Production Environment**
```bash
# Deploy production infrastructure
terraform apply -var="environment=prod"

# Configure kubectl for EKS
aws eks update-kubeconfig --region us-west-2 --name order-processor-prod

# Deploy applications
./kubernetes/scripts/deploy-prod.sh
```

## 🧪 **Infrastructure Testing**

### **Run All Infrastructure Tests**
```bash
# Comprehensive infrastructure validation
./run-infrastructure-tests.sh

# Test specific components
./run-infrastructure-tests.sh --test-type aws --verbose

# Production environment testing
./run-infrastructure-tests.sh --environment prod
```

### **Test Categories**
- **AWS Resources**: DynamoDB, EKS, VPC, IAM
- **Kubernetes**: Cluster connectivity, service accounts
- **Security**: IAM policies, network policies
- **Monitoring**: Prometheus, Grafana, Loki setup

## 📊 **Cost Management**

### **Development Environment**
- **DynamoDB**: ~$5-10/month (pay-per-use)
- **Total**: ~$5-10/month

### **Production Environment**
- **EKS**: ~$40/month (3 nodes)
- **DynamoDB**: ~$20/month (higher usage)
- **Monitoring**: ~$15/month (Prometheus stack)
- **Other**: ~$5/month (VPC, IAM, etc.)
- **Total**: ~$80/month

### **Cost Optimization Tips**
- Use spot instances for non-critical workloads
- Implement auto-scaling based on demand
- Monitor DynamoDB read/write capacity
- Use S3 lifecycle policies for log retention

## 🔧 **Configuration Management**

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

### **Customization**
- **VPC CIDR**: Configure in `variables.tf`
- **Cluster Size**: Adjust node count in `eks.tf`
- **Database**: Modify DynamoDB configuration in `dynamodb.tf`
- **Monitoring**: Customize Prometheus stack in monitoring directory

## 🚨 **Security Considerations**

### **Network Security**
- Private subnets for database and application services
- Public subnets only for load balancers
- Security groups with minimal required access

### **Access Control**
- IAM roles with least-privilege permissions
- Service accounts for Kubernetes applications
- Secrets management for sensitive data

### **Compliance**
- VPC flow logs for network monitoring
- CloudTrail for API call logging
- Config rules for resource compliance

## 📚 **Additional Resources**

- **Infrastructure Tests**: [infrastructure-tests/README.md](infrastructure-tests/README.md)
- **Kubernetes Deployment**: [../kubernetes/README.md](../kubernetes/README.md)
- **Monitoring Setup**: [../monitoring/README.md](../monitoring/README.md)
- **Service Deployment**: [../scripts/README.md](../scripts/README.md)

## 🔄 **Maintenance & Updates**

### **Regular Tasks**
- Update Terraform and provider versions
- Review and rotate access keys
- Monitor cost and usage patterns
- Update security policies

### **Upgrade Procedures**
- Test changes in development first
- Use Terraform plan to review changes
- Backup critical data before major updates
- Monitor system health during upgrades
