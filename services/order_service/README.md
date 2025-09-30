# 📋 Order Service

> FastAPI microservice for order processing, trading operations, and portfolio management

## 🚀 Quick Start
- **Prerequisites**: Python 3.11+, pip, virtual environment
- **Install**: `cd order_service && python -m pip install -e .`
- **Test**: `python -m pytest`
- **Run**: `python -m uvicorn src.main:app --reload --port 8002`

## ✨ Key Features
- **Market Order Processing**: Buy and sell orders with real-time execution
- **Order Lifecycle Management**: Creation, validation, execution, and completion
- **Balance Integration**: Automatic balance validation and transaction creation
- **Portfolio Management**: Real-time portfolio calculation with market values
- **Asset Balance Tracking**: Individual asset balance management and history

## 🔗 Quick Links
- [Services Overview](../README.md)
- [Build Script](../build.sh)
- [API Documentation](#api-endpoints)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All features implemented and tested
- **Last Updated**: August 20, 2025

## 🎯 Current Status

### ✅ **All Features Working**
- **Order Management**: Order creation, retrieval, and status updates
- **Trading Operations**: Market buy/sell orders with balance validation
- **Portfolio Tracking**: Real-time portfolio calculation and asset balances
- **Integration**: Working with User Service and Inventory Service
- **Testing**: Comprehensive test coverage with end-to-end validation

---

## 📁 Project Structure

```
order_service/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── api_models/             # API request/response models
│   │   ├── asset.py           # Asset balance models
│   │   ├── order.py           # Order request/response models
│   │   └── shared/            # Shared models
│   │       └── common.py      # Common model utilities
│   ├── controllers/            # Business logic controllers
│   │   ├── asset_balance.py   # Asset balance operations
│   │   ├── asset_transaction.py # Asset transaction operations
│   │   ├── create_order.py    # Order creation logic
│   │   ├── get_order.py       # Order retrieval logic
│   │   ├── list_orders.py     # Order listing logic
│   │   ├── portfolio.py       # Portfolio calculations
│   │   ├── health.py          # Health check controller
│   │   └── dependencies.py    # Controller dependencies
│   ├── order_exceptions/       # Order-specific exceptions
│   │   └── exceptions.py      # Order exception definitions
│   ├── services/              # Business services
│   ├── utils/                 # Utility functions
│   └── validation/            # Input validation and business rules
│       ├── business_validators.py # Business logic validation
│       └── field_validators.py # Field-level validation
├── tests/                     # Test suite
├── requirements.txt            # Python dependencies
└── setup.py                   # Package configuration
```

## 🔐 API Endpoints

### **Order Management**
```bash
POST /orders                    # Create new order
GET  /orders/{id}              # Get order details
GET  /orders                    # List user orders
```

### **Asset Management**
```bash
GET  /assets/{asset_id}/balance # Get user asset balance
GET  /assets/balances           # Get all user asset balances
GET  /assets/{asset_id}/transactions # Get asset transaction history
```

### **Portfolio Management**
```bash
GET  /portfolio/{username}      # Get user portfolio with market values
```

### **System**
```bash
GET  /health                    # Service health status
GET  /health/ready              # Readiness check
GET  /health/live               # Liveness check
GET  /internal/metrics          # Prometheus metrics (internal monitoring)
```

## 🏗️ Architecture

### **Order-Balance Integration**
```
Order Creation Flow:
1. Validate user balance (via Balance DAO)
2. Create order record (Order DAO)
3. Create balance transaction (Balance DAO)
4. Update user balance
5. Create asset balance/transaction records
6. Return success/fail response
```

### **Market Order Types**
- **Market Buy**: Immediate purchase with balance validation
- **Market Sell**: Immediate sale with asset balance validation
- **Limit Buy**: Future implementation
- **Limit Sell**: Future implementation

### **Integration Points**
- **User Service**: Balance validation and transaction management
- **Inventory Service**: Asset information and market pricing
- **API Gateway**: Authentication and request routing

## 🛠️ Technology Stack

- **Framework**: FastAPI with async support
- **Database**: AWS DynamoDB via common package
- **Authentication**: JWT tokens via API Gateway
- **Validation**: Pydantic models and business validators
- **Testing**: pytest with comprehensive coverage
- **Monitoring**: Prometheus metrics, middleware tracking, and health checks
- **Integration**: User Service and Inventory Service APIs
- **Observability**: Request correlation, performance metrics, and business metrics

## 🧪 Testing & Development

```bash
# Test this service
../build.sh --test-only order_service

# Test all services
../build.sh --test-only
```

## 🔍 Troubleshooting

```bash
../build.sh --check-prerequisites order_service
```

## 📚 Related Documentation

- **[Services Overview](../README.md)**: Complete services architecture
- **[Common Package](../common/README.md)**: Shared utilities and DAOs
- **[User Service](../user_service/README.md)**: Balance management integration
- **[Inventory Service](../inventory_service/README.md)**: Asset information
- **[Build Script](../build.sh)**: Automated build and testing

---

**Note**: This service provides complete order processing and portfolio management functionality. For system-wide information, see the main services README.