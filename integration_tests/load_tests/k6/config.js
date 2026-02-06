/**
 * k6 Load Test Configuration
 * Reads same environment variables as integration_tests/config/constants.py
 * No generator needed - directly uses env vars like Python config does
 * 
 * Reuses same logic as integration tests for consistency
 * Matches: integration_tests/config/constants.py (ExternalServices class)
 */

// Gateway Configuration (matches integration_tests/config/constants.py)
// Reads same env vars: GATEWAY_HOST, GATEWAY_PORT (same defaults)
export const GATEWAY_HOST = __ENV.GATEWAY_HOST || "localhost";
export const GATEWAY_PORT = __ENV.GATEWAY_PORT || "8080";
export const BASE_URL = `http://${GATEWAY_HOST}:${GATEWAY_PORT}`;
export const API_BASE = `${BASE_URL}/api/v1`;

// API Endpoints (matches integration_tests/config/constants.py APIEndpoints)
// These match Python constants exactly - just the path part (API_BASE is added separately)
export const ENDPOINTS = {
    // Health endpoints (matches APIEndpoints.GATEWAY_HEALTH)
    HEALTH: "/health",
    
    // Auth endpoints (matches APIEndpoints in constants.py)
    AUTH_LOGIN: "/auth/login",
    AUTH_REGISTER: "/auth/register",
    AUTH_PROFILE: "/auth/profile",
    AUTH_LOGOUT: "/auth/logout",
    
    // Inventory endpoints (matches APIEndpoints.INVENTORY_*)
    INVENTORY_ASSETS: "/inventory/assets",
    INVENTORY_ASSET_BY_ID: "/inventory/assets/{asset_id}",
    
    // Order endpoints (matches APIEndpoints.ORDERS_*, PORTFOLIO_GET)
    ORDERS: "/orders",
    ORDERS_CREATE: "/orders",
    ORDER_BY_ID: "/orders/{order_id}",
    PORTFOLIO: "/portfolio",
    
    // Balance endpoints (matches APIEndpoints.BALANCE_*)
    BALANCE: "/balance",
    BALANCE_DEPOSIT: "/balance/deposit",
    BALANCE_WITHDRAW: "/balance/withdraw",
    BALANCE_TRANSACTIONS: "/balance/transactions",
    ASSET_BALANCE_BY_ID: "/balance/asset/{asset_id}",
    ASSET_TRANSACTIONS_BY_ID: "/assets/{asset_id}/transactions",
};
