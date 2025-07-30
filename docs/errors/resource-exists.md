# Resource Exists Error

**Type:** `https://github.com/yourusername/cloud-native-order-processor/blob/main/docs/errors/resource-exists.md`

**HTTP Status:** `409 Conflict`

## Description

This error occurs when trying to create a resource that already exists. The resource cannot be created because it conflicts with an existing resource.

## Common Causes

- Username already taken
- Email already registered
- Duplicate resource creation
- Unique constraint violation
- Resource ID already exists

## Response Format

```json
{
  "type": "https://github.com/yourusername/cloud-native-order-processor/blob/main/docs/errors/resource-exists.md",
  "title": "Resource Already Exists",
  "status": 409,
  "detail": "A resource with this identifier already exists",
  "instance": "/api/v1/auth/register"
}
```

## How to Fix

1. **For Registration:**
   - Use a different username or email
   - Check if you already have an account
   - Try logging in instead of registering

2. **For Resource Creation:**
   - Use a unique identifier
   - Check if the resource already exists
   - Consider updating instead of creating

## Examples

### Username Already Exists
```json
{
  "type": "https://github.com/yourusername/cloud-native-order-processor/blob/main/docs/errors/resource-exists.md",
  "title": "Resource Already Exists",
  "status": 409,
  "detail": "Username 'john_doe' already exists",
  "instance": "/api/v1/auth/register"
}
```

### Email Already Registered
```json
{
  "type": "https://github.com/yourusername/cloud-native-order-processor/blob/main/docs/errors/resource-exists.md",
  "title": "Resource Already Exists",
  "status": 409,
  "detail": "Email 'john@example.com' is already registered",
  "instance": "/api/v1/auth/register"
}
```