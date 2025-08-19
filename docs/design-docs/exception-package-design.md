# 🚨 Exception Package Design

## 🎯 **Purpose**
Document design decisions, options considered, and rationale for the Exception Package to prevent re-designing and maintain consistency.

---

## 📋 **Component Design: Exception Package**
**Date**: 2025-08-20
**Author**: System Design Team
**Status**: Completed

#### **🎯 Problem Statement**
- **Problem**: Need standardized error handling across all microservices
- **Requirements**: Consistent error responses, security, client experience, debugging
- **Constraints**: RFC 7807 compliance, FastAPI integration, maintainability

#### **🔍 Options Considered**

- **Option A: Basic HTTP Status Codes**
  - ✅ Pros: Simple, standard, no additional dependencies
  - ❌ Cons: Limited information, poor client experience, difficult debugging
  - 💰 Cost: Low cost, low functionality
  - ⏱️ Complexity: Low complexity, low value

- **Option B: RFC 7807 Problem Details (Chosen)**
  - ✅ Pros: Industry standard, rich error information, self-documenting
  - ❌ Cons: More complex implementation, larger response size
  - 💰 Cost: Medium cost, high functionality
  - ⏱️ Complexity: Medium complexity, high value

- **Option C: Custom Error Format**
  - ✅ Pros: Full control, tailored to needs, optimized
  - ❌ Cons: Non-standard, client learning curve, maintenance overhead
  - 💰 Cost: High cost, medium functionality
  - ⏱️ Complexity: High complexity, medium value

#### **🏗️ Final Decision**
- **Chosen Option**: RFC 7807 Problem Details with standardized error codes
- **Rationale**: Industry standard, excellent client experience, comprehensive error information
- **Trade-offs Accepted**: Implementation complexity for superior error handling

#### **🔧 Implementation Details**

**Key Components**:
- **Error Models**: RFC 7807 compliant Problem Details structure
- **Error Codes**: Standardized error codes across all services
- **Exception Mapping**: Internal to external error transformation
- **FastAPI Integration**: Automatic exception handlers and middleware
- **Security Layer**: Internal exception protection and sanitization

**Data Structures**:
- **ProblemDetails**: RFC 7807 compliant error response
- **ErrorCode**: Standardized error code enumeration
- **ErrorDetails**: Field-specific validation errors
- **ExceptionMapping**: Internal to external error mapping

**Configuration**:
- **Error Codes**: 7 standardized error codes for all services
- **Security**: Internal exceptions never exposed to clients
- **Logging**: Comprehensive error logging and audit trails
- **Documentation**: Self-documenting error responses with links

#### **🧪 Testing Strategy**
- **Unit Tests**: Error model validation and exception mapping
- **Integration Tests**: FastAPI exception handler integration
- **Security Tests**: Internal exception protection validation
- **Compliance Tests**: RFC 7807 standard compliance verification

#### **📝 Notes & Future Considerations**
- **Known Limitations**: Larger response size, implementation complexity
- **Future Improvements**: Advanced error analytics, error correlation, performance optimization

---

## 📝 **Quick Decision Log**

| Date | Component | Decision | Why | Impact | Status |
|------|-----------|----------|-----|---------|---------|
| 8/17 | Error Format | RFC 7807 over basic HTTP | Industry standard, rich info | High | ✅ Done |
| 8/17 | Error Codes | 7 standardized over custom | Consistency, simplicity | Medium | ✅ Done |
| 8/17 | Security | Internal protection over exposure | Security, client safety | High | ✅ Done |
| 8/17 | Integration | FastAPI handlers over manual | Automation, consistency | Medium | ✅ Done |

**Status Indicators:**
- ✅ **Done** - Decision implemented and working
- 🔄 **In Progress** - Decision made, implementation ongoing
- 📋 **Planned** - Decision made, not yet started
- ❌ **Rejected** - Decision was made but later rejected
- 🔍 **Under Review** - Decision being reconsidered

---

## 🏗️ **Simple Architecture Diagrams**

### **Exception Package Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Microservices │    │   Exception     │    │   Client        │
│   (Internal)    │◄──►│   Package       │◄──►│   (External)    │
│   - Domain      │    │   - Mapping     │    │   - RFC 7807    │
│   - Business    │    │   - Security    │    │   - Standard    │
│   - System      │    │   - Validation  │    │   - Rich Info   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   FastAPI       │
                       │   - Handlers    │
                       │   - Middleware  │
                       │   - Integration │
                       └─────────────────┘
```

### **Exception Flow**
```
1. Internal Exception (Service)
2. Exception Mapping Layer
3. Security Validation
4. RFC 7807 Transformation
5. FastAPI Handler
6. Client Response
7. Error Logging
8. Audit Trail
```

---

## 🔐 **API Design & Models**

### **Core Error Models**

#### **Problem Details (RFC 7807)**
```python
class ProblemDetails(BaseModel):
    type: str = Field(..., description="URI reference to error type")
    title: str = Field(..., description="Short, human-readable error title")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Human-readable error description")
    instance: str = Field(..., description="URI reference to specific error instance")
    trace_id: Optional[str] = Field(None, description="Request correlation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    errors: Optional[List[ErrorDetails]] = Field(None, description="Field-specific errors")
    help_url: Optional[str] = Field(None, description="Link to error documentation")
```

#### **Error Details**
```python
class ErrorDetails(BaseModel):
    field: str = Field(..., description="Field name with error")
    message: str = Field(..., description="Field-specific error message")
    value: Optional[Any] = Field(None, description="Invalid field value")
    code: Optional[str] = Field(None, description="Field-specific error code")
    constraint: Optional[str] = Field(None, description="Validation constraint violated")
```

#### **Error Code Enumeration**
```python
class ErrorCode(str, Enum):
    # Authentication Errors (401)
    AUTHENTICATION_ERROR = "AUTH_001"

    # Authorization Errors (403)
    AUTHORIZATION_ERROR = "AUTH_002"

    # Resource Errors (404, 409)
    RESOURCE_NOT_FOUND = "RES_001"
    RESOURCE_ALREADY_EXISTS = "RES_002"
    RESOURCE_CONFLICT = "RES_003"

    # Validation Errors (422)
    VALIDATION_ERROR = "VAL_001"
    INVALID_INPUT = "VAL_002"
    MISSING_REQUIRED_FIELD = "VAL_003"

    # Server Errors (500, 503)
    INTERNAL_SERVER_ERROR = "INT_001"
    SERVICE_UNAVAILABLE = "SVC_001"
    EXTERNAL_SERVICE_ERROR = "SVC_002"

    # Rate Limiting (429)
    RATE_LIMIT_EXCEEDED = "RATE_001"

    # Business Logic Errors (400)
    INSUFFICIENT_BALANCE = "BUS_001"
    INVALID_ORDER = "BUS_002"
    ASSET_NOT_AVAILABLE = "BUS_003"
```

### **Exception Mapping Models**

#### **Exception Mapping Configuration**
```python
class ExceptionMapping(BaseModel):
    exception_class: Type[Exception]
    error_code: ErrorCode
    http_status: int
    title: str
    detail_template: str
    include_traceback: bool = Field(False, description="Include stack trace in logs only")
    log_level: str = Field("ERROR", description="Logging level for this exception")
    audit_required: bool = Field(True, description="Whether to create audit log entry")
```

#### **Exception Response**
```python
class ExceptionResponse(BaseModel):
    success: bool = Field(False, description="Always false for errors")
    error: ProblemDetails = Field(..., description="RFC 7807 Problem Details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    service: str = Field(..., description="Service name generating the error")
    version: str = Field(..., description="Service version")
    request_id: Optional[str] = Field(None, description="Request correlation ID")
```

### **FastAPI Integration Models**

#### **Exception Handler Configuration**
```python
class ExceptionHandlerConfig(BaseModel):
    include_traceback: bool = Field(False, description="Include stack traces in development")
    log_exceptions: bool = Field(True, description="Log all exceptions")
    audit_exceptions: bool = Field(True, description="Create audit log entries")
    rate_limit_logging: bool = Field(False, description="Log rate limit exceptions")
    development_mode: bool = Field(False, description="Development mode for debugging")
```

#### **Middleware Configuration**
```python
class ExceptionMiddlewareConfig(BaseModel):
    enable_request_logging: bool = Field(True, description="Log incoming requests")
    enable_response_logging: bool = Field(False, description="Log outgoing responses")
    enable_error_logging: bool = Field(True, description="Log all errors")
    enable_performance_logging: bool = Field(False, description="Log performance metrics")
    correlation_id_header: str = Field("X-Correlation-ID", description="Correlation ID header")
    trace_id_header: str = Field("X-Trace-ID", description="Trace ID header")
```

### **Utility Models**

#### **Error Context**
```python
class ErrorContext(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    username: Optional[str] = Field(None, description="Authenticated username")
    service_name: str = Field(..., description="Service generating the error")
    endpoint: str = Field(..., description="API endpoint being called")
    method: str = Field(..., description="HTTP method")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    request_body: Optional[Dict[str, Any]] = Field(None, description="Request body (sanitized)")
    query_params: Optional[Dict[str, Any]] = Field(None, description="Query parameters")
```

#### **Audit Log Entry**
```python
class AuditLogEntry(BaseModel):
    audit_id: str = Field(..., description="Unique audit log identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str = Field(..., description="Audit level (INFO, WARNING, ERROR)")
    category: str = Field(..., description="Audit category (AUTH, BUSINESS, SYSTEM)")
    action: str = Field(..., description="Action being audited")
    username: Optional[str] = Field(None, description="User performing action")
    service_name: str = Field(..., description="Service generating audit entry")
    endpoint: str = Field(..., description="API endpoint")
    request_id: str = Field(..., description="Request correlation ID")
    details: Dict[str, Any] = Field(..., description="Audit details")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    success: bool = Field(..., description="Whether action was successful")
    error_code: Optional[str] = Field(None, description="Error code if failed")
    error_message: Optional[str] = Field(None, description="Error message if failed")
```

### **Configuration Models**

#### **Exception Package Configuration**
```python
class ExceptionPackageConfig(BaseModel):
    # Error Response Configuration
    include_traceback: bool = Field(False, description="Include stack traces in responses")
    include_internal_details: bool = Field(False, description="Include internal error details")
    sanitize_error_messages: bool = Field(True, description="Sanitize error messages for clients")

    # Logging Configuration
    log_level: str = Field("ERROR", description="Default logging level")
    log_format: str = Field("json", description="Log output format")
    log_to_file: bool = Field(False, description="Log to file in addition to console")
    log_file_path: Optional[str] = Field(None, description="Log file path")

    # Audit Configuration
    enable_audit_logging: bool = Field(True, description="Enable audit logging")
    audit_log_level: str = Field("INFO", description="Audit logging level")
    audit_retention_days: int = Field(90, description="Audit log retention period")

    # Security Configuration
    mask_sensitive_fields: bool = Field(True, description="Mask sensitive fields in logs")
    sensitive_field_patterns: List[str] = Field(default_factory=lambda: [
        r"password", r"token", r"secret", r"key", r"credential"
    ])

    # Performance Configuration
    enable_performance_logging: bool = Field(False, description="Enable performance logging")
    performance_threshold_ms: int = Field(1000, description="Performance threshold in milliseconds")
    enable_correlation_tracking: bool = Field(True, description="Enable request correlation tracking")
```

---

## 🔗 **Related Documentation**

- **[Services Design](./services-design.md)**: Overall services architecture
- **[Common Package Design](./common-package-design.md)**: Shared components design
- **[Exception Package README](../services/exception/README.md)**: Implementation and usage guide
- **[RFC 7807](https://tools.ietf.org/html/rfc7807)**: Problem Details for HTTP APIs

---

**🎯 This exception package design provides standardized error handling with RFC 7807 compliance, comprehensive security, and excellent client experience across all microservices.**
