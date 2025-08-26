# Docker Service Deployment Script

Simple script to deploy, restart, and manage CNOP Docker services.

## Quick Start

```bash
# Deploy auth service (rebuild + start)
./deploy.sh auth deploy

# Restart all services
./deploy.sh all restart

# Check status of all services
./deploy.sh all status

# View logs for user service
./deploy.sh user logs
```

## Available Commands

### Services
- `auth` - Auth service
- `user` - User service
- `inventory` - Inventory service
- `order` - Order service
- `all` - All services

### Actions
- `deploy` - Rebuild and deploy service (full redeploy)
- `restart` - Restart service without rebuild
- `stop` - Stop service
- `start` - Start service
- `logs` - Show service logs
- `status` - Show service status

## Examples

```bash
# Deploy specific service
./deploy.sh auth deploy    # Deploy auth service
./deploy.sh user deploy    # Deploy user service

# Manage all services
./deploy.sh all deploy     # Deploy all services
./deploy.sh all restart    # Restart all services
./deploy.sh all stop       # Stop all services
./deploy.sh all start      # Start all services

# Monitor services
./deploy.sh all status     # Show all services status
./deploy.sh auth logs      # Show auth service logs
```

## What Deploy Does

The `deploy` action:
1. Stops existing container
2. Removes old container
3. Rebuilds Docker image (no cache)
4. Starts new container
5. Waits for health check
6. Reports success/failure

## Health Checks

The script waits for services to become healthy before reporting success. If a service fails to become healthy, it shows the logs and exits with an error.

## Prerequisites

- Docker and Docker Compose must be installed
- Must be run from the `docker/` directory
- Services must have health check endpoints at `/health`
