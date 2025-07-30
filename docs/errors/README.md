# API Error Documentation

This directory contains documentation for all standard API errors used in the Order Processor system. All errors follow the [RFC 7807 Problem Details](https://tools.ietf.org/html/rfc7807) standard.

## Error Types

| Error Type | HTTP Status | Documentation |
|------------|-------------|---------------|
| Validation Error | 422 | [validation-error.md](./validation-error.md) |
| Authentication Error | 401 | [authentication-error.md](./authentication-error.md) |
| Resource Not Found | 404 | [resource-not-found.md](./resource-not-found.md) |
| Resource Exists | 409 | [resource-exists.md](./resource-exists.md) |
| Internal Server Error | 500 | [internal-error.md](./internal-error.md) |

## Standard Response Format

All errors follow this RFC 7807 format:

```json
{
  "type": "https://github.com/yifeng2019uwb/cloud-native-order-processor/blob/main/docs/errors/{error-type}.md",
  "title": "Error Title",
  "status": 422,
  "detail": "Human-readable error message",
  "instance": "/api/v1/endpoint"
}
```

## Additional Fields

Some error types include additional fields:

- **Validation Errors**: Include `errors` array with field-specific details
- **Resource Errors**: May include resource-specific context
- **Authentication Errors**: May include token-specific information

## Implementation

These error types are implemented in the `services/exception/` package and used across all services to provide consistent error responses.

## GitHub URLs

All error documentation URLs point to this GitHub repository for easy access and maintenance.