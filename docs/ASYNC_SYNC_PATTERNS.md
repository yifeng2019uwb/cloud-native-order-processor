# Async/Sync Patterns Documentation

## What

**Async/Sync Pattern**: A design approach that uses async operations for data modification and sync operations for data reading across all CNOP services.

## Why

**Problem**: Race conditions occur when multiple requests try to modify the same user's data simultaneously (e.g., balance updates, order creation).

**Solution**: Use database-level locking to ensure atomic operations and prevent data corruption.

## How

### WRITE OPERATIONS (async)
- **What**: All operations that modify data (deposit, withdraw, create_order)
- **Why**: Need locking to prevent race conditions
- **How**: Use `UserLock` context manager with database locks

### READ OPERATIONS (sync)
- **What**: All read-only operations (get_balance, get_orders, get_assets)
- **Why**: No data modification, no locks needed
- **How**: Simple sync functions, FastAPI handles thread pool

### Locking Strategy
- **What**: User-level database locks using `LOCK` as Sort Key (SK)
- **Why**: Prevents concurrent modifications to same user's data
- **How**: DynamoDB conditional writes with lock expiration

### Lock Timeouts
- **Deposit/Withdraw**: 5 seconds
- **Order Operations**: 5 seconds
- **Read Operations**: 1 second (optional)

## Code Pattern

```python
# WRITE OPERATION (async)
async def deposit_funds(...) -> DepositResponse:
    """
    ASYNC OPERATION: Modifies balance, requires user lock for atomicity.
    Lock timeout: 5 seconds (LOCK_TIMEOUTS['deposit'])
    """
    async with UserLock(username, "deposit", LOCK_TIMEOUTS["deposit"]):
        # Atomic balance update
        pass

# READ OPERATION (sync)
def get_balance(...) -> BalanceResponse:
    """
    SYNC OPERATION: Read-only, no locks needed.
    FastAPI runs in thread pool automatically.
    """
    # Simple read operation
    pass
```

## Decision Rule

```
Modifies data? → ASYNC + Lock
Reads data? → SYNC
```
