# 📦 Inventory Service

> Asset management service for cryptocurrency catalog, market data, and public asset browsing

## 🚀 Quick Start
- **Prerequisites**: Python 3.11+, pip, virtual environment
- **Build & Test**: `./dev.sh` (builds and runs unit tests)
- **Deploy**: From repo root: `./docker/deploy.sh local deploy` (local) or `./docker/deploy.sh inventory_service deploy` (dev/AWS), or K8s (see [Docker](../../docker/README.md), [Kubernetes](../../kubernetes/README.md))
- **Integration Tests**: `./integration_tests/run_all_tests.sh`
- **Example**: `curl http://localhost:8001/health`

## ✨ Key Features
- Asset catalog management (98+ cryptocurrencies)
- Market data integration (CoinGecko API)
- Public asset browsing (no authentication required)
- Asset search and filtering
- Real-time pricing updates

## 📁 Project Structure
```
inventory_service/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── controllers/            # API controllers and endpoints
│   │   └── asset_controller.py # Asset management endpoints
│   ├── services/               # Business logic services
│   │   └── asset_service.py    # Asset management logic
│   ├── models/                 # Data models and schemas
│   │   └── asset_models.py     # Asset request/response models
│   ├── external/               # External API integration
│   │   └── coingecko_client.py # CoinGecko API client
│   └── utils/                  # Utility functions
│       └── data_processor.py   # Market data processing
├── tests/                      # Unit and integration tests
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
└── README.md                   # This file
```

## 🔗 Quick Links
- [Services Overview](../README.md)
- [API Documentation](http://localhost:8001/docs)
- [Common Package](../common/README.md)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - Asset management and market data working
- **Last Updated**: February 2026

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and guides.