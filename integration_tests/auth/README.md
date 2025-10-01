# Centralized Authentication Requirement Tests

This package verifies that protected endpoints require authentication.

## Purpose

**Test auth requirements ONCE** - verify protected endpoints return 401 without authentication.

Individual API tests will:
- ✅ **Use valid authentication** (setup tokens in tests)
- ✅ **Focus on business logic** (validation, edge cases, data correctness)
- ✅ **Implicitly test auth** (tests fail if auth is broken)
- ❌ **NOT test auth explicitly** (no test_unauthorized, test_invalid_token, etc.)

## What is tested here

### All Protected Services (User & Order)
1. **No token** - ❌ DISABLED - endpoints return 403 (BUG: should be 401, see GATEWAY-002)
2. **Invalid token** - ✅ ACTIVE - endpoints return 401

### Inventory Service
1. **Public access** - ✅ ACTIVE - endpoints are accessible without auth (no 401)

**⚠️ Known Issue (GATEWAY-002)**: ALL protected services return 403 instead of 401 for missing tokens. This is a critical gateway bug that needs fixing. All services should return 401 for authentication failures.

**Tests Currently Disabled**:
- `test_user_service_no_token()` - Disabled until GATEWAY-002 is fixed
- `test_order_service_no_token()` - Disabled until GATEWAY-002 is fixed

**Active Tests**:
- `test_user_service_invalid_token()` - ✅ Passing
- `test_order_service_invalid_token()` - ✅ Passing
- `test_inventory_service_is_public()` - ✅ Passing

## Test Coverage

### User Service Endpoints
- `/api/v1/auth/profile` - User profile (requires auth)
- `/api/v1/balance` - User balance (requires auth)
- `/api/v1/balance/transactions` - Transaction history (requires auth)

### Order Service Endpoints
- `/api/v1/orders` - List orders (requires auth)
- `/api/v1/portfolio/{user_id}` - User portfolio (requires auth)
- `/api/v1/asset-balances` - Asset balances (requires auth)
- `/api/v1/assets/{asset_id}/transactions` - Asset transactions (requires auth)

### Inventory Service Endpoints
- `/api/v1/inventory/assets` - List assets (public)
- `/api/v1/inventory/assets/{asset_id}` - Get asset (public)

## Running Tests

```bash
# Run from integration_tests directory
python3 auth/test_gateway_auth.py
```

## What Individual Endpoint Tests Should Focus On

Individual endpoint tests (in `user_services/`, `order_service/`, `inventory_service/`) should **NOT** repeat auth testing. Instead, they should focus on:

1. **Business logic validation**
   - Invalid amounts, quantities, dates
   - Business rule violations
   - Data constraints

2. **Edge cases**
   - Empty inputs, very long inputs
   - Boundary values
   - Special characters

3. **Data correctness**
   - Response schema validation
   - Correct calculations
   - Proper data transformations

4. **API-specific behavior**
   - Pagination
   - Filtering
   - Sorting
   - Query parameters

**Auth testing is DONE HERE, not in individual endpoint tests.**
