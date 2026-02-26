# 🚪 API Gateway

> Go-based API gateway: single entry point, JWT auth, request routing to backend services, rate limiting, and security (CORS, IP block).

## 🚀 Quick Start

- **Prerequisites**: Go 1.24+, Redis (optional; enables rate limiting and IP block)
- **Build & Test**: `./build.sh`
- **Run Locally**: `./dev.sh run`
- **Deploy**: From repo root: `./docker/deploy.sh local deploy` or `./docker/deploy.sh gateway deploy`, or K8s ([Docker](../docker/README.md), [Kubernetes](../kubernetes/README.md))
- **Health**: `curl http://localhost:8080/health`

## ✨ Main Features

- **Reverse proxy & routing** — Single entry point for all APIs. Routes `/api/v1/*` to backend services (auth, user, inventory, order, portfolio, balance, assets, insights, cny). Configurable service URLs via env (e.g. `USER_SERVICE_URL`, `AUTH_SERVICE_URL`).
- **JWT authentication** — Validates JWT on protected routes; public routes (e.g. login, register, GET assets) skip token check. Role-based access where required.
- **Rate limiting** — Redis-based per-IP rate limit when Redis is available; configurable via `GATEWAY_RATE_LIMIT` (requests per minute).
- **Security** — CORS, IP block (SEC-011) when Redis is available (see below), request logging, panic recovery.
- **Observability** — Prometheus metrics at `/metrics`, health at `/health` (reports Redis status).

## IP block (SEC-011)

When Redis is available, the auth middleware checks a per-IP block key before validating the token. After 5 failed logins (401 from POST `/auth/login`) in the window, the gateway sets the block; subsequent requests from that IP get **403**. Block and failure-count TTL match so when the block expires the count is removed (fresh start).  
**Defaults**: 300s (5 min) for dev/test. **Production**: set `GATEWAY_BLOCK_DURATION_SECONDS=86400` and `GATEWAY_FAILED_LOGIN_WINDOW_SECONDS=86400` for 24h.  
**Ops**: Manual block `redis-cli SET ip_block:<ip> 1 EX 300` (or `EX 86400` for 24h); unblock `redis-cli DEL ip_block:<ip> login_fail:<ip>` (clear both or the next 401 re-blocks).  
**Troubleshooting**: See [Failed-login burst runbook](../docs/runbooks/failed-login-burst.md) and [integration_tests/incident/README.md](../integration_tests/incident/README.md).

## 📁 Project Structure

```
gateway/
├── cmd/gateway/                # Entry point
├── internal/                   # Server, config, middleware, proxy, Redis
├── pkg/                        # Logging, metrics, models, constants
├── build.sh, dev.sh
└── docker/
```

## 🔗 Quick Links

- [Gateway design](../docs/design-docs/gateway-design.md)
- [Services overview](../services/README.md)
- [Failed-login runbook](../docs/runbooks/failed-login-burst.md) (IP block ops)
- API docs: http://localhost:8080/docs (when running)

## 📊 Status

- **Status**: ✅ Production ready — core features implemented and tested
- **Last Updated**: Feb 2026
