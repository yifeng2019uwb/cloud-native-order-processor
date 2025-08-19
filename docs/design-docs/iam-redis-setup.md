# IAM and Redis Setup Guide

## Overview

This guide covers the setup of IAM roles for service accounts (IRSA) and Redis integration for both local K8s and AWS EKS environments.

## Architecture

### Dev Environment (Local K8s)
- **IAM**: Uses IAM user with access keys for role assumption
- **Redis**: Local Redis pod in K8s cluster
- **Authentication**: Direct AWS credentials

### Prod Environment (AWS EKS)
- **IAM**: IRSA (IAM Roles for Service Accounts) with OIDC provider
- **Redis**: AWS ElastiCache Redis (cache.t3.micro - free tier eligible)
- **Authentication**: Web identity tokens via EKS OIDC

## IAM Configuration

### Application Role
The application role (`order-processor-{env}-application-service-role`) provides access to:

- **DynamoDB**: User, order, and inventory tables
- **S3**: Main and logs buckets
- **SQS**: Order processing queues
- **SNS**: Event notifications
- **ECR**: Container image access
- **Secrets Manager**: Database credentials
- **ElastiCache**: Redis cluster access (prod only)

### Role Assumption Methods

#### Dev Environment
```yaml
# Uses IAM user with access keys
env:
- name: AWS_ACCESS_KEY_ID
  value: "AKIA..."
- name: AWS_SECRET_ACCESS_KEY
  value: "..."
- name: AWS_ROLE_ARN
  value: "arn:aws:iam::ACCOUNT:role/order-processor-dev-application-service-role"
```

#### Prod Environment
```yaml
# Uses IRSA with service account annotation
metadata:
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::ACCOUNT:role/order-processor-prod-application-service-role"
```

## Redis Configuration

### Environment-Specific Setup

#### Dev Environment
```yaml
# Local Redis in K8s
env:
- name: REDIS_HOST
  value: "redis.order-processor.svc.cluster.local"
- name: REDIS_PORT
  value: "6379"
- name: REDIS_DB
  value: "0"
```

#### Prod Environment
```yaml
# AWS ElastiCache Redis
env:
- name: REDIS_ENDPOINT
  valueFrom:
    secretKeyRef:
      name: app-secrets
      key: redis-endpoint
- name: REDIS_PORT
  value: "6379"
- name: REDIS_DB
  value: "0"
```

### Redis Features
- **SSL/TLS**: Enabled in production for security
- **Connection Pooling**: Automatic connection management
- **Health Checks**: Built-in health monitoring
- **Token Blacklisting**: JWT token invalidation
- **Session Management**: User session storage
- **Caching**: General-purpose caching

## Setup Instructions

### 1. Deploy Infrastructure

#### Dev Environment
```bash
# Deploy local infrastructure
cd terraform
terraform apply -var="environment=dev"

# Deploy local K8s
cd ../kubernetes
./deploy.sh --environment dev
```

#### Prod Environment
```bash
# Deploy AWS infrastructure
cd terraform
terraform apply -var="environment=prod"

# Setup IRSA
cd ../kubernetes
./scripts/setup-irsa.sh --environment prod

# Deploy to EKS
./deploy.sh --environment prod
```

### 2. Verify Setup

#### Test IAM Access
```bash
# Run IAM and resource access tests
cd services/common/src/examples
python -m test_iam_assumption
```

#### Test Redis Connection
```python
from common.database.redis_connection import test_redis_connection, get_redis_health_status

# Test connection
if test_redis_connection():
    print("✅ Redis connection successful")

    # Get health status
    health = get_redis_health_status()
    print(f"Health: {health}")
else:
    print("❌ Redis connection failed")
```

### 3. Monitor and Troubleshoot

#### Check IAM Role
```bash
# Verify role assumption
aws sts get-caller-identity

# Check role permissions
aws iam get-role --role-name order-processor-prod-application-service-role
```

#### Check Redis Health
```bash
# Check Redis pod (dev)
kubectl get pods -n order-processor -l component=redis

# Check Redis logs
kubectl logs -n order-processor deployment/redis

# Check ElastiCache (prod)
aws elasticache describe-cache-clusters --cache-cluster-id order-processor-prod-redis
```

## Usage Examples

### Redis Caching
```python
from common.examples.redis_usage import RedisCache

# Create cache instance
cache = RedisCache("users")

# Cache user data
user_data = {"id": "123", "name": "John", "email": "john@example.com"}
cache.set("user:123", user_data, 3600)  # 1 hour TTL

# Retrieve cached data
cached_user = cache.get("user:123")
```

### Token Blacklisting
```python
from common.examples.redis_usage import TokenBlacklist
from datetime import datetime, timedelta

# Create blacklist instance
blacklist = TokenBlacklist()

# Blacklist a token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
expires_at = datetime.now() + timedelta(hours=1)
blacklist.blacklist_token(token, expires_at)

# Check if token is blacklisted
is_blacklisted = blacklist.is_blacklisted(token)
```

### Session Management
```python
from common.examples.redis_usage import SessionManager

# Create session manager
session_mgr = SessionManager()

# Create user session
session_data = {"name": "John", "role": "user", "preferences": {"theme": "dark"}}
session_id = session_mgr.create_session("user123", session_data)

# Get session data
session = session_mgr.get_session(session_id)

# Update session
session_mgr.update_session(session_id, {"last_activity": datetime.now().isoformat()})
```

## Security Considerations

### IAM Security
- **Least Privilege**: Each service has minimal required permissions
- **Role Separation**: Different roles for different environments
- **Audit Logging**: All AWS API calls are logged in CloudTrail

### Redis Security
- **SSL/TLS**: Encrypted connections in production
- **Network Isolation**: Redis in private subnets (prod)
- **No Authentication**: Simplified setup for personal project
- **Key Namespacing**: All keys are namespaced by environment

### Best Practices
1. **Never commit secrets** to version control
2. **Use IRSA** instead of access keys in production
3. **Monitor Redis memory usage** to prevent OOM
4. **Set appropriate TTLs** for cached data
5. **Use connection pooling** for Redis operations

## Troubleshooting

### Common Issues

#### IAM Role Assumption Fails
```bash
# Check OIDC provider
aws iam list-open-id-connect-providers

# Verify service account annotation
kubectl get serviceaccount order-processor-sa -n order-processor -o yaml

# Check pod identity
kubectl exec -it <pod-name> -n order-processor -- aws sts get-caller-identity
```

#### Redis Connection Fails
```bash
# Check Redis pod status
kubectl get pods -n order-processor -l component=redis

# Check Redis logs
kubectl logs -n order-processor deployment/redis

# Test Redis connectivity
kubectl exec -it <pod-name> -n order-processor -- redis-cli -h redis ping
```

#### ElastiCache Issues
```bash
# Check ElastiCache cluster status
aws elasticache describe-cache-clusters --cache-cluster-id order-processor-prod-redis

# Check security groups
aws ec2 describe-security-groups --group-ids <security-group-id>

# Test connectivity from EKS
kubectl exec -it <pod-name> -n order-processor -- telnet <redis-endpoint> 6379
```

### Debug Commands
```bash
# Check environment variables
kubectl exec -it <pod-name> -n order-processor -- env | grep -E "(REDIS|AWS)"

# Test AWS credentials
kubectl exec -it <pod-name> -n order-processor -- aws sts get-caller-identity

# Test Redis connection
kubectl exec -it <pod-name> -n order-processor -- python -c "
from common.database.redis_connection import test_redis_connection
print('Redis connection:', test_redis_connection())
"
```

## Cost Optimization

### Redis Costs
- **Dev**: $0 (local K8s Redis)
- **Prod**: ~$13/month (cache.t3.micro - free tier eligible)

### IAM Costs
- **IAM Roles**: Free
- **OIDC Provider**: Free
- **CloudTrail**: Free tier includes 5GB/month

### Monitoring
- **CloudWatch**: Monitor Redis metrics
- **X-Ray**: Trace Redis operations
- **Cost Explorer**: Track monthly costs

## Next Steps

1. **Implement token blacklisting** in auth services
2. **Add Redis caching** to improve performance
3. **Set up monitoring** and alerting
4. **Implement Redis clustering** for high availability
5. **Add Redis persistence** for data durability