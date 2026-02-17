# Base Kubernetes Configuration

This directory contains the base Kubernetes configurations that are shared across all environments (local and production).

## Contents

- **namespace.yaml**: Defines the `order-processor` namespace
- **service-account.yaml**: Defines the service account and Kubernetes RBAC (Role/RoleBinding) for in-cluster permissions
- **kustomization.yaml**: Kustomize configuration for base resources

## Usage

### Apply base configuration:
```bash
kubectl apply -k .
```

### View base resources:
```bash
kubectl get all -n order-processor
```

## Structure

```
base/
├── namespace.yaml          # Shared namespace
├── service-account.yaml    # Service account + K8s RBAC
├── kustomization.yaml      # Kustomize config
└── README.md              # This file
```

## Notes

- These resources are shared between local (Kind) and production (AWS EKS) environments
- Environment-specific configurations are in `../local/` and `../prod/` directories
- Use Kustomize to manage and apply these configurations