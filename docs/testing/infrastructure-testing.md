# Infrastructure Testing

## Quick Commands

### Terraform
```bash
cd terraform
terraform validate
terraform plan -var="environment=dev"
terraform apply -var="environment=dev"
```

### Kubernetes
```bash
cd kubernetes
./scripts/k8s-manage.sh deploy
./scripts/k8s-manage.sh test
```

### AWS Resources
```bash
aws dynamodb list-tables
aws eks describe-cluster --name order-processor-dev
aws iam list-roles --query 'Roles[?contains(RoleName, `order-processor`)]'
```

### Docker
```bash
docker-compose up -d
docker-compose logs [service-name]
docker stats
```

### Monitoring
```bash
kubectl create namespace monitoring
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring
kubectl port-forward svc/monitoring-grafana 3000:80
```
