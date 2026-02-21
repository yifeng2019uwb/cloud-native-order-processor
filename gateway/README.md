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
- Security features (CORS, input validation)
- Production-ready with comprehensive testing

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