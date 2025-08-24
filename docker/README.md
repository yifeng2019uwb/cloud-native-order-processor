# Docker Setup for Cloud Native Order Processor

**📊 Current Status: PRODUCTION-READY DOCKER ARCHITECTURE** ✅

**Last Updated: 8/24/2025**
- ✅ **Production-Ready Dockerfiles**: Auth Service completed, others pending
- ✅ **Simplified Port Configuration**: Only Gateway (8080) exposed externally
- ✅ **Microservices Architecture**: All requests go through Gateway
- ✅ **Common Package Integration**: Auth Service using shared JWT utilities
- ✅ **Security Improvements**: Non-root users, proper file permissions

This directory contains Docker configurations for running the entire application stack.

## Services

- **Frontend**: React application (port 80) - External access
- **Gateway**: API Gateway (port 8080) - **ONLY EXTERNAL ENTRY POINT**
- **User Service**: FastAPI authentication service (port 8000) - Internal only
- **Inventory Service**: FastAPI inventory management service (port 8001) - Internal only
- **Order Service**: FastAPI order processing service (port 8002) - Internal only
- **Auth Service**: FastAPI JWT validation service (port 8003) - Internal only

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
# Frontend: http://localhost:80
# Gateway (API Entry Point): http://localhost:8080
# Note: Individual services are internal only, access through Gateway
```

### Development Mode

```bash
# Start development environment with hot reloading
docker-compose -f docker-compose.dev.yml up --build

# Access the application
# Frontend: http://localhost:80 (with hot reloading)
# Gateway (API Entry Point): http://localhost:8080
# Note: Individual services are internal only, access through Gateway
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

### **Gateway (port 8080) - Main API Entry Point**
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/profile` - Get user profile (requires JWT)
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/inventory/assets` - List all assets
- `GET /api/v1/inventory/assets/{id}` - Get asset details
- `GET /health` - Gateway health check

### **Frontend (port 80)**
- `/` - Main application
- `/inventory` - Inventory page
- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - User dashboard

### **Internal Services (not directly accessible)**
- **User Service (8000)**: Authentication and user management
- **Inventory Service (8001)**: Asset and inventory management
- **Order Service (8002)**: Order processing and management
- **Auth Service (8003)**: JWT validation and token management

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

## New Architecture: Production-Ready Docker

### **Port Configuration Strategy**
- **External Access**: Only Frontend (80) and Gateway (8080) exposed
- **Internal Services**: User (8000), Inventory (8001), Order (8002), Auth (8003) are internal only
- **Microservices Pattern**: All API requests go through Gateway (8080)

### **Production-Ready Features**
- **Security**: Non-root users, proper file permissions, minimal attack surface
- **Docker Optimization**: Layer caching, cache cleanup, optimized build process
- **Common Package Integration**: Shared utilities properly installed in each service
- **Health Checks**: Optimized health monitoring for all services

### **Benefits**
- ✅ **Simplified Development**: Direct port access (80, 8080) instead of confusing 3000x mappings
- ✅ **Better Security**: Services not directly accessible from external network
- ✅ **Production Ready**: Optimized for production deployment
- ✅ **Consistent Architecture**: Same Docker patterns across all services
- ✅ **Easy Scaling**: Each service is self-contained and independently scalable

## Network Configuration

All services are connected via the `order-processor-network` bridge network, allowing them to communicate using service names as hostnames.