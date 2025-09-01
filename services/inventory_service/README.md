# 📦 Inventory Service

> FastAPI microservice for digital asset management, cryptocurrency data, and inventory operations

## 🚀 Quick Start
- **Prerequisites**: Python 3.11+, pip, virtual environment
- **Install**: `cd inventory_service && python -m pip install -e .`
- **Test**: `../build.sh --test-only inventory_service`
- **Run**: `python -m uvicorn src.main:app --reload --port 8001`

## ✨ Key Features
- **Digital Asset Catalog**: 98+ cryptocurrency assets with real-time pricing
- **CoinGecko Integration**: Live cryptocurrency data and price updates
- **Asset Management**: Asset listing, search, and detailed information
- **Inventory Operations**: Asset initialization, seeding, and status tracking
- **Public Access**: No authentication required for asset browsing

## 🔗 Quick Links
- [Services Overview](../README.md)
- [Build Script](../build.sh)
- [API Documentation](#api-endpoints)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All features implemented and tested
- **Last Updated**: August 20, 2025

## 🎯 Current Status

### ✅ **All Features Working**
- **Asset Catalog**: 98+ cryptocurrency assets with metadata
- **Real-time Pricing**: CoinGecko API integration for live prices
- **Search & Filtering**: Asset discovery and detailed information
- **Health Monitoring**: Service health checks and Prometheus metrics
- **Integration**: Working with API Gateway and other services

---

## 📁 Project Structure

```
inventory_service/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── api_models/             # API request/response models
│   │   └── inventory/         # Inventory models
│   │       ├── asset_list.py  # Asset list models
│   │       ├── asset_requests.py # Asset request models
│   │       └── asset_response.py # Asset response models
│   ├── controllers/            # Business logic controllers
│   │   ├── assets.py          # Asset operations logic
│   │   ├── health.py          # Health monitoring logic
│   │   └── dependencies.py    # Controller dependencies
│   ├── data/                  # Data initialization
│   │   └── init_inventory.py  # Inventory initialization
│   ├── services/              # External service integrations
│   │   └── fetch_coins.py     # CoinGecko API integration
│   ├── inventory_exceptions/   # Inventory-specific exceptions
│   │   └── exceptions.py      # Inventory exception definitions
│   ├── validation/            # Input validation and business rules
│   │   ├── business_validators.py # Business logic validation
│   │   └── field_validators.py # Field-level validation
│   ├── constants.py           # Service constants
│   └── metrics.py             # Metrics collection
├── tests/                     # Test suite
├── requirements.txt            # Python dependencies
└── setup.py                   # Package configuration
```

## 🔐 API Endpoints

### **Asset Management**
```bash
GET  /inventory/assets           # List all assets with pagination
GET  /inventory/assets/{id}      # Get specific asset details
GET  /inventory/assets/search    # Search assets by criteria
```

### **System**
```bash
GET  /health                     # Service health status
GET  /health/detailed            # Detailed health with external API status
GET  /metrics                    # Prometheus metrics
```

## 🏗️ Architecture

### **Database Design**
- **Single Table Design**: DynamoDB with composite PK/SK
- **Asset Entity**: PK=asset_id, SK=asset_id
- **Asset Status**: Active, Inactive, Suspended
- **Price Data**: Real-time integration with CoinGecko

### **External Integrations**
- **CoinGecko API**: Real-time cryptocurrency pricing
- **DynamoDB**: Asset data persistence via common package
- **Prometheus**: Metrics collection and monitoring

### **Data Flow**
```
1. Asset Initialization → Seed database with initial catalog
2. Price Updates → Periodic updates from CoinGecko API
3. Asset Queries → Fast retrieval from DynamoDB
4. Status Management → Asset availability tracking
```

## 🛠️ Technology Stack

- **Framework**: FastAPI with async support
- **Database**: AWS DynamoDB via common package
- **External API**: CoinGecko for cryptocurrency data
- **Validation**: Pydantic models and business validators
- **Testing**: pytest with comprehensive coverage
- **Monitoring**: Prometheus metrics and health checks
- **Documentation**: Swagger/OpenAPI automatic generation

## 🧪 Testing & Development

```bash
# Test this service
../build.sh --test-only inventory_service

# Test all services
../build.sh --test-only
```

## 🔍 Troubleshooting

```bash
../build.sh --check-prerequisites inventory_service
```

## 📚 Related Documentation

- **[Services Overview](../README.md)**: Complete services architecture
- **[Common Package](../common/README.md)**: Shared utilities and DAOs
- **[Exception Package](../exception/README.md)**: Error handling patterns
- **[Build Script](../build.sh)**: Automated build and testing

---

**Note**: This service provides public access to digital asset information and cryptocurrency data. For system-wide information, see the main services README.