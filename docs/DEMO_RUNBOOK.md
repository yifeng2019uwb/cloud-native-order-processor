# Demo Runbook

Quick steps to run and demo the Cloud-Native Order Processor.

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ and Python 3.11+ (if running services locally)
- AWS CLI configured (only for AWS/EKS demos)

## Start the system

### Option 1: Docker (recommended for demos)

```bash
# From repo root – build and run all services
./scripts/deploy-docker.sh -bd all

# Or using docker compose directly
cd docker
docker compose -f docker-compose.local.yml up -d
```

### Option 2: Local Kubernetes (Kind)

```bash
./kubernetes/deploy.sh dev
```

## Service URLs (Docker local)

| Service        | URL                     |
|----------------|-------------------------|
| Frontend       | http://localhost:3000   |
| API Gateway    | http://localhost:8080   |
| User Service   | http://localhost:8000   |
| Inventory      | http://localhost:8001   |
| Order Service  | http://localhost:8002   |
| Auth Service   | http://localhost:8003   |
| Insights       | http://localhost:8004   |

## Quick health check

```bash
curl -s http://localhost:8080/health   # Gateway
curl -s http://localhost:8000/health   # User
curl -s http://localhost:8001/health   # Inventory
curl -s http://localhost:8002/health   # Order
```

## Demo flow (happy path)

1. Open frontend: http://localhost:3000  
2. Register / log in (JWT via Auth Service).  
3. Use portfolio, orders, and insights from the UI.  
4. Optionally call gateway endpoints with a valid JWT for API demos.

## Logs and monitoring

- **Grafana (if running):** http://localhost:3001 (default user `admin` / `admin123`)  
- **Loki log query (by service):** e.g. `{service="user"} | json | request_id="<id>"`  
- **Prometheus (if running):** via proxy on port 9090.

## Stop

```bash
cd docker
docker compose -f docker-compose.local.yml down
```

For Kind:

```bash
kind delete cluster --name order-processor-dev
```
