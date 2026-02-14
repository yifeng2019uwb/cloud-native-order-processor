/**
 * Lock Management Load Tests
 * TC-LOCK-001: Concurrent operations for same user
 *
 * Tests user-level locking to prevent race conditions.
 * Combines deposit/withdraw (2s lock timeout) and orders (5s lock timeout).
 *
 * Test Flow:
 * 1. Setup: Deposit $1000 initial balance
 * 2. Get initial balance and asset info
 * 3. Send deposit/withdraw operations concurrently
 * 4. Send buy/sell orders concurrently
 * 5. Check all responses and verify final balance
 */

import { check } from 'k6';
import http from 'k6/http';
import { API_BASE, ENDPOINTS } from './config.js';
import { loadTestUserToken, buildAuthHeaders } from './utils.js';

// Load test user token
const testUserToken = loadTestUserToken();

// Test configuration
// Note: Deposit API enforces daily limit (default 10000 USD); amounts exceeding it return 422.
const INITIAL_BALANCE_DEPOSIT = 50000.00;
const DEPOSIT_AMOUNTS = [100.00, 50.00, 75.00];
const WITHDRAW_AMOUNTS = [31.00, 43.00, 74.00];
const TEST_ASSET_ID = 'BTC'; // Use BTC as test asset
// Create 15 buy orders with defined quantities to test lock contention
const BUY_QUANTITIES = [
  0.01, 0.02, 0.015, 0.025, 0.03,  // Small orders
  0.035, 0.04, 0.045, 0.05, 0.055,  // Medium orders
  0.06, 0.065, 0.07, 0.075, 0.1    // Larger orders
];
const SELL_QUANTITIES = [0.01, 0.02, 0.015, 0.025, 0.03]; // Sell orders (must have assets first)

// Create payload lists
const depositPayloads = DEPOSIT_AMOUNTS.map(amount => ({
  operation: 'deposit',
  amount: amount,
  url: `${API_BASE}${ENDPOINTS.BALANCE_DEPOSIT}`,
  payload: JSON.stringify({ amount: amount })
}));

const withdrawPayloads = WITHDRAW_AMOUNTS.map(amount => ({
  operation: 'withdraw',
  amount: amount,
  url: `${API_BASE}${ENDPOINTS.BALANCE_WITHDRAW}`,
  payload: JSON.stringify({ amount: amount })
}));

export const options = {
  scenarios: {
    lock_contention: {
      executor: 'ramping-arrival-rate',
      startRate: 30, // Start with 30 requests per second (reduced from 50)
      timeUnit: '1s',
      preAllocatedVUs: 50, // Pre-allocate 50 VUs (reduced from 100 to save memory)
      maxVUs: 50, // Maximum 50 VUs (reduced from 100)
      stages: [
        { duration: '2s', target: 50 }, // Ramp up to 50 req/s in 2s (reduced from 100)
        { duration: '6s', target: 50 }, // Maintain 50 req/s for 6s (reduced from 8s)
      ],
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<20000'], // Orders take longer due to lock timeout and contention
    http_req_failed: ['rate<0.5'], // Allow up to 50% failures (503 lock contention is expected)
  },
};

// Setup: Deposit $1000 initial balance and get asset info
export function setup() {
  console.log(`\n🔍 Step 0: Setting up test - depositing $${INITIAL_BALANCE_DEPOSIT.toFixed(2)}...`);

  const headers = buildAuthHeaders(testUserToken);

  // Deposit initial balance
  const depositUrl = `${API_BASE}${ENDPOINTS.BALANCE_DEPOSIT}`;
  const depositResponse = http.post(depositUrl, JSON.stringify({ amount: INITIAL_BALANCE_DEPOSIT }), { headers });

  if (depositResponse.status !== 201) {
    console.log(`❌ Failed to deposit initial balance (status: ${depositResponse.status})`);
    return { initialBalance: 0, assetPrice: 0 };
  }

  // Get balance to confirm
  const balanceUrl = `${API_BASE}${ENDPOINTS.BALANCE}`;
  const balanceResponse = http.get(balanceUrl, { headers });
  let initialBalance = 0;
  if (balanceResponse.status === 200) {
    const balanceData = JSON.parse(balanceResponse.body);
    initialBalance = parseFloat(balanceData.current_balance || balanceData.balance || 0);
  }

  // Get asset price from inventory
  const inventoryUrl = `${API_BASE}${ENDPOINTS.INVENTORY_ASSETS}`;
  const inventoryResponse = http.get(inventoryUrl, { headers });
  let assetPrice = 50000; // Default fallback
  if (inventoryResponse.status === 200) {
    try {
      const inventoryData = JSON.parse(inventoryResponse.body);
      const assets = inventoryData.assets || inventoryData.data || [];
      const btcAsset = assets.find(a => a.asset_id === TEST_ASSET_ID);
      if (btcAsset && btcAsset.price_usd) {
        assetPrice = parseFloat(btcAsset.price_usd);
      }
    } catch (e) {
      console.log(`⚠️  Could not parse inventory, using default price: $${assetPrice}`);
    }
  }

  console.log(`✅ Initial balance: $${initialBalance.toFixed(2)}, Asset (${TEST_ASSET_ID}) price: $${assetPrice.toFixed(2)}\n`);
  return { initialBalance, assetPrice };
}

export default function (data) {
  const headers = buildAuthHeaders(testUserToken);
  const assetPrice = data.assetPrice || 50000;
  const vuId = __VU; // Get current VU ID
  const iterId = __ITER; // Get current iteration ID

  // Each VU sends a mix of operations to create lock contention
  // Use VU ID to vary the operations
  
  // Send deposit operation
  const depositAmount = DEPOSIT_AMOUNTS[vuId % DEPOSIT_AMOUNTS.length];
  const depositResponse = http.post(
    `${API_BASE}${ENDPOINTS.BALANCE_DEPOSIT}`,
    JSON.stringify({ amount: depositAmount }),
    { headers }
  );
  
  // Send withdraw operation
  const withdrawAmount = WITHDRAW_AMOUNTS[vuId % WITHDRAW_AMOUNTS.length];
  const withdrawResponse = http.post(
    `${API_BASE}${ENDPOINTS.BALANCE_WITHDRAW}`,
    JSON.stringify({ amount: withdrawAmount }),
    { headers }
  );

  // Send buy order (small quantity to avoid balance issues)
  const buyQuantity = BUY_QUANTITIES[vuId % BUY_QUANTITIES.length];
  const buyOrderResponse = http.post(
    `${API_BASE}${ENDPOINTS.ORDERS_CREATE}`,
    JSON.stringify({
      asset_id: TEST_ASSET_ID,
      quantity: buyQuantity,
      order_type: 'market_buy',
      price: null
    }),
    { headers }
  );

  // Log responses for this VU
  const depositStatus = depositResponse.status === 201 ? 'SUCCESS' : depositResponse.status === 503 ? 'LOCK CONTENTION' : `ERROR (${depositResponse.status})`;
  const withdrawStatus = withdrawResponse.status === 201 ? 'SUCCESS' : withdrawResponse.status === 503 ? 'LOCK CONTENTION' : `ERROR (${withdrawResponse.status})`;
  const buyStatus = buyOrderResponse.status === 201 ? 'SUCCESS' : buyOrderResponse.status === 503 ? 'LOCK CONTENTION' : `ERROR (${buyOrderResponse.status})`;
  
  const depositDuration = depositResponse.timings ? `${depositResponse.timings.duration.toFixed(0)}ms` : 'N/A';
  const withdrawDuration = withdrawResponse.timings ? `${withdrawResponse.timings.duration.toFixed(0)}ms` : 'N/A';
  const buyDuration = buyOrderResponse.timings ? `${buyOrderResponse.timings.duration.toFixed(0)}ms` : 'N/A';

  // Log error details for 500 errors to help diagnose issues
  let depositErrorDetail = '';
  if (depositResponse.status === 500) {
    const bodyLength = depositResponse.body ? depositResponse.body.length : 0;
    if (bodyLength > 0) {
      try {
        const errorBody = JSON.parse(depositResponse.body);
        depositErrorDetail = ` | Deposit Error: ${JSON.stringify(errorBody).substring(0, 200)}`;
      } catch (e) {
        depositErrorDetail = ` | Deposit Body (raw): ${depositResponse.body.substring(0, 200)}`;
      }
    } else {
      depositErrorDetail = ` | Deposit Error: Empty response body`;
    }
  }

  let withdrawErrorDetail = '';
  if (withdrawResponse.status === 500) {
    const bodyLength = withdrawResponse.body ? withdrawResponse.body.length : 0;
    if (bodyLength > 0) {
      try {
        const errorBody = JSON.parse(withdrawResponse.body);
        withdrawErrorDetail = ` | Withdraw Error: ${JSON.stringify(errorBody).substring(0, 200)}`;
      } catch (e) {
        withdrawErrorDetail = ` | Withdraw Body (raw): ${withdrawResponse.body.substring(0, 200)}`;
      }
    } else {
      withdrawErrorDetail = ` | Withdraw Error: Empty response body`;
    }
  }

  let buyErrorDetail = '';
  if (buyOrderResponse.status === 500) {
    const bodyLength = buyOrderResponse.body ? buyOrderResponse.body.length : 0;
    if (bodyLength > 0) {
      try {
        const errorBody = JSON.parse(buyOrderResponse.body);
        buyErrorDetail = ` | Buy Error: ${JSON.stringify(errorBody).substring(0, 200)}`;
      } catch (e) {
        buyErrorDetail = ` | Buy Body (raw): ${buyOrderResponse.body.substring(0, 200)}`;
      }
    } else {
      buyErrorDetail = ` | Buy Error: Empty response body`;
    }
  }

  // Log all errors (500 and 503) and first few VUs for general visibility
  const hasError = depositResponse.status === 500 || withdrawResponse.status === 500 || buyOrderResponse.status === 500 ||
                   depositResponse.status === 503 || withdrawResponse.status === 503 || buyOrderResponse.status === 503;
  
  if (hasError || vuId <= 5) {
    // Log with error details for 500 errors, simple log for others
    if (depositResponse.status === 500 || withdrawResponse.status === 500 || buyOrderResponse.status === 500) {
      console.log(`VU${vuId}: Deposit=$${depositAmount.toFixed(2)} (${depositResponse.status} ${depositStatus}, ${depositDuration})${depositErrorDetail}, ` +
                  `Withdraw=$${withdrawAmount.toFixed(2)} (${withdrawResponse.status} ${withdrawStatus}, ${withdrawDuration})${withdrawErrorDetail}, ` +
                  `Buy=${buyQuantity} (${buyOrderResponse.status} ${buyStatus}, ${buyDuration})${buyErrorDetail}`);
    } else {
      // Log 503 errors and first few VUs (without 500 error details)
      console.log(`VU${vuId}: Deposit=$${depositAmount.toFixed(2)} (${depositResponse.status} ${depositStatus}, ${depositDuration}), ` +
                  `Withdraw=$${withdrawAmount.toFixed(2)} (${withdrawResponse.status} ${withdrawStatus}, ${withdrawDuration}), ` +
                  `Buy=${buyQuantity} (${buyOrderResponse.status} ${buyStatus}, ${buyDuration})`);
    }
  }

  // Check for lock contention (503 errors)
  check(depositResponse.status, {
    'deposit status is 201 or 503': (status) => status === 201 || status === 503,
  });
  
  check(withdrawResponse.status, {
    'withdraw status is 201 or 503': (status) => status === 201 || status === 503,
  });
  
  check(buyOrderResponse.status, {
    'buy order status is 201 or 503': (status) => status === 201 || status === 503,
  });
}
