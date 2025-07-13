# Production Kubernetes Deployment

This directory contains the production Kubernetes configurations for deploying the Order Processor application to AWS EKS.

## Prerequisites

1. **AWS EKS cluster running**:
   ```bash
   # Verify cluster is running
   aws eks describe-cluster --name order-processor-prod --region us-east-1
   ```

2. **AWS ECR repositories created**:
   ```bash
   # Create ECR repositories
   aws ecr create-repository --repository-name order-processor-user-service
   aws ecr create-repository --repository-name order-processor-inventory-service
   aws ecr create-repository --repository-name order-processor-frontend
   ```

3. **AWS Load Balancer Controller installed**:
   ```bash
   # Verify ALB controller is installed
   kubectl get pods -n kube-system | grep aws-load-balancer-controller
   ```

4. **SSL Certificate in AWS Certificate Manager**:
   - Create certificate for your domain
   - Update `ingress.yaml` with certificate ARN

5. **AWS credentials configured**:
   - Update `secrets.yaml` with production AWS credentials
   - Base64 encode your credentials:
     ```bash
     echo -n "your-production-access-key" | base64
     echo -n "your-production-secret-key" | base64
     ```

## Deployment Process

### 1. Build and Push Docker Images
```bash
# Build images
docker-compose -f ../../docker/docker-compose.dev.yml build

# Tag for ECR
docker tag docker-user_service:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/order-processor-user-service:latest
docker tag docker-inventory_service:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/order-processor-inventory-service:latest
docker tag docker-frontend-dev:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/order-processor-frontend:latest

# Push to ECR
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/order-processor-user-service:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/order-processor-inventory-service:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/order-processor-frontend:latest
```

### 2. Update Configuration
- Edit `secrets.yaml` with your production secrets
- Update `ingress.yaml` with your domain and certificate ARN
- Set environment variables:
  ```bash
  export AWS_ACCOUNT_ID="your-account-id"
  export AWS_REGION="us-east-1"
  ```

### 3. Apply Base Configuration
```bash
kubectl apply -k ../base
```

### 4. Deploy to Production
```bash
kubectl apply -k .
```

### 5. Verify Deployment
```bash
kubectl get all -n order-processor
kubectl get ingress -n order-processor
```

## Access Points

After deployment, the services will be available at:

- **Frontend**: https://order-processor.yourdomain.com
- **API**: https://api.order-processor.yourdomain.com
- **User Service**: https://api.order-processor.yourdomain.com/auth
- **Inventory Service**: https://api.order-processor.yourdomain.com/inventory

## Configuration

### Environment Variables
- `ENVIRONMENT`: production
- `AWS_REGION`: us-east-1
- `JWT_SECRET`: From Kubernetes secrets

### Resources (Production)
- **User Service**: 512Mi-1Gi memory, 250m-500m CPU (2 replicas)
- **Inventory Service**: 512Mi-1Gi memory, 250m-500m CPU (2 replicas)
- **Frontend**: 128Mi-256Mi memory, 100m-200m CPU (2 replicas)

### Security Features
- **Non-root containers**: Run as user 1000
- **Read-only filesystem**: Enhanced security
- **No privilege escalation**: Restricted permissions
- **SSL/TLS**: HTTPS with certificate management
- **Secrets management**: Kubernetes secrets for sensitive data

### Load Balancer
- **AWS ALB**: Internet-facing load balancer
- **SSL termination**: HTTPS on port 443
- **Health checks**: Automatic health monitoring
- **Path-based routing**: Different paths to different services

## Monitoring and Troubleshooting

### Check Deployment Status
```bash
kubectl get deployments -n order-processor
kubectl describe deployment user-service -n order-processor
```

### Check Pod Status
```bash
kubectl get pods -n order-processor
kubectl describe pod <pod-name> -n order-processor
```

### Check Logs
```bash
kubectl logs <pod-name> -n order-processor
kubectl logs -f <pod-name> -n order-processor
```

### Check Services
```bash
kubectl get svc -n order-processor
kubectl describe svc user-service -n order-processor
```

### Check Ingress
```bash
kubectl get ingress -n order-processor
kubectl describe ingress order-processor-ingress -n order-processor
```

### Check Load Balancer
```bash
# Get ALB details
kubectl get ingress order-processor-ingress -n order-processor -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

## Scaling

### Horizontal Pod Autoscaling
```bash
# Create HPA for user service
kubectl autoscale deployment user-service -n order-processor --cpu-percent=70 --min=2 --max=10

# Create HPA for inventory service
kubectl autoscale deployment inventory-service -n order-processor --cpu-percent=70 --min=2 --max=10
```

### Manual Scaling
```bash
kubectl scale deployment user-service --replicas=5 -n order-processor
```

## Cleanup

To remove the production deployment:
```bash
kubectl delete -k .
```

## Cost Optimization

- **Spot instances**: Use spot instances for cost savings
- **Resource limits**: Set appropriate resource limits
- **Auto-scaling**: Implement HPA for dynamic scaling
- **Monitoring**: Use CloudWatch for cost monitoring

## Notes

- Uses ECR for container image storage
- Requires AWS Load Balancer Controller
- SSL certificate must be in the same region as EKS cluster
- Production secrets should be managed securely (consider AWS Secrets Manager)
- Consider implementing monitoring with Prometheus/Grafana
- Set up proper backup and disaster recovery procedures