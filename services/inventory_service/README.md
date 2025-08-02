# Inventory Service

A microservice responsible for managing digital assets, cryptocurrency data, and inventory operations in the cloud-native order processor system.

## Features

### Asset Management
- Digital asset catalog with real-time pricing
- Cryptocurrency data integration via CoinGecko API
- Asset metadata and status tracking
- Bulk asset operations

### Data Integration
- Real-time cryptocurrency price updates
- Historical price data tracking
- Asset availability status
- Market data aggregation

### Inventory Operations
- Asset listing and search
- Asset detail retrieval
- Inventory initialization and seeding
- Asset status management

## API Endpoints

### Asset Management
- `GET /inventory/assets` - List all assets with pagination
- `GET /inventory/assets/{asset_id}` - Get specific asset details
- `GET /inventory/assets/search` - Search assets by criteria

### Health & Monitoring
- `GET /health` - Service health status
- `GET /health/detailed` - Detailed health with external API status
- `GET /metrics` - Prometheus metrics

## Architecture

### Database Design
- **Single Table Design**: Uses DynamoDB with composite PK/SK
- **Asset Entity**: PK=asset_id, SK=asset_id
- **Asset Status**: Active, Inactive, Suspended
- **Price Data**: Real-time integration with CoinGecko

### External Integrations
- **CoinGecko API**: Real-time cryptocurrency pricing
- **DynamoDB**: Asset data persistence
- **Prometheus**: Metrics collection

### Data Flow
1. **Asset Initialization**: Seeds database with initial asset catalog
2. **Price Updates**: Periodic updates from CoinGecko API
3. **Asset Queries**: Fast retrieval from DynamoDB
4. **Status Management**: Asset availability tracking

## Technology Stack

- **Framework**: FastAPI
- **Database**: DynamoDB (AWS)
- **External API**: CoinGecko for cryptocurrency data
- **Validation**: Pydantic
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Monitoring**: Prometheus metrics
- **Documentation**: Swagger/OpenAPI

## Development Status

### ✅ Completed
- Asset entity and DAO implementation
- CoinGecko API integration
- Asset listing and detail endpoints
- Two-layer validation strategy
- Comprehensive test coverage
- Health checks and metrics
- Inventory initialization system

### 🚧 In Progress
- Enhanced asset search functionality
- Price history tracking
- Asset categorization features

### 📋 Planned
- Real-time price websocket updates
- Asset analytics and reporting
- Bulk asset operations
- Advanced filtering and sorting
- Asset recommendation system

## Quick Start

### Prerequisites
- Python 3.11+
- AWS credentials configured
- DynamoDB table created
- Internet access for CoinGecko API

### Installation
```bash
cd services/inventory_service
pip install -r requirements.txt
pip install -e .
```

### Running Tests
```bash
./build.sh inventory_service
```

### Running Locally
```bash
cd src
uvicorn main:app --reload --port 8002
```

### Environment Variables
```bash
AWS_REGION=us-west-2
DYNAMODB_TABLE_NAME=order-processor-table
COINGECKO_API_URL=https://api.coingecko.com/api/v3
LOG_LEVEL=INFO
```

## API Documentation

Once the service is running, visit:
- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## Testing

### Test Coverage
- Unit tests for all controllers
- Integration tests for database operations
- Validation tests for API models
- External API integration tests

### Running Specific Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/controllers/test_assets.py
```

## Health Checks

- `GET /health` - Basic service health
- `GET /health/detailed` - Health with CoinGecko API status

## Metrics

The service exposes Prometheus metrics at `/metrics`:
- Request counts and durations
- Database operation metrics
- External API call metrics
- Asset operation metrics

## Error Handling

### Validation Errors
- Field validation at API model level
- Business validation at controller level
- Consistent error response format

### External API Errors
- CoinGecko API failure handling
- Rate limiting and retry logic
- Graceful degradation

### Database Errors
- Connection error handling
- Query optimization
- Data consistency checks

## Data Models

### Asset Entity
```python
class Asset(BaseModel):
    asset_id: str
    symbol: str
    name: str
    current_price: Decimal
    market_cap: Optional[Decimal]
    volume_24h: Optional[Decimal]
    price_change_24h: Optional[Decimal]
    status: AssetStatus
    created_at: datetime
    updated_at: datetime
```

### Asset Status
- **ACTIVE**: Available for trading
- **INACTIVE**: Temporarily unavailable
- **SUSPENDED**: Suspended from trading

## Contributing

1. Follow the established validation strategy
2. Add tests for new features
3. Update documentation
4. Ensure code coverage remains above 60%
5. Handle external API failures gracefully

## Dependencies

### Common Package
- Entities: Asset
- DAOs: AssetDAO
- Database: DynamoDB connection and health checks
- Validation: Field and business validators
- Exceptions: Custom exception classes

### External Dependencies
- FastAPI for web framework
- Pydantic for data validation
- boto3 for AWS services
- httpx for HTTP client
- prometheus-client for metrics

## Integration Points

### Order Service
- Provides asset information for order validation
- Supplies current prices for order calculations
- Validates asset availability

### User Service
- Provides asset portfolio information
- Supplies asset details for user holdings

### Gateway
- Handles routing and load balancing
- Provides unified API access

## Performance Considerations

### Caching Strategy
- Asset data caching for frequently accessed items
- Price data caching with TTL
- Database query optimization

### Scalability
- Horizontal scaling support
- Database connection pooling
- External API rate limiting

## Security

### Input Validation
- Comprehensive field validation
- SQL injection prevention
- XSS protection

### API Security
- Rate limiting
- Request size limits
- Error message sanitization

## Monitoring and Alerting

### Key Metrics
- API response times
- Database query performance
- External API availability
- Error rates and types

### Alerting
- Service health monitoring
- External API failure alerts
- Performance degradation alerts