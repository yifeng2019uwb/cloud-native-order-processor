// API Configuration Constants
export const API_CONFIG = {
  // Base API URL - can be configured via VITE_REACT_APP_API_BASE_URL environment variable
  BASE_URL: import.meta.env.VITE_REACT_APP_API_BASE_URL || 'http://localhost:8080',

  // API Version
  API_VERSION: 'v1',

  // Service-specific base paths
  AUTH_BASE: '/api/v1/auth',
  BALANCE_BASE: '/api/v1/balance',
  INVENTORY_BASE: '/api/v1/inventory',
  ORDERS_BASE: '/api/v1/orders',
  PORTFOLIO_BASE: '/api/v1/portfolio',
  ASSETS_BASE: '/api/v1/assets',

  // Health check endpoints
  HEALTH_CHECK: '/health',
  GATEWAY_HEALTH: '/api/v1/health',
} as const;

// Helper function to build full API URLs
export const buildApiUrl = (basePath: string): string => {
  return `${API_CONFIG.BASE_URL}${basePath}`;
};

// Pre-built API URLs for each service
export const API_URLS = {
  AUTH: buildApiUrl(API_CONFIG.AUTH_BASE),
  BALANCE: buildApiUrl(API_CONFIG.BALANCE_BASE),
  INVENTORY: buildApiUrl(API_CONFIG.INVENTORY_BASE),
  ORDERS: buildApiUrl(API_CONFIG.ORDERS_BASE),
  PORTFOLIO: buildApiUrl(API_CONFIG.PORTFOLIO_BASE),
  ASSETS: buildApiUrl(API_CONFIG.ASSETS_BASE),
  HEALTH: buildApiUrl(API_CONFIG.HEALTH_CHECK),
  GATEWAY_HEALTH: buildApiUrl(API_CONFIG.GATEWAY_HEALTH),
} as const;

// For production, you can override BASE_URL by setting environment variable
// VITE_REACT_APP_API_BASE_URL=https://api.yourdomain.com
