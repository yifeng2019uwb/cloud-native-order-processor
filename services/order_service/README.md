# Order Service

A cloud-native order processing service for the Cloud Native Order Processor platform.

## Overview

The Order Service handles order creation, management, and processing for trading operations. It provides RESTful APIs for order lifecycle management including creation, retrieval, and status updates with integrated balance management.

## Features

- **Market Order Processing**: Buy and sell orders with real-time execution
- **Order Lifecycle Management**: Creation, validation, execution, completion
- **Balance Integration**: Automatic balance validation and transaction creation
- **Order History**: Complete order tracking and history
- **Status Management**: Real-time order status updates
- **Integration**: Seamless integration with User Service (balance) and Inventory Service (assets)

## Architecture

### **Order-Balance Integration**
The Order Service integrates with the User Service for balance management:

```
Order Creation Flow:
1. Validate user balance (via Balance DAO)
2. Create order record (Order DAO)
3. Create balance transaction (Balance DAO)
4. Update user balance
5. Return success/fail response
```

### **Market Order Types**
- **Market Buy**: Immediate purchase with balance validation
- **Market Sell**: Immediate sale with balance credit on execution
- **Limit Buy**: Future implementation (TODO)
- **Limit Sell**: Future implementation (TODO)

## API Endpoints

### **Order Management**
```
POST /orders                    - Create new order
GET  /orders/{id}              - Get order details
GET  /orders                    - List user orders
PUT  /orders/{id}/cancel        - Cancel order
GET  /orders/{id}/status        - Get order status
```

### **Health & Monitoring**
```
GET  /health                    - Health check
GET  /metrics                   - Service metrics
```

## Technology Stack

- **Framework**: FastAPI
- **Database**: DynamoDB (via common package)
- **Authentication**: JWT tokens (via API Gateway)
- **Integration**: User Service (balance), Inventory Service (assets)
- **Deployment**: Lambda/Kubernetes ready

## Development Status

🔄 **IN DEVELOPMENT**

### **Completed**
- ✅ Order entities and DAOs (common package)
- ✅ Balance integration design
- ✅ Database schema and relationships
- ✅ API model definitions

### **In Progress**
- 🔄 Order creation with balance validation
- 🔄 Order execution and completion
- 🔄 Order cancellation and refunds
- 🔄 API endpoint implementation

### **Planned**
- 📋 Limit order implementation
- 📋 Order hold/release mechanisms
- 📋 Advanced order types (stop-loss, take-profit)
- 📋 Order analytics and reporting

## Integration Points

### **User Service Integration**
- Balance validation before order creation
- Automatic balance transaction creation
- Real-time balance updates

### **Inventory Service Integration**
- Asset validation and pricing
- Asset availability checking
- Asset metadata retrieval

### **Common Package Dependencies**
- Order DAO for database operations
- Balance DAO for balance management
- Shared entities and exceptions
- Database connection management

## Development

This service is part of the larger Cloud Native Order Processor microservices architecture.

### **Local Development**
```bash
cd services/order_service
./build.sh
```

### **Testing**
```bash
pytest tests/ -v --cov=src
```

## License

MIT License