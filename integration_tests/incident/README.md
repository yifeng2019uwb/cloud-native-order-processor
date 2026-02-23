# Incident response integration tests

Tests for incident/security features (e.g. **IP block SEC-011**). All integration tests are **external/black-box**: they call only the gateway; they do not access Redis or any internal service.

## IP block (SEC-011)

**What we test from outside:**

1. **Init** – Create a user (register + login + logout) via the gateway.
2. **Step 3** – Same user, wrong password: 5 failed logins, then the **6th** request must get **403** (IP blocked). The gateway records each 401 from POST /auth/login and sets `ip_block:<ip>` in Redis after 5 failures in a 1-day window.
3. **Step 4** – Wait 5 minutes for the block TTL to expire, then login again with the correct password; must get **200** (block expired, login works again).

**Run individually:**

```bash
cd integration_tests
python3 incident/test_ip_block.py
```

**Run via test runner:** `./run_all_tests.sh incident` or include in `./run_all_tests.sh all`.

**Note:** Step 4 uses a 5-minute sleep, so the incident suite takes at least 5 minutes when run in full.
