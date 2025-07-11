# Docker Setup for Cloud Native Order Processor

This directory contains Docker configurations for running the entire application stack.

## Services

- **Frontend**: React application with Vite (port 3000)
- **User Service**: FastAPI authentication service (port 8000)
- **Inventory Service**: FastAPI inventory management service (port 8001)

## Prerequisites

1. Docker and Docker Compose installed
2. AWS credentials configured in `~/.aws/`
3. DynamoDB tables created in AWS

## Quick Start

### Production Build

```bash
# Build and start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# User Service API: http://localhost:8000
# Inventory Service API: http://localhost:8001
```

### Development Mode

```bash
# Start development environment with hot reloading
docker-compose -f docker-compose.dev.yml up --build

# Access the application
# Frontend: http://localhost:3000 (with hot reloading)
# User Service API: http://localhost:8000
# Inventory Service API: http://localhost:8001
```

## Individual Service Commands

### Build specific service
```bash
# Build frontend only
docker-compose build frontend

# Build user service only
docker-compose build user-service

# Build inventory service only
docker-compose build inventory-service
```

### Run specific service
```bash
# Run only user service
docker-compose up user-service

# Run only inventory service
docker-compose up inventory-service
```

## Environment Variables

### User Service
- `JWT_SECRET`: Secret key for JWT tokens
- `JWT_ALGORITHM`: JWT algorithm (default: HS256)
- `JWT_EXPIRATION_HOURS`: Token expiration time
- `AWS_REGION`: AWS region for DynamoDB
- `USERS_TABLE`: DynamoDB table name for users
- `ORDERS_TABLE`: DynamoDB table name for orders
- `INVENTORY_TABLE`: DynamoDB table name for inventory

### Inventory Service
- `AWS_REGION`: AWS region for DynamoDB
- `USERS_TABLE`: DynamoDB table name for users
- `ORDERS_TABLE`: DynamoDB table name for orders
- `INVENTORY_TABLE`: DynamoDB table name for inventory

## Health Checks

All services include health checks:

- User Service: `http://localhost:8000/health`
- Inventory Service: `http://localhost:8001/health`
- Frontend: `http://localhost:3000`

## API Endpoints

### User Service (port 8000)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/profile` - Get user profile
- `POST /auth/logout` - User logout
- `GET /health` - Health check

### Inventory Service (port 8001)
- `GET /inventory/assets` - List all assets
- `GET /inventory/assets/{id}` - Get asset details
- `GET /health` - Health check

### Frontend (port 3000)
- `/` - Main application
- `/inventory` - Inventory page
- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - User dashboard

## Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 3000, 8000, and 8001 are available
2. **AWS credentials**: Ensure `~/.aws/credentials` is properly configured
3. **DynamoDB tables**: Verify tables exist in the specified AWS region

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs user-service
docker-compose logs inventory-service
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

### Cleanup

```bash
# Stop all services
docker-compose down

# Remove containers and networks
docker-compose down --remove-orphans

# Remove all containers, networks, and images
docker-compose down --rmi all --volumes --remove-orphans
```

## Development Workflow

1. Use `docker-compose.dev.yml` for development with hot reloading
2. Make changes to source code - they will be reflected automatically
3. Use `docker-compose.yml` for production builds
4. Test API endpoints using the exposed ports

## Network Configuration

All services are connected via the `order-processor-network` bridge network, allowing them to communicate using service names as hostnames.