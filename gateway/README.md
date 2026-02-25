# 🚪 API Gateway

> High-performance Go-based API gateway with JWT authentication and intelligent request routing

## 🚀 Quick Start
- **Prerequisites**: Go 1.24+, Redis (optional)
- **Build & Test**: `./build.sh` (builds and runs tests)
- **Run Locally**: `./dev.sh run`
- **Deploy**: From repo root: `./docker/deploy.sh local deploy` (local) or `./docker/deploy.sh gateway deploy` (dev/AWS), or K8s (see [Docker](../docker/README.md), [Kubernetes](../kubernetes/README.md))
- **Example**: `curl http://localhost:8080/health`

## ✨ Key Features
- JWT authentication
- Intelligent request routing to backend services
- Security features (CORS, input validation, **IP block**)
- Production-ready with comprehensive testing

**IP block (SEC-011):** When Redis is available, the auth middleware checks for a per-IP block key before validating the token. Blocked IPs receive 403. After 5 failed logins (401 from POST /auth/login) in a 5-minute window (dev/test; production would use 1-day), the gateway sets `ip_block:<ip>` in Redis (TTL 5 min dev/test). Ops: manual block with `redis-cli SET ip_block:<ip> 1 EX 300`; unblock: key expires automatically, or `redis-cli DEL ip_block:<ip>`.

### Tracing IP block in gateway logs

Use gateway logs to debug why you get **401** instead of **403** after 5 wrong logins:

1. **Startup**  
   - `"Redis connection successful"` → Redis is used; IP block check and failed-login recording are active.  
   - `"Redis connection failed"` → Redis is nil; no IP block check and no recording; every request is proxied and you only see 401 from the auth service.

2. **Every request (auth middleware)**  
   - If Redis errors during `IsIPBlocked`: log `"IP block check failed, allowing request"` with `client_ip` and `error`. Request is allowed (fail-open).  
   - If IP is blocked: log `"Request from blocked IP"` and respond **403**.

3. **After proxying POST /auth/login**  
   - If backend returns **401**, gateway calls `RecordFailedLogin(clientIP)` (increment `login_fail:<ip>` with 5-min window dev/test, and if count ≥ 5 set `ip_block:<ip>`).  
   - If that Redis call fails: log `"RecordFailedLogin failed (non-fatal)"` with `client_ip` and `error`; client still gets 401.

**Code path:** `cmd/gateway/main.go` (Redis init) → `internal/middleware/auth.go` (IP block check then pass through) → `internal/api/server.go` `handleProxyRequest` (proxy to auth; on 401 call `redisService.RecordFailedLogin`) → next request from same IP hits middleware and gets 403 if block was set.

**Integration tests:** Full flow (init → 5 wrong logins → 403 → wait 5 min → login works again) is covered by `integration_tests/incident/test_ip_block.py`. Run via `./run_all_tests.sh incident` from `integration_tests`.

## 📁 Project Structure
```
gateway/
├── cmd/gateway/                # Application entry point
├── internal/                  # Private application code
│   ├── api/                   # HTTP server and routing
│   ├── config/                # Configuration
│   ├── middleware/            # Auth, rate limit, metrics, CORS, logging
│   └── services/              # Proxy, auth client, Redis, circuit breaker
├── pkg/                       # Public packages (logging, metrics, models, utils)
├── docker/                    # Docker configuration
├── build.sh                   # Build and test script
└── dev.sh                     # Development script
```

## 🔗 Quick Links
- [Design Documentation](../docs/design-docs/gateway-design.md)
- [Services Overview](../services/README.md)
- [API Documentation](http://localhost:8080/docs)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All core features implemented and tested
- **Last Updated**: February 2026

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and code.