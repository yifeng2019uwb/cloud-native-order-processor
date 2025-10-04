# 🚪 API Gateway

> High-performance Go-based API gateway with JWT authentication, role-based authorization, and intelligent request routing

## 🚀 Quick Start
- **Prerequisites**: Go 1.24+, Redis (optional)
- **Build & Test**: `./build.sh` (builds and runs tests)
- **Run Locally**: `./dev.sh run`
- **Deploy**: `./deploy.sh` (deploy to Docker or K8s)
- **Example**: `curl http://localhost:8080/health`

## ✨ Key Features
- JWT authentication and role-based authorization
- Intelligent request routing to backend services
- Security features (CORS, input validation)
- Production-ready with comprehensive testing

## 📁 Project Structure
```
gateway/
├── src/
│   ├── main.go                 # Application entry point
│   ├── handlers/               # HTTP handlers
│   │   ├── auth_handler.go     # Authentication endpoints
│   │   └── proxy_handler.go    # Request proxying
│   ├── middleware/             # Middleware components
│   │   ├── auth.go            # JWT authentication
│   │   ├── cors.go            # CORS handling
│   │   └── logging.go         # Request logging
│   ├── services/              # Business logic
│   │   └── auth_service.go    # Authentication service
│   └── config/                # Configuration
│       └── config.go          # App configuration
├── tests/                     # Unit and integration tests
├── docker/                    # Docker configuration
├── build.sh                   # Build and test script
├── dev.sh                     # Development script
└── deploy.sh                  # Deployment script
```

## 🔗 Quick Links
- [Design Documentation](../docs/design-docs/gateway-design.md)
- [Services Overview](../services/README.md)
- [API Documentation](http://localhost:8080/docs)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All core features implemented and tested
- **Last Updated**: January 8, 2025

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and code.