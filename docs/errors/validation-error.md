# Validation Error

**Type:** `https://github.com/yourusername/cloud-native-order-processor/blob/main/docs/errors/validation-error.md`

**HTTP Status:** `422 Unprocessable Entity`

## Description

This error occurs when the request data fails validation rules. The request body, query parameters, or path parameters contain invalid or malformed data.

## Common Causes

- Missing required fields
- Invalid data formats (email, date, etc.)
- Data length violations (too short/long)
- Invalid enum values
- Malformed JSON
- Type mismatches

## Response Format

```json
{
  "type": "https://github.com/yourusername/cloud-native-order-processor/blob/main/docs/errors/validation-error.md",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request body contains invalid data",
  "instance": "/api/v1/users",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "value": "invalid-email"
    },
    {
      "field": "password",
      "message": "Password must be at least 12 characters",
      "value": "short"
    }
  ]
}
```

## Field-Specific Errors

The `errors` array contains detailed information about each validation failure:

- `field`: The name of the field that failed validation
- `message`: Human-readable error message
- `value`: The invalid value that was provided (optional)

## How to Fix

1. Review the `errors` array for specific field issues
2. Check the field requirements in the API documentation
3. Ensure all required fields are provided
4. Validate data formats before sending
5. Check field length constraints

## Examples

### Missing Required Field
```json
{
  "type": "https://github.com/yourusername/cloud-native-order-processor/blob/main/docs/errors/validation-error.md",
  "title": "Validation Error",
  "status": 422,
  "detail": "Missing required field: email",
  "instance": "/api/v1/auth/register",
  "errors": [
    {
      "field": "email",
      "message": "Email is required"
    }
  ]
}
```

### Invalid Email Format
```json
{
  "type": "https://github.com/yourusername/cloud-native-order-processor/blob/main/docs/errors/validation-error.md",
  "title": "Validation Error",
  "status": 422,
  "detail": "Invalid email format",
  "instance": "/api/v1/auth/register",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "value": "not-an-email"
    }
  ]
}
```