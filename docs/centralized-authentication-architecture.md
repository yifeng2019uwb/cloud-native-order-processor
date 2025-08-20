# Centralized Authentication Architecture via Auth Service

## 📋 Document Overview

**Document Type**: Architecture Design Document
**Version**: 2.0
**Date**: 2025-08-20
**Status**: Draft
**Author**: Cloud Native Order Processor Team

## 🎯 Executive Summary

This document outlines the design for implementing centralized authentication in the Cloud Native Order Processor system. The architecture introduces a dedicated **Auth Service** that handles all JWT validation and user authentication, while the Gateway focuses on routing and request forwarding. This eliminates the need for individual backend services to validate JWT tokens and provides a foundation for future RBAC implementation.

## 🏗️ System Architecture Overview

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External      │    │     Gateway     │    │   Auth Service  │    │   Backend       │
│   Clients       │───▶│   (Routing)     │◄──▶│   (JWT + RBAC)  │    │   Services      │
│                 │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                                              │
                                │                                              │
                                ▼                                              │
                       ┌─────────────────┐                                    │
                       │   Request       │                                    │
                       │   Forwarding    │────────────────────────────────────┘
                       │   & Response    │
                       │   Handling      │
                       └─────────────────┘
```

#### Request Flow:
1. **Client → Gateway**: External request with JWT token
2. **Gateway → Auth Service**: Forward for JWT validation
3. **Auth Service → Gateway**: Return user context and authentication result
4. **Gateway → Backend**: Forward request with security headers
5. **Backend → Gateway**: Return business logic response
6. **Gateway → Client**: Forward response to client

#### Key Architecture Principles:
- **Gateway**: Single entry point, handles routing and forwarding
- **Auth Service**: Dedicated authentication and authorization
- **Backend Services**: Business logic only, no JWT validation
- **Internal Network**: All services communicate via Kubernetes internal network
- **Security Headers**: Gateway injects security context from Auth Service

### Key Principles

1. **Dedicated Authentication Service**: Auth Service handles all JWT validation and user authentication
2. **Gateway as Router**: Gateway focuses on routing and request forwarding, not authentication logic
3. **Trusted Internal Communication**: Backend services trust Auth Service completely
4. **No JWT Secret Distribution**: Only Auth Service possesses JWT validation secrets
5. **Network Isolation**: Backend services are not directly accessible externally
6. **Future RBAC Ready**: Architecture designed to support Role-Based Access Control

## 🔐 Authentication Flow

### 1. Client Request Processing

#### External Request
- Client sends HTTP request with `Authorization: Bearer <JWT_TOKEN>`
- Request is routed to Gateway (no direct backend access possible)
- Gateway becomes the single entry point for all external traffic

#### Request Routing
- Gateway receives request and forwards to **Auth Service** for authentication
- Gateway maintains request/response correlation
- Gateway handles routing decisions based on Auth Service response

### 2. Auth Service Processing

#### JWT Validation
- **Auth Service** validates JWT token using its configured JWT secret
- **Auth Service** extracts user information from JWT claims:
  - Username
  - Role
  - Permissions
  - Token expiration
- If validation fails, Auth Service returns authentication error

#### User Context Extraction
- Username from JWT `sub` claim
- Role from JWT `role` claim
- Authentication status (authenticated/unauthenticated)
- Token metadata (creation time, expiration)
- Future: RBAC permissions and access control

#### Authentication Response
- **Auth Service** returns authentication result to Gateway
- Includes user context and authentication status
- May include authorization decisions for specific endpoints

### 3. Gateway Processing

#### Authentication Integration
- Gateway receives authentication result from Auth Service
- Gateway adds security headers based on Auth Service response
- **Gateway forwards request to appropriate backend service**

#### Security Header Injection
Gateway adds the following headers to all forwarded requests:
- `X-Source: gateway` - Proves request came through Gateway
- `X-Auth-Service: auth-service` - Proves authentication was handled by Auth Service
- `X-User-ID: <username>` - Extracted username from Auth Service
- `X-User-Role: <role>` - Extracted user role from Auth Service
- `X-Authenticated: true` - Authentication status from Auth Service
- `X-Request-ID: <uuid>` - Request tracking
- `X-Auth-Token: <token-id>` - Authentication token reference

#### Request Routing
- **Gateway determines target backend service** based on URL path
- **Gateway forwards request** with all original headers + security headers
- **Gateway maintains request/response correlation**
- **Gateway handles response forwarding** back to client

### 4. Backend Service Processing

#### Source Validation
- Backend service validates `X-Source: gateway` header
- Backend service validates `X-Auth-Service: auth-service` header
- Rejects any request without proper source identification
- Only processes requests from trusted Gateway and Auth Service

#### User Context Extraction
- Backend extracts user information from Gateway headers
- No JWT parsing or validation required
- User context available for business logic decisions

#### Business Logic Execution
- Service executes business logic based on user context
- Permission checks based on Auth Service-provided user role
- Audit logging using Auth Service-provided user information

## 🛡️ Security Model

### Network Security

#### External Access Control
- **Gateway**: Exposed to external network (ports 8080/30002)
- **Auth Service**: Internal network only (no external ports)
- **Backend Services**: Internal network only (no external ports)
- **Load Balancer**: Routes all external traffic to Gateway

#### Internal Network Isolation
- Auth Service and backend services communicate via Kubernetes internal network
- Services are not accessible from external networks
- Gateway and Auth Service act as security boundary

#### Network-Level Security Controls

##### Kubernetes Network Policies
```yaml
# Backend services only accept requests from internal network
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-services-network-policy
spec:
  podSelector:
    matchLabels:
      app: backend-service
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: internal-services
    - podSelector:
        matchLabels:
          app: gateway
    - podSelector:
        matchLabels:
          app: auth-service
    ports:
    - protocol: TCP
      port: 8000  # Backend service port
```

##### Service Configuration
- **Backend Services**: Bind only to internal Kubernetes cluster IPs
- **No External Load Balancers**: Services not exposed via LoadBalancer type
- **Internal Port Binding**: Services listen only on internal cluster ports
- **NodePort Restrictions**: No NodePort exposure for backend services

##### IP Whitelisting
- **Internal Cluster IPs**: Only accept requests from Kubernetes cluster IP range
- **Gateway IPs**: Whitelist Gateway service IPs
- **Auth Service IPs**: Whitelist Auth Service IPs
- **Reject External IPs**: Block all requests from external IP addresses

##### Port Security
- **Backend Service Ports**: Only listen on internal cluster ports (8000, 8001, 8002)
- **No External Port Mapping**: No port forwarding to external interfaces
- **Internal Service Discovery**: Use Kubernetes internal service names for communication

### Trust Model

#### Auth Service Trust
- **Gateway** trusts Auth Service for all authentication decisions
- **Backend services** trust Gateway and Auth Service completely
- **Auth Service** is the single source of truth for authentication

#### Request Source Validation
- Backend services validate both `X-Source: gateway` and `X-Auth-Service: auth-service` headers
- Reject requests without proper source identification
- Prevent bypass of security layers

### Authentication Boundaries

#### External → Gateway
- Request routing and forwarding
- Security header management
- Response handling

#### Gateway → Auth Service
- Authentication requests
- JWT validation requests
- User context retrieval

#### Gateway → Backend
- Trusted internal communication
- Security header injection
- Request forwarding

#### Backend → Backend (if needed)
- Direct service-to-service communication
- May require internal service mesh authentication
- Separate from external authentication flow

## 🔧 Service Responsibilities

### Common Package Architecture

#### JWT Token Management (`services/common/src/security/token_manager.py`)
- **Centralized JWT functionality** shared across all services
- **Token creation**: `create_access_token()` method for User Service
- **Token validation**: `verify_access_token()` method for Auth Service
- **Shared configuration**: JWT secret, algorithm, expiration settings
- **Consistent implementation**: Same JWT logic across all services

#### Benefits of Common Package Approach
- **DRY Principle**: No duplicate JWT code across services
- **Consistency**: All services use identical JWT implementation
- **Maintainability**: Single place to update JWT logic
- **Testing**: JWT functionality can be tested independently
- **Version Control**: JWT changes affect all services simultaneously

#### JWT Secret Management
- **Single source of truth**: JWT secret configured in common package
- **Environment-based**: Secret loaded from environment variables
- **Fallback values**: Development fallbacks for local development
- **Production security**: Production secrets managed via Kubernetes secrets

### Gateway Service

#### Primary Responsibilities
- **Request routing** to appropriate services
- **Request/response correlation** and forwarding
- **Header manipulation** and security injection
- **Error handling** and logging

#### Authentication Responsibilities
- **None** - No JWT validation or authentication logic
- **Request forwarding** to Auth Service for authentication
- **Header management** based on Auth Service response

#### Security Features
- CORS policy enforcement
- Request sanitization
- Audit logging
- Security header management

### Auth Service

#### Authentication Responsibilities
- **JWT token validation** and parsing
- **User context extraction** and enrichment
- **Token management** (creation, validation, blacklisting)
- **Authentication status** verification

#### Authorization Responsibilities (Future RBAC)
- **Role-based access control** policies
- **Permission mapping** for different roles
- **Dynamic permission** evaluation
- **Access control** decisions

#### Security Features
- JWT secret management
- Token blacklist functionality
- Rate limiting for auth operations
- Audit logging for authentication events

### Backend Services

#### Authentication Responsibilities
- **None** - No JWT validation required
- Source validation (`X-Source: gateway`, `X-Auth-Service: auth-service`)
- User context extraction from Gateway headers

#### Business Logic
- Core business functionality
- Permission-based access control
- User context utilization
- Audit trail maintenance

#### Security Features
- Source header validation
- User context verification
- Business-level permission checks

### User Service (Special Case)

#### JWT Token Creation
- Creates JWT tokens for user login/registration
- Uses same JWT secret as Auth Service (for token creation only)
- No JWT validation for incoming requests

#### Authentication Flow
- Receives login/registration requests via Gateway
- Validates user credentials
- Creates JWT tokens with appropriate claims
- Returns tokens to client through Gateway

#### JWT Implementation
- **JWT functionality remains in common package** (`services/common/src/security/token_manager.py`)
- **User Service imports and uses** `TokenManager` for token creation
- **Auth Service imports and uses** `TokenManager` for token validation
- **Shared JWT secret**: Both services use the same JWT secret from common configuration
- **Consistent token format**: All services use the same JWT structure and claims

## 📊 Data Flow Examples

### 1. User Registration and Login

```
1. Client → Gateway → User Service (Registration)
   - User Service creates user account
   - Returns success response

2. Client → Gateway → User Service (Login)
   - User Service validates credentials
   - User Service creates JWT token using shared secret
   - JWT token returned to client via Gateway
```

### 2. Protected API Access

```
1. Client → Gateway (with JWT token)
   - Gateway forwards request to Auth Service for validation
   - Auth Service validates JWT and extracts user context
   - Auth Service returns authentication result to Gateway

2. Gateway → Backend Service
   - Gateway adds security headers based on Auth Service response
   - Gateway forwards request to appropriate backend service
   - Backend validates X-Source and X-Auth-Service headers
   - Backend extracts user context from Gateway headers
   - Backend executes business logic
   - Backend returns response to Gateway

3. Gateway → Client
   - Gateway receives response from backend service
   - Gateway forwards backend response to client
   - Gateway maintains response headers and status
```

### 3. Service-to-Service Communication

```
1. Service A → Service B (internal)
   - May require internal authentication
   - Separate from external JWT flow
   - Uses internal service mesh or direct calls

2. External Client → Gateway → Auth Service → Gateway → Service A → Gateway → Service B
   - Auth Service handles external authentication
   - Gateway forwards requests between services
   - Internal calls use Auth Service-provided context
   - No additional authentication required
```

## 🎯 Benefits

### Security Improvements

#### Centralized Security Control
- Single point of security policy management
- Consistent authentication across all services
- Easier security auditing and monitoring

#### Reduced Attack Surface
- Backend services not directly accessible
- No JWT secret distribution across services
- Centralized security boundary

#### Trust Model Simplification
- Clear authentication boundaries
- Eliminates trust issues between services
- Simplified security architecture

### Performance Improvements

#### Reduced Processing Overhead
- No double JWT validation
- Faster backend service processing
- Reduced cryptographic operations

#### Improved Response Times
- Eliminates redundant auth checks
- Streamlined request processing
- Better resource utilization

### Operational Benefits

#### Simplified Configuration Management
- Single JWT secret to manage
- Centralized authentication configuration
- Easier environment management

#### Enhanced Monitoring and Debugging
- Centralized authentication logs
- Better request tracing
- Simplified troubleshooting

#### Easier Security Updates
- Single location for security policy changes
- Faster security patch deployment
- Reduced update complexity

### Architectural Benefits

#### Better Service Separation
- Gateway focuses on routing
- Auth Service handles authentication
- Backend services focus on business logic

#### Improved Scalability
- Auth Service can be scaled independently
- Multiple Gateway instances can share Auth Service
- Better resource utilization

#### Future-Proof Design
- Ready for RBAC implementation
- Easy to add new authentication methods
- Flexible permission system

## ⚠️ Considerations and Risks

### Single Point of Failure

#### Auth Service Availability
- Auth Service becomes critical infrastructure component
- Requires high availability and redundancy
- Load balancing and failover strategies needed

#### Mitigation Strategies
- Multiple Auth Service instances
- Health monitoring and auto-scaling
- Circuit breaker patterns for auth failures

### Security Implications

#### Auth Service Security
- Auth Service becomes high-value attack target
- Requires enhanced security measures
- Regular security audits and penetration testing

#### Internal Trust
- Backend services must trust Auth Service completely
- No verification of Auth Service's authentication decisions
- Requires secure internal network

### Performance Considerations

#### Auth Service Bottleneck
- All authentication flows through Auth Service
- Potential performance bottleneck
- Requires proper sizing and scaling

#### Header Overhead
- Additional headers increase request size
- Minimal impact on performance
- Benefits outweigh overhead

## 🚀 Implementation Roadmap

### Phase 1: Auth Service Creation
- Create dedicated Auth Service
- **Update common package**: Ensure JWT functionality is reusable
- **JWT reuse strategy**: Import `TokenManager` from common package
- Implement JWT validation and user context extraction using common package
- Set up internal communication with Gateway
- Test authentication flows

### Phase 2: Gateway Integration
- Update Gateway to use Auth Service for authentication
- Implement request forwarding to Auth Service
- Add security header injection based on Auth Service response
- Test Gateway-Auth Service integration

### Phase 3: Backend Service Updates
- Remove JWT validation from backend services
- **Maintain common package imports**: Keep `TokenManager` for any remaining JWT operations
- **User Service updates**: Ensure login still uses common package for token creation
- Implement source header validation
- Update user context extraction
- Test security measures

### Phase 4: Network Security Implementation
- **Kubernetes Network Policies**: Implement NetworkPolicy to restrict backend service access
- **Service Configuration**: Update services to bind only to internal cluster IPs
- **IP Whitelisting**: Configure services to reject external IP requests
- **Port Security**: Ensure no external port exposure for backend services
- **Load Balancer Removal**: Remove external LoadBalancer services for backend
- **Internal Service Discovery**: Configure internal-only service communication

### Phase 5: RBAC Implementation
- Add role-based access control to Auth Service
- **Extend common package**: Add RBAC utilities to common package
- **RBAC reuse**: Make RBAC functionality available to other services
- Implement permission mapping and evaluation
- Update authorization logic
- Test RBAC functionality

### Phase 6: Testing and Validation
- Comprehensive security testing
- Performance testing and optimization
- Integration testing
- Security audit and penetration testing
- **Network Security Testing**: Verify backend services reject external requests
- **IP Whitelist Testing**: Confirm only internal IPs can access backend services
- **Common Package Testing**: Verify JWT functionality works across all services
- **JWT Reuse Testing**: Test token creation in User Service and validation in Auth Service

### Phase 7: Deployment and Monitoring
- Production deployment
- Monitoring and alerting setup
- Performance monitoring
- Security monitoring
- **Network Monitoring**: Monitor for unauthorized access attempts
- **Security Alerting**: Alert on external IP access attempts
- **JWT Monitoring**: Monitor JWT creation and validation across services

## 📝 Conclusion

The centralized authentication architecture with a dedicated Auth Service provides significant security, performance, and operational benefits while following proper microservices principles. By centralizing authentication in a dedicated service, we eliminate JWT secret distribution issues, improve performance, and create a more maintainable and scalable security model.

This design follows industry best practices for microservices authentication and provides a solid foundation for future RBAC implementation and security enhancements.

---

**Document Status**: Draft
**Next Review**: TBD
**Approval**: Pending
