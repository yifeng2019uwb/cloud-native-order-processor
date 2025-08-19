# 🏗️ Infrastructure Management

> Manage AWS and Kubernetes infrastructure

## 🚀 Quick Start
```bash
# Validate environment
./validate-environment.sh

# Deploy infrastructure
./deploy.sh --type infra --environment dev

# Destroy resources
./destroy.sh --environment dev --force
```

## ☁️ AWS Infrastructure

```bash
# Deploy development infrastructure
./deploy.sh --type infra --environment dev

# Deploy production infrastructure
./deploy.sh --type infra --environment prod

# Or use Terraform directly
cd terraform/dev
terraform init && terraform plan && terraform apply
```

## ☸️ Kubernetes Infrastructure

```bash
# Create Kind cluster
kind create cluster --name order-processor

# Configure cluster
kind export kubeconfig --name order-processor

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

## 🔐 Security Management

```bash
# Update AWS credentials
./update-aws-credentials.sh

# Verify credentials
aws sts get-caller-identity

# Create service account
kubectl create serviceaccount order-processor-sa -n order-processor
```

## 🔍 Validation

```bash
# Check AWS connectivity
aws sts get-caller-identity
aws dynamodb list-tables

# Check Kubernetes health
kubectl cluster-info
kubectl get pods -n order-processor
```

## 🧹 Cleanup

```bash
# Destroy environment
./destroy.sh --environment dev --force

# Delete Kind cluster
kind delete cluster --name order-processor

# Clean up local resources
docker system prune -a
```

---

**Note**: For application deployment, see Build & Deploy guide.
