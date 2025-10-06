package constants

// API Path Constants
// Centralized API path definitions for the gateway service

// Base API paths
const (
	APIV1Base = "/api/v1"
)

// Service-specific API paths
const (
	// Assets API paths
	APIV1AssetsPrefix    = "/api/v1/assets/"
	APIV1InventoryPrefix = "/api/v1/inventory/assets/"

	// Orders API paths
	APIV1OrdersPrefix = "/api/v1/orders/"

	// Portfolio API paths
	APIV1PortfolioPrefix = "/api/v1/portfolio/"

	// Balance API paths
	APIV1BalancePrefix = "/api/v1/balance/asset/"
)

// API path suffixes
const (
	TransactionsSuffix = "/transactions"
	BalanceSuffix      = "/balance"
)

// Health and monitoring paths
const (
	StatusPath = "/status"
)

// API version constants
const (
	APIVersion1 = "v1"
)

// HTTP methods
const (
	HTTPMethodOptions = "OPTIONS"
)

// Path separators
const (
	PathSeparator = "/"
)
