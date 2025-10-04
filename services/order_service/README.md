# 📋 Order Service

> Order processing service for trading operations, portfolio management, and order lifecycle

## 🚀 Quick Start
- **Prerequisites**: Python 3.11+, pip, virtual environment
- **Build & Test**: `./dev.sh` (builds and runs unit tests)
- **Deploy**: `./deploy.sh` (deploy to Docker or K8s)
- **Integration Tests**: `./integration_tests/run_all_tests.sh`
- **Example**: `curl http://localhost:8002/health`

## ✨ Key Features
- Order creation and processing (buy/sell)
- Portfolio management and calculations
- Order lifecycle management
- Atomic transactions with distributed locking
- Real-time portfolio updates

## 📁 Project Structure
```
order_service/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── controllers/            # API controllers and endpoints
│   │   ├── order_controller.py # Order management endpoints
│   │   ├── portfolio_controller.py # Portfolio endpoints
│   │   └── create_order.py     # Order creation endpoints
│   ├── services/               # Business logic services
│   │   ├── order_service.py    # Order processing logic
│   │   └── portfolio_service.py # Portfolio calculation logic
│   ├── models/                 # Data models and schemas
│   │   ├── order_models.py     # Order request/response models
│   │   └── portfolio_models.py # Portfolio response models
│   ├── validation/             # Input validation
│   │   └── business_validators.py # Business rule validators
│   └── dependencies.py         # Dependency injection
├── tests/                      # Unit and integration tests
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
└── README.md                   # This file
```

## 🔗 Quick Links
- [Services Overview](../README.md)
- [API Documentation](http://localhost:8002/docs)
- [Common Package](../common/README.md)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - Order processing and portfolio management working
- **Last Updated**: January 8, 2025

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and guides.