# 📝 Base Logging Standards - Cloud Native Order Processor

> Practical logging for microservices with good observability without enterprise complexity

## 🎯 Simple Goals

- **Track requests** across services with correlation IDs
- **Debug issues** quickly with good context
- **Monitor security** events like failed logins
- **Learn patterns** for future enterprise work

## 🏗️ Basic Log Format

### **Standard Fields (Keep It Simple)**
```json
{
  "timestamp": "2025-08-20T10:30:45Z",
  "level": "INFO",
  "service": "user_service",
  "request_id": "req-12345",
  "user": "john_doe",
  "action": "login",
  "message": "User login successful",
  "duration_ms": 45,
  "extra": {
    "ip": "192.168.1.100",
    "endpoint": "/auth/login"
  }
}
```

### **Required Fields Only**
| Field | Description | Example |
|-------|-------------|---------|
| `timestamp` | When it happened | `2025-08-20T10:30:45Z` |
| `level` | Log level | `INFO`, `WARN`, `ERROR` |
| `service` | Which service | `gateway`, `user_service` |
| `request_id` | Unique request ID | `req-12345` |
| `action` | What happened | `login`, `create_order` |
| `message` | Human readable | `User login successful` |

### **Optional Fields**
| Field | Description | Example |
|-------|-------------|---------|
| `user` | Username (if available) | `john_doe` |
| `duration_ms` | How long it took | `45` |
| `extra` | Additional context | `{"ip": "...", "amount": 100}` |

## 🌐 Gateway Logging (Go)

### **Simple Middleware**
```go
// middleware/base_logging.go
package middleware

import (
    "encoding/json"
    "time"
    "github.com/gin-gonic/gin"
    "github.com/google/uuid"
)

type LogEntry struct {
    Timestamp  string                 `json:"timestamp"`
    Level      string                 `json:"level"`
    Service    string                 `json:"service"`
    RequestID  string                 `json:"request_id"`
    User       string                 `json:"user,omitempty"`
    Action     string                 `json:"action"`
    Message    string                 `json:"message"`
    DurationMS int64                  `json:"duration_ms,omitempty"`
    Extra      map[string]interface{} `json:"extra,omitempty"`
}

func BaseLoggingMiddleware() gin.HandlerFunc {
    return gin.LoggerWithConfig(gin.LoggerConfig{
        Formatter: func(param gin.LogFormatterParams) string {
            requestID := "req-" + uuid.New().String()[:8]

            // Simple user extraction from JWT (optional)
            user := extractUserFromJWT(param.Request)

            // Simple action mapping
            action := getBaseAction(param.Path, param.Method)

            logEntry := LogEntry{
                Timestamp:  param.TimeStamp.UTC().Format(time.RFC3339),
                Level:      getLevel(param.StatusCode),
                Service:    "gateway",
                RequestID:  requestID,
                User:       user,
                Action:     action,
                Message:    fmt.Sprintf("%s %s", param.Method, param.Path),
                DurationMS: param.Latency.Milliseconds(),
                Extra: map[string]interface{}{
                    "method": param.Method,
                    "path":   param.Path,
                    "status": param.StatusCode,
                    "ip":     maskIP(param.ClientIP),
                },
            }

            jsonBytes, _ := json.Marshal(logEntry)
            return string(jsonBytes) + "\n"
        },
    })
}

func getLevel(statusCode int) string {
    if statusCode >= 500 {
        return "ERROR"
    } else if statusCode >= 400 {
        return "WARN"
    }
    return "INFO"
}

func getBaseAction(path string, method string) string {
    // Simple mapping for main endpoints
    switch {
    case path == "/auth/login":
        return "login"
    case path == "/auth/register":
        return "register"
    case path == "/orders" && method == "POST":
        return "create_order"
    case path == "/orders" && method == "GET":
        return "list_orders"
    case path == "/health":
        return "health_check"
    default:
        return "api_call"
    }
}

func maskIP(ip string) string {
    // Simple IP masking for privacy
    if len(ip) > 7 {
        return ip[:len(ip)-3] + "***"
    }
    return ip
}
```

## 🐍 FastAPI Logging (Python)

### **Base Logger Class**
```python
# common/base_logger.py
import json
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

class BaseLogger:
    def __init__(self, service_name: str):
        self.service_name = service_name

    def log(self, level: str, action: str, message: str,
            user: str = None, duration_ms: int = None,
            extra: Dict[str, Any] = None):

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "service": self.service_name,
            "request_id": f"req-{uuid.uuid4().hex[:8]}",
            "action": action,
            "message": message
        }

        # Add optional fields only if provided
        if user:
            log_entry["user"] = user
        if duration_ms is not None:
            log_entry["duration_ms"] = duration_ms
        if extra:
            log_entry["extra"] = extra

        print(json.dumps(log_entry))

    def info(self, action: str, message: str, **kwargs):
        self.log("INFO", action, message, **kwargs)

    def warn(self, action: str, message: str, **kwargs):
        self.log("WARN", action, message, **kwargs)

    def error(self, action: str, message: str, **kwargs):
        self.log("ERROR", action, message, **kwargs)

# Global logger instances
user_logger = BaseLogger("user_service")
order_logger = BaseLogger("order_service")
inventory_logger = BaseLogger("inventory_service")
```

### **Base Request Middleware**
```python
# middleware/base_request_logging.py
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class BaseRequestMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Get user from JWT if available (simplified)
        user = self.get_user_from_jwt(request)

        response = await call_next(request)

        duration_ms = int((time.time() - start_time) * 1000)
        action = self.get_action(request.method, str(request.url.path))

        level = "ERROR" if response.status_code >= 500 else "WARN" if response.status_code >= 400 else "INFO"

        self.logger.log(
            level=level,
            action=action,
            message=f"{request.method} {request.url.path}",
            user=user,
            duration_ms=duration_ms,
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "status": response.status_code
            }
        )

        return response

    def get_user_from_jwt(self, request: Request) -> str:
        # Simple JWT user extraction
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # Extract user from JWT - simplified
            # In real implementation, decode JWT properly
            return "user_from_jwt"  # placeholder
        return None

    def get_action(self, method: str, path: str) -> str:
        # Simple action mapping
        if "/auth/login" in path:
            return "login"
        elif "/auth/register" in path:
            return "register"
        elif "/orders" in path and method == "POST":
            return "create_order"
        elif "/orders" in path and method == "GET":
            return "list_orders"
        elif "/balance" in path:
            return "balance_operation"
        elif "/health" in path:
            return "health_check"
        else:
            return f"{method.lower()}_request"
```

## 📊 Base Usage Examples

### **User Service Examples**
```python
from common.base_logger import user_logger

# Login success
user_logger.info(
    action="login",
    message="User logged in successfully",
    user="john_doe",
    duration_ms=45,
    extra={"method": "password"}
)

# Login failure
user_logger.warn(
    action="login_failed",
    message="Invalid password attempt",
    extra={"username": "john_doe", "ip": "192.168.1.100"}
)

# Balance deposit
user_logger.info(
    action="deposit",
    message="Balance deposit processed",
    user="john_doe",
    extra={"amount": 1000.0, "new_balance": 1500.0}
)
```

### **Order Service Examples**
```python
from common.base_logger import order_logger

# Order creation
order_logger.info(
    action="create_order",
    message="Market buy order created",
    user="john_doe",
    duration_ms=120,
    extra={
        "asset": "BTC",
        "amount": 0.1,
        "cost": 5000.0
    }
)

# Order failure
order_logger.error(
    action="create_order_failed",
    message="Insufficient balance for order",
    user="john_doe",
    extra={
        "asset": "BTC",
        "required": 5000.0,
        "available": 1000.0
    }
)
```

### **Security Events**
```python
# Failed authentication
user_logger.warn(
    action="auth_failed",
    message="Authentication failed - invalid credentials",
    extra={
        "username": "attempted_user",
        "ip": "192.168.1.100",
        "attempts": 3
    }
)

# Suspicious activity
user_logger.warn(
    action="suspicious_activity",
    message="Multiple failed login attempts",
    extra={
        "username": "john_doe",
        "attempts_in_hour": 10,
        "ip": "192.168.1.100"
    }
)
```

## 🔍 Base Log Analysis

### **Basic Queries**
```bash
# Find all errors
grep '"level":"ERROR"' logs/*.json

# Find login attempts
grep '"action":"login"' logs/*.json

# Find slow requests
grep '"duration_ms"' logs/*.json | jq 'select(.duration_ms > 1000)'

# Find specific user activity
grep '"user":"john_doe"' logs/*.json

# Security events
grep '"action":"auth_failed"' logs/*.json
```

### **Base Monitoring Alerts**
```bash
# Count failed logins in last hour
grep '"action":"login_failed"' logs/$(date +%Y-%m-%d).json | wc -l

# Find errors in last 10 minutes
grep '"level":"ERROR"' logs/*.json | grep $(date -d "10 minutes ago" +%H:%M)
```

## 📋 Implementation Steps

### **1. Gateway Setup**
```bash
# Add to your Gateway main.go
router.Use(middleware.BaseLoggingMiddleware())
```

### **2. FastAPI Services Setup**
```python
# Add to each service's main.py
from middleware.base_request_logging import BaseRequestMiddleware
from common.base_logger import user_logger

app = FastAPI()
app.add_middleware(BaseRequestMiddleware, logger=user_logger)
```

### **3. Business Logic Logging**
```python
# Add logging to important operations
def create_user(user_data):
    try:
        # ... business logic ...
        user_logger.info("user_created", "New user registered",
                         user=user_data.username)
    except Exception as e:
        user_logger.error("user_creation_failed", str(e),
                          extra={"username": user_data.username})
```

## 🎯 What This Gets You

### **For Learning**
- Good logging patterns for your portfolio
- Simple but professional structure
- Easy to explain in interviews

### **For Debugging**
- Quick request tracking across services
- Easy error identification
- Performance monitoring

### **For Monitoring**
- Ready for log aggregation systems
- Simple alert creation
- Business metrics tracking

## 📋 Quick Decision Log

| Date | Component | Decision | Why | Impact | Status |
|------|-----------|----------|-----|---------|---------|
| 8/20 | Logging Format | JSON structured logging | Machine readable, easy parsing | High | ✅ Done |
| 8/20 | Correlation IDs | Request ID per request | Cross-service request tracking | High | ✅ Done |
| 8/20 | Log Levels | INFO, WARN, ERROR | Standard levels, easy filtering | Medium | ✅ Done |
| 8/20 | Security Events | Dedicated security logging | Security monitoring and audit | High | ✅ Done |
| 8/20 | Performance | Duration tracking | Performance monitoring | Medium | ✅ Done |

---

**🎯 This base approach gives you 80% of the benefits with 20% of the complexity - perfect for a personal project that still demonstrates professional practices!**
