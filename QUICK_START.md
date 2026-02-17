# 🚀 Quick Start - Cloud Native Order Processor

Multi-asset trading platform (microservices, JWT auth, DynamoDB, Redis).

- **Quick start:** Local deploy (Docker only) — for anyone who wants to try the project without AWS.
- **Regular development:** Dev deploy (AWS) — use Terraform-deployed infra and Docker deploy.

| Goal | What you need |
|------|----------------|
| **Local** (quick start) | Docker + Docker Compose |
| **Dev** (AWS) | AWS credentials + Terraform-deployed infra, then Docker deploy |

---

## Option A: Local deploy (quick start)

```bash
git clone https://github.com/yourusername/cloud-native-order-processor
cd cloud-native-order-processor
./docker/deploy.sh local deploy
```

- **Frontend:** http://localhost:3000  
- **Gateway:** http://localhost:8080  

Stop: `./docker/deploy.sh local destroy`

---

## Option B: Dev deploy (AWS, regular path)

Terraform must have deployed dev infrastructure first. Then:

```bash
./docker/deploy.sh all deploy
# or: ./docker/deploy.sh gateway deploy   (single service)
```

See [docker/README.md](docker/README.md). Unit tests: run `./dev.sh test` in each component (frontend, gateway, services/*).

---

## Test the API

With the app running (Option A or B):

```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/api/v1/auth/register -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "securepass123"}'
curl -X POST http://localhost:8080/api/v1/auth/login -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "securepass123"}'
```

(Use the token from login for protected endpoints like `GET /api/v1/portfolio`, `POST /api/v1/orders`.)

---

## Run tests

- **Integration:** `cd integration_tests && pip install -r requirements.txt && ./run_all_tests.sh all` (stack must be running; see [integration_tests/README.md](integration_tests/README.md)).
- **Unit:** In each component run `./dev.sh test` (e.g. `cd frontend && ./dev.sh test`). More: [scripts/README.md](scripts/README.md).

---

## Deployment summary

| Environment | Command |
|-------------|---------|
| Local | `./docker/deploy.sh local deploy` / `local destroy` |
| Dev (AWS) | `./docker/deploy.sh all deploy` or `<service> deploy` |
| Kubernetes | See [kubernetes/README.md](kubernetes/README.md) and Terraform docs. |

---

**Ready to explore?** Run `./docker/deploy.sh local deploy` and open http://localhost:3000.

More: [README.md](README.md), [docker/README.md](docker/README.md), [docs/](docs/).
