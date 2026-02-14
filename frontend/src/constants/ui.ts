// UI String Constants
// Centralized location for all user-facing text to improve maintainability and enable internationalization

/** Max total order value (USD) per trade - must match backend constants.MAX_ORDER_VALUE_USD */
export const MAX_ORDER_VALUE_USD = 10000;

export const UI_STRINGS = {
  // Common Actions
  LOGIN: 'Login',
  REGISTER: 'Register',
  LOGOUT: 'Logout',
  SUBMIT: 'Submit',
  CANCEL: 'Cancel',
  CONFIRM: 'Confirm',
  BACK: 'Back',
  LOADING: 'Loading...',
  SAVE: 'Save',
  EDIT: 'Edit',
  DELETE: 'Delete',
  REFRESH: 'Refresh',

  // Navigation
  DASHBOARD: 'Dashboard',
  PORTFOLIO: 'Portfolio',
  TRADING: 'Trading',
  INVENTORY: 'Inventory',
  ACCOUNT: 'Account',
  PROFILE: 'Profile',

  // Headers and Titles
  ORDER_PROCESSOR_DASHBOARD: 'Order Processor Dashboard',
  PORTFOLIO_TITLE: 'Portfolio',
  PORTFOLIO_SUBTITLE: 'View your asset holdings and performance',
  TRADING_TITLE: 'Trading',
  TRADING_SUBTITLE: 'Buy and sell assets',
  ACCOUNT_SUBTITLE: 'Manage your account settings',
  PROFILE_SUBTITLE: 'Update your profile information',

  // Welcome Messages
  WELCOME_USER: 'Welcome, {username}!',
  WELCOME_BACK: 'Welcome back!',

  // Form Labels
  USERNAME: 'Username',
  PASSWORD: 'Password',
  EMAIL: 'Email',
  FIRST_NAME: 'First Name',
  LAST_NAME: 'Last Name',
  QUANTITY: 'Quantity',
  ORDER_TYPE: 'Order Type',
  ASSET: 'Asset',

  // Form Placeholders
  ENTER_USERNAME: 'Enter your username',
  ENTER_PASSWORD: 'Enter your password',
  ENTER_EMAIL: 'Enter your email',
  ENTER_FIRST_NAME: 'Enter your first name',
  ENTER_LAST_NAME: 'Enter your last name',
  ENTER_QUANTITY: 'Enter quantity',

  // Validation Messages
  USERNAME_REQUIRED: 'Username is required',
  PASSWORD_REQUIRED: 'Password is required',
  EMAIL_REQUIRED: 'Email is required',
  FIRST_NAME_REQUIRED: 'First name is required',
  LAST_NAME_REQUIRED: 'Last name is required',
  QUANTITY_REQUIRED: 'Quantity is required',
  INVALID_CREDENTIALS: 'Invalid username or password',
  LOGIN_FAILED: 'Login failed. Please check your credentials.',
  REGISTRATION_FAILED: 'Registration failed. Please try again.',

  // Account Summary
  ACCOUNT_SUMMARY: 'Account Summary',
  TOTAL_BALANCE: 'Total Balance',
  TOTAL_ASSET_VALUE: 'Total Asset Value',
  ASSET_HOLDINGS: 'Asset Holdings',
  RECENT_ORDERS: 'Recent Orders',

  // Portfolio
  CURRENT_PRICE: 'Current Price',
  MARKET_VALUE: 'Market Value',
  ALLOCATION: 'Allocation',
  TOTAL_VALUE: 'Total Value',
  NO_ASSETS: 'No assets in portfolio',
  PORTFOLIO_LOADING: 'Loading portfolio data...',
  PORTFOLIO_ERROR: 'Failed to load portfolio data',

  // Trading
  BUY: 'Buy',
  SELL: 'Sell',
  CREATE_ORDER: 'Create Order',
  TRADING_ERROR: 'Failed to load trading data',
  MARKET_BUY: 'Market Buy',
  MARKET_SELL: 'Market Sell',
  SELECT_ASSET: 'Select Asset',
  ORDER_CONFIRMATION: 'Order Confirmation',
  CONFIRM_ORDER: 'Confirm Order',
  ORDER_SUCCESS: 'Order placed successfully!',
  ORDER_FAILED: 'Failed to create order',
  INSUFFICIENT_BALANCE: 'Insufficient balance for this order',
  NO_ASSETS_AVAILABLE: 'No assets available for trading',
  ORDER_MAX_VALUE_EXCEEDED: 'Order total exceeds maximum ($10,000)',

  // Transaction History
  TRANSACTION_HISTORY: 'Transaction History',
  DATE: 'Date',
  TYPE: 'Type',
  PRICE: 'Price',
  STATUS: 'Status',
  NO_TRANSACTIONS: 'No transactions found',
  TRANSACTION_LOADING: 'Loading transaction history...',
  TRANSACTION_ERROR: 'Failed to load transaction history',

  // Asset Details
  ASSET_DETAILS: 'Asset Details',
  MARKET_CAP: 'Market Cap',
  VOLUME_24H: '24h Volume',
  PRICE_CHANGE_24H: '24h Price Change',
  ASSET_NOT_FOUND: 'Asset not found',
  ASSET_LOADING: 'Loading asset details...',
  ASSET_ERROR: 'Failed to load asset details',

  // Error Messages
  NETWORK_ERROR: 'Network error occurred',
  SERVER_ERROR: 'Server error occurred',
  UNAUTHORIZED: 'Unauthorized access',
  FORBIDDEN: 'Access forbidden',
  NOT_FOUND: 'Resource not found',
  VALIDATION_ERROR: 'Validation error',
  UNKNOWN_ERROR: 'An unknown error occurred',

  // Success Messages
  SUCCESS: 'Success',
  OPERATION_SUCCESSFUL: 'Operation completed successfully',
  DATA_SAVED: 'Data saved successfully',
  DATA_UPDATED: 'Data updated successfully',
  DATA_DELETED: 'Data deleted successfully',

  // Loading States
  LOADING_DATA: 'Loading data...',
  LOADING_USER_DATA: 'Loading user data...',
  PROCESSING: 'Processing...',
  SAVING: 'Saving...',
  UPDATING: 'Updating...',

  // Empty States
  NO_DATA: 'No data available',
  NO_RESULTS: 'No results found',
  EMPTY_PORTFOLIO: 'Your portfolio is empty',
  EMPTY_ORDERS: 'No orders found',
  EMPTY_TRANSACTIONS: 'No transactions found',

  // Confirmation Messages
  CONFIRM_DELETE: 'Are you sure you want to delete this item?',
  CONFIRM_LOGOUT: 'Are you sure you want to logout?',
  CONFIRM_ORDER_CANCEL: 'Are you sure you want to cancel this order?',

  // Marketing Consent
  MARKETING_CONSENT: 'I agree to receive marketing emails',
  TERMS_AND_CONDITIONS: 'I agree to the Terms and Conditions',
  PRIVACY_POLICY: 'Privacy Policy',

  // Registration Success
  REGISTRATION_SUCCESS: 'Registration successful! Please login to continue.',
  REGISTRATION_SUCCESS_TITLE: 'Account Created',
  REGISTRATION_SUCCESS_MESSAGE: 'Your account has been created successfully. You can now login with your credentials.',

  // Order Types
  ORDER_TYPE_MARKET_BUY: 'Market Buy',
  ORDER_TYPE_MARKET_SELL: 'Market Sell',
  ORDER_TYPE_LIMIT_BUY: 'Limit Buy',
  ORDER_TYPE_LIMIT_SELL: 'Limit Sell',

  // Transaction Types
  TRANSACTION_TYPE_BUY: 'Buy',
  TRANSACTION_TYPE_SELL: 'Sell',
  TRANSACTION_TYPE_DEPOSIT: 'Deposit',
  TRANSACTION_TYPE_WITHDRAWAL: 'Withdrawal',
  TRANSACTION_TYPE_ORDER_SALE: 'Order Sale',

  // Status
  STATUS_COMPLETED: 'Completed',
  STATUS_PENDING: 'Pending',
  STATUS_FAILED: 'Failed',
  STATUS_CANCELLED: 'Cancelled',

  // Currency
  CURRENCY_USD: 'USD',
  CURRENCY_SYMBOL: '$',

  // Time Formats
  DATE_FORMAT: 'MM/DD/YYYY',
  TIME_FORMAT: 'HH:mm:ss',
  DATETIME_FORMAT: 'MM/DD/YYYY HH:mm:ss'
} as const;

// Helper function to format strings with placeholders
export const formatString = (template: string, values: Record<string, string | number>): string => {
  return template.replace(/\{(\w+)\}/g, (match, key) => {
    return values[key]?.toString() || match;
  });
};

// Common UI patterns
export const UI_PATTERNS = {
  // Button classes
  PRIMARY_BUTTON: 'bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors',
  SECONDARY_BUTTON: 'bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors',
  DANGER_BUTTON: 'bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors',
  SUCCESS_BUTTON: 'bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors',

  // Input classes
  INPUT_FIELD: 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
  INPUT_ERROR: 'mt-1 block w-full px-3 py-2 border border-red-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500',

  // Card classes
  CARD: 'bg-white overflow-hidden shadow rounded-lg',
  CARD_HEADER: 'px-4 py-5 sm:px-6',
  CARD_BODY: 'px-4 py-5 sm:p-6',

  // Table classes
  TABLE: 'min-w-full divide-y divide-gray-200',
  TABLE_HEADER: 'bg-gray-50',
  TABLE_HEADER_CELL: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
  TABLE_BODY: 'bg-white divide-y divide-gray-200',
  TABLE_CELL: 'px-6 py-4 whitespace-nowrap text-sm text-gray-900',

  // Status badges
  STATUS_SUCCESS: 'px-2 py-1 text-xs rounded-full bg-green-100 text-green-800',
  STATUS_WARNING: 'px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800',
  STATUS_ERROR: 'px-2 py-1 text-xs rounded-full bg-red-100 text-red-800',
  STATUS_INFO: 'px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800',

  // Loading spinner
  LOADING_SPINNER: 'animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto'
} as const;
