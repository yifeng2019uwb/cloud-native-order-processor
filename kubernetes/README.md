# Kubernetes Deployment Package

This directory contains Kubernetes configurations for deploying the Order Processor application to different environments.

## Structure

```
kubernetes/
├── base/                    # Shared base configurations
│   ├── namespace.yaml       # Common namespace
│   ├── service-account.yaml # Service account + RBAC
│   ├── kustomization.yaml   # Base kustomize config
│   └── README.md           # Base documentation
├── local/                   # Local development (Kind)
│   ├── deployment.yaml     # Local deployments
│   ├── service.yaml        # NodePort services
│   ├── secrets.yaml        # Local secrets
│   ├── values.yaml         # Local configuration
│   ├── kustomization.yaml  # Local kustomize config
│   └── README.md           # Local deployment guide
├── prod/                    # Production (AWS EKS)
│   ├── deployment.yaml     # Production deployments
│   ├── service.yaml        # ClusterIP services
│   ├── ingress.yaml        # AWS ALB ingress
│   ├── secrets.yaml        # Production secrets
│   ├── values.yaml         # Production configuration
│   ├── kustomization.yaml  # Production kustomize config
│   └── README.md           # Production deployment guide
├── scripts/                 # Deployment automation
│   ├── deploy-local.sh     # Deploy to local cluster
│   ├── deploy-prod.sh      # Deploy to production
│   ├── cleanup.sh          # Cleanup deployments
│   └── port-forward.sh     # Port forwarding utilities
└── README.md               # This file
```

## Quick Start

### Local Development (Kind)

1. **Create Kind cluster**:
   ```bash
   kind create cluster --name order-processor
   ```

2. **Deploy to local**:
   ```bash
   ./scripts/deploy-local.sh
   ```

3. **Access services**:
   - Frontend: http://localhost:30000
   - User Service: http://localhost:30001
   - Inventory Service: http://localhost:30002

### Production (AWS EKS)

1. **Set environment variables**:
   ```bash
   export AWS_ACCOUNT_ID="your-account-id"
   export AWS_REGION="us-east-1"
   ```

2. **Deploy to production**:
   ```bash
   ./scripts/deploy-prod.sh
   ```

3. **Access services**:
   - Frontend: https://order-processor.yourdomain.com
   - API: https://api.order-processor.yourdomain.com

## Prerequisites

### Local Development
- [Docker](https://docs.docker.com/get-docker/)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

### Production
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- AWS EKS cluster
- AWS ECR repositories
- SSL certificate in AWS Certificate Manager

## Configuration

### Environment-Specific Settings

| Setting | Local | Production |
|---------|-------|------------|
| Replicas | 1 | 2 |
| Resources | 128Mi-256Mi | 512Mi-1Gi |
| Service Type | NodePort | ClusterIP |
| Load Balancer | None | AWS ALB |
| SSL | No | Yes |
| Image Source | Local Docker | AWS ECR |

### Secrets Management

Both environments require AWS credentials for DynamoDB access:

```bash
# Generate base64 encoded credentials
echo -n "your-access-key" | base64
echo -n "your-secret-key" | base64

# Update secrets.yaml files
# local/secrets.yaml
# prod/secrets.yaml
```

## Deployment Scripts

### `deploy-local.sh`
- Builds Docker images
- Loads images into Kind cluster
- Deploys to local environment
- Shows access URLs

### `deploy-prod.sh`
- Builds and tags Docker images
- Pushes to AWS ECR
- Deploys to production environment
- Shows ingress status

### `cleanup.sh`
- Removes deployments
- Usage: `./cleanup.sh [local|prod|all]`

## Troubleshooting

### Common Issues

1. **Images not found**:
   ```bash
   # Rebuild and reload images
   docker-compose -f ../docker/docker-compose.dev.yml build
   kind load docker-image docker-user_service:latest --name order-processor
   ```

2. **Secrets not configured**:
   ```bash
   # Check secrets
   kubectl get secrets -n order-processor
   kubectl describe secret aws-credentials -n order-processor
   ```

3. **Services not accessible**:
   ```bash
   # Check service status
   kubectl get svc -n order-processor
   kubectl describe svc user-service -n order-processor
   ```

### Useful Commands

```bash
# Check deployment status
kubectl get all -n order-processor

# View logs
kubectl logs <pod-name> -n order-processor

# Describe resources
kubectl describe pod <pod-name> -n order-processor
kubectl describe svc <service-name> -n order-processor

# Port forward (if needed)
kubectl port-forward svc/user-service 8000:8000 -n order-processor
```

## Development Workflow

1. **Local Development**:
   - Use Docker for rapid development
   - Use Kind for Kubernetes testing
   - Test integration with local deployment

2. **Production Deployment**:
   - Build and test locally first
   - Deploy to production when ready
   - Monitor deployment status

## Security Notes

- Production uses non-root containers
- Secrets are stored in Kubernetes secrets
- SSL/TLS enabled in production
- Network policies can be added for additional security

## Cost Optimization

- Local development is free (Kind)
- Production uses appropriate resource limits
- Consider spot instances for cost savings
- Monitor usage with CloudWatch