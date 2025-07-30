# Authentication Error

**Type:** `https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/authentication-error.md`

**HTTP Status:** `401 Unauthorized`

## Description

This error occurs when authentication fails. The user's credentials are invalid, missing, or the authentication token has expired.

## Common Causes

- Invalid username/password combination
- Missing or invalid JWT token
- Expired authentication token
- Malformed authorization header
- Invalid token signature

## Response Format

```json
{
  "type": "https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/authentication-error.md",
  "title": "Authentication Error",
  "status": 401,
  "detail": "Invalid credentials",
  "instance": "/api/v1/auth/login"
}
```

## How to Fix

1. **For Login Requests:**
   - Verify username and password are correct
   - Check for typos in credentials
   - Ensure account exists and is active

2. **For Protected Endpoints:**
   - Include valid JWT token in Authorization header
   - Ensure token format: `Bearer <token>`
   - Check if token has expired
   - Re-authenticate if token is invalid

## Examples

### Invalid Credentials
```json
{
  "type": "https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/authentication-error.md",
  "title": "Authentication Error",
  "status": 401,
  "detail": "Invalid username or password",
  "instance": "/api/v1/auth/login"
}
```

### Missing Token
```json
{
  "type": "https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/authentication-error.md",
  "title": "Authentication Error",
  "status": 401,
  "detail": "Missing or invalid authorization token",
  "instance": "/api/v1/auth/me"
}
```

### Expired Token
```json
{
  "type": "https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/authentication-error.md",
  "title": "Authentication Error",
  "status": 401,
  "detail": "Token has expired",
  "instance": "/api/v1/auth/me"
}
```