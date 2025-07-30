# Resource Not Found Error

**Type:** `https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/resource-not-found.md`

**HTTP Status:** `404 Not Found`

## Description

This error occurs when the requested resource does not exist. The resource may have been deleted, moved, or the identifier provided is incorrect.

## Common Causes

- Invalid resource ID
- Resource has been deleted
- Incorrect URL path
- Resource belongs to different user/account
- Typo in resource identifier

## Response Format

```json
{
  "type": "https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/resource-not-found.md",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "The requested resource was not found",
  "instance": "/api/v1/users/12345"
}
```

## How to Fix

1. **Verify Resource ID:**
   - Check if the resource ID is correct
   - Ensure the ID format is valid
   - Verify the resource exists

2. **Check Permissions:**
   - Ensure you have access to the resource
   - Verify the resource belongs to your account
   - Check if authentication is required

3. **URL Issues:**
   - Verify the API endpoint URL is correct
   - Check for typos in the path
   - Ensure you're using the correct API version

## Examples

### User Not Found
```json
{
  "type": "https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/resource-not-found.md",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "User '12345' not found",
  "instance": "/api/v1/users/12345"
}
```

### Asset Not Found
```json
{
  "type": "https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/resource-not-found.md",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "Asset 'BTC' not found",
  "instance": "/api/v1/assets/BTC"
}
```