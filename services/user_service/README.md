# User Service

A microservice responsible for user management, authentication, and account balance operations in the cloud-native order processor system.

## Features

### User Management
- User registration with email and username validation
- User authentication with JWT tokens
- User profile management
- Password hashing with bcrypt

### Account Balance Management
- Balance tracking for each user
- Deposit and withdrawal operations
- Transaction history with audit trail
- Automatic balance updates on transaction completion

### Security
- JWT-based authentication
- Password hashing with bcrypt
- Input validation and sanitization
- Rate limiting support

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Authenticate user and get JWT token

### User Management
- `GET /users/{user_id}/profile` - Get user profile
- `PUT /users/{user_id}/profile` - Update user profile
- `GET /users/{user_id}/portfolio` - Get user's asset portfolio

### Balance Management
- `GET /users/{user_id}/balance` - Get current balance
- `POST /users/{user_id}/balance/deposit` - Deposit funds
- `POST /users/{user_id}/balance/withdraw` - Withdraw funds
- `GET /users/{user_id}/balance/transactions` - Get transaction history

## Architecture

### Database Design
- **Single Table Design**: Uses DynamoDB with composite PK/SK
- **User Entity**: PK=user_id, SK=user_id
- **Balance Entity**: PK=user_id, SK=balance
- **BalanceTransaction Entity**: PK=transaction_id, SK=user_id#timestamp

### Integration Points
- **Order Service**: Validates user balance before order creation
- **Inventory Service**: Provides user portfolio information
- **Gateway**: Handles authentication and routing

### Balance-Order Integration Flow
1. **Order Creation**: Order service validates user balance
2. **Transaction Creation**: Creates pending transaction
3. **Order Execution**: Updates transaction status to completed
4. **Balance Update**: Automatically updates user balance

## Technology Stack

- **Framework**: FastAPI
- **Database**: DynamoDB (AWS)
- **Authentication**: JWT tokens
- **Password Hashing**: bcrypt
- **Validation**: Pydantic
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Monitoring**: Prometheus metrics

## Development Status

### ✅ Completed
- User registration and authentication
- JWT token management
- Password hashing and validation
- Basic user profile management
- Balance entity and DAO implementation
- Balance creation on user registration
- Two-layer validation strategy
- Comprehensive test coverage

### 🚧 In Progress
- Balance management APIs (deposit/withdraw)
- Transaction history endpoints
- Portfolio integration with inventory service

### 📋 Planned
- Email confirmation for registration
- Password reset functionality
- Enhanced security features
- Rate limiting implementation
- Advanced user analytics

## Quick Start

### Prerequisites
- Python 3.11+
- AWS credentials configured
- DynamoDB table created

### Installation
```bash
cd services/user_service
pip install -r requirements.txt
pip install -e .
```

### Running Tests
```bash
./build.sh user_service
```

### Running Locally
```bash
cd src
uvicorn main:app --reload --port 8001
```

### Environment Variables
```bash
AWS_REGION=us-west-2
DYNAMODB_TABLE_NAME=order-processor-table
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API Documentation

Once the service is running, visit:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Testing

### Test Coverage
- Unit tests for all controllers
- Integration tests for database operations
- Validation tests for API models
- Authentication flow tests

### Running Specific Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/controllers/auth/test_register.py
```

## Health Checks

- `GET /health` - Service health status
- `GET /health/detailed` - Detailed health with database status

## Metrics

The service exposes Prometheus metrics at `/metrics`:
- Request counts and durations
- Database operation metrics
- Authentication success/failure rates
- Balance operation metrics

## Error Handling

### Validation Errors
- Field validation at API model level
- Business validation at controller level
- Consistent error response format

### Database Errors
- Connection error handling
- Transaction rollback on failures
- Graceful degradation

### Authentication Errors
- Invalid credentials handling
- Token expiration management
- Rate limiting for failed attempts

## Contributing

1. Follow the established validation strategy
2. Add tests for new features
3. Update documentation
4. Ensure code coverage remains above 60%

## Dependencies

### Common Package
- Entities: User, Balance, BalanceTransaction
- DAOs: UserDAO, BalanceDAO
- Database: DynamoDB connection and health checks
- Validation: Field and business validators
- Exceptions: Custom exception classes

### External Dependencies
- FastAPI for web framework
- Pydantic for data validation
- boto3 for AWS services
- bcrypt for password hashing
- PyJWT for JWT handling