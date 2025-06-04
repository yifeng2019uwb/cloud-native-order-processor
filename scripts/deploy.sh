#!/bin/bash

set -e

echo "Deploying infrastructure with Terraform..."
cd terraform
terraform init
terraform plan
terraform apply -auto-approve

echo "Deploying to Kubernetes..."
cd ../kubernetes
kubectl apply -f namespace.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

echo "Deployment completed!"