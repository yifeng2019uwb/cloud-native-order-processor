# 🏗️ Architecture Documentation

## 🎯 **System Overview**

The Cloud-Native Order Processor is designed as a microservices-based trading platform with a focus on scalability, cost-efficiency, and rapid development. The architecture prioritizes personal project optimization while maintaining production-ready quality.

## 🏗️ **Design Philosophy & Trade-offs** 🎯

### **Core Design Principles**
- **Serverless-First**: Minimize operational overhead and maintenance costs
- **Cost Optimization**: Prioritize efficient resource usage over complex features
- **Development Velocity**: Focus on rapid iteration and learning
- **80/20 Rule**: Optimize for common use cases over edge cases

### **Technology Choices & Rationale**

#### **DynamoDB as Primary Database**
- **Why DynamoDB**: Serverless, pay-per-use, no maintenance overhead
- **Cost Efficiency**: Only pay for actual usage, no idle costs
- **Scalability**: Automatic scaling without configuration
- **Trade-off**: Limited query flexibility, but optimized for our access patterns

#### **Single-Table Design**
- **Why Single-Table**: Simplified queries, reduced complexity for personal project scale
- **Cost Benefits**: Fewer table operations, lower RCU/WCU consumption
- **Maintenance**: Easier to manage and understand
- **Trade-off**: Less normalized, but optimized for our specific use cases

#### **Simplified Atomic Operations**
- **Why Conditional Expressions**: Using `upsert_asset_balance` instead of complex DynamoDB transactions
- **Cost Optimization**: Avoid expensive transaction costs
- **Simplicity**: Easier to understand and debug
- **Trade-off**: Less ACID guarantees, but sufficient for our use cases

#### **PK/SK Strategy**
- **Why User-Centric Design**: Optimized for 80% use cases (user-specific queries)
- **Efficiency**: Minimize RCU/WCU usage through efficient key design
- **Performance**: Fast queries for common access patterns
- **Trade-off**: Less flexible for complex multi-dimensional queries

## 🏗️ **System Architecture**

### **Microservices Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Backend       │
│   (React)       │◄──►│   (Go/Gin)      │◄──►│   Services      │
│   - Auth        │    │   - Auth        │    │   - User        │
│   - Dashboard   │    │   - Proxy       │    │   - Inventory   │
│   - Inventory   │    │   - Security    │    │   - Orders      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │   (Caching)     │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   DynamoDB      │
                       │   (AWS)         │
                       └─────────────────┘
```

### **Service Responsibilities**

#### **Frontend (React + TypeScript)**
- **User Interface**: Responsive, modern UI with authentication
- **State Management**: Client-side state and API integration
- **Security**: Token management and secure API calls

#### **API Gateway (Go + Gin)**
- **Authentication**: JWT validation and protected routes
- **Routing**: Intelligent request routing to backend services
- **Security**: CORS, rate limiting, input validation
- **Performance**: Request/response optimization

#### **Backend Services (Python + FastAPI)**
- **User Service**: Authentication, balance management, transactions
- **Inventory Service**: Asset management and public data
- **Order Service**: Order processing and portfolio management
- **Common Package**: Shared utilities and database access

## 🗄️ **Database Design**

### **DynamoDB Schema Strategy**

#### **Single-Table Design Benefits**
- **Simplified Queries**: All data in one table with consistent access patterns
- **Cost Efficiency**: Fewer table operations, lower RCU/WCU consumption
- **Maintenance**: Easier to manage and understand
- **Performance**: Optimized for our specific access patterns

#### **Key Design Patterns**
```
Users Table:
├── User Records: PK=username, SK=USER
├── Balance Records: PK=username, SK=BALANCE
├── Asset Balances: PK=username, SK=ASSET#{asset_id}
├── Asset Transactions: PK=TRANS#{username}#{asset_id}, SK=timestamp
└── Orders: PK=order_id, SK=ORDER (with GSI for user queries)
```

#### **Global Secondary Indexes (GSI)**
- **UserOrdersIndex**: PK=username, SK=ASSET_ID for efficient user order queries
- **Cost Optimization**: Only create GSIs for frequently used access patterns
- **Performance**: Fast queries for user-specific data

## 🔐 **Security Architecture**

### **Multi-Layer Security**
- **API Gateway**: JWT validation, rate limiting, CORS
- **Service Level**: Auth-gated endpoints, input validation
- **Database**: AWS IAM roles, least privilege access
- **Infrastructure**: Kubernetes (service accounts), network policies

### **Authentication Flow**
1. **User Login**: Credentials validated against User Service
2. **JWT Generation**: Secure token with user claims
3. **Request Validation**: Gateway validates JWT for each request
4. **Service context**: Services receive user context from gateway (auth-only; no RBAC—see [Gateway Design](gateway-design.md#authorization-model) for rationale)

## 🚀 **Deployment Architecture**

### **Container Strategy**
- **Docker**: All services containerized for consistency
- **Kubernetes**: Orchestration for scalability and reliability
- **Helm**: Package management for complex deployments

### **Environment Strategy**
- **Development**: Local Docker Compose for rapid iteration
- **Staging**: Kubernetes with production-like configuration
- **Production**: AWS EKS with auto-scaling and monitoring

## 📊 **Performance & Scalability**

### **Optimization Strategies**
- **Caching**: Redis for frequently accessed data
- **Database**: Efficient DynamoDB key design and query patterns
- **API**: Response compression and connection pooling
- **Frontend**: Code splitting and lazy loading

### **Scaling Considerations**
- **Horizontal Scaling**: Stateless services scale automatically
- **Database Scaling**: DynamoDB auto-scales based on demand
- **Cost Management**: Monitor RCU/WCU usage and optimize queries

## 🔄 **Development Workflow**

### **Code Quality Standards**
- **Testing**: 90%+ test coverage across all services
- **Documentation**: Comprehensive API and architecture docs
- **Code Review**: Automated checks and manual review process
- **CI/CD**: Automated testing and deployment pipeline

### **Development Philosophy**
- **Rapid Iteration**: Focus on working features over perfect architecture
- **Learning Focus**: Prioritize understanding over complexity
- **Production Ready**: Maintain quality while optimizing for development speed
- **Cost Conscious**: Monitor and optimize resource usage

## 📈 **Monitoring & Observability**

### **Health Checks**
- **Service Health**: Each service exposes health endpoints
- **Database Health**: Connection and query performance monitoring
- **Infrastructure**: Kubernetes and AWS resource monitoring

### **Logging Strategy**
- **Structured Logging**: JSON format for easy parsing
- **Centralized Logging**: AWS CloudWatch for log aggregation
- **Error Tracking**: Comprehensive error logging and alerting

## 🎯 **Future Considerations**

### **Potential Enhancements**
- **Event-Driven Architecture**: Add message queues for async processing
- **Advanced Caching**: Implement more sophisticated caching strategies
- **Micro-Frontends**: Split frontend into smaller, independent applications
- **Service Mesh**: Add Istio for advanced service-to-service communication

### **Scaling Considerations**
- **Multi-Region**: Deploy across multiple AWS regions
- **CDN**: Add CloudFront for global content delivery
- **Database Sharding**: Consider DynamoDB global tables for multi-region
- **Advanced Monitoring**: Implement distributed tracing and APM

---

*This architecture prioritizes simplicity, cost-efficiency, and rapid development while maintaining production-ready quality standards.*
