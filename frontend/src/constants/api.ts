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

// API Path Constants - No hardcoding allowed
export const API_PATHS = {
  // Inventory service
  INVENTORY_ASSETS: '/assets',
  INVENTORY_ASSET_BY_ID: (assetId: string) => `/assets/${assetId}`,

  // Portfolio service
  PORTFOLIO: '',

  // Balance service
  BALANCE: '/balance',
  BALANCE_ASSET: (assetId: string) => `/balance/asset/${assetId}`,

  // Order service
  ORDERS: '',
  ORDER_BY_ID: (orderId: string) => `/orders/${orderId}`,

  // Auth service
  AUTH_LOGIN: '/auth/login',
  AUTH_REGISTER: '/auth/register',
  AUTH_PROFILE: '/auth/profile',
  AUTH_LOGOUT: '/auth/logout',
} as const;

// Helper function to build query string
export const buildQueryString = (params: Record<string, any>): string => {
  const queryParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      queryParams.append(key, value.toString());
    }
  });
  const queryString = queryParams.toString();
  return queryString ? `?${queryString}` : '';
};

// For production, you can override BASE_URL by setting environment variable
// VITE_REACT_APP_API_BASE_URL=https://api.yourdomain.com
