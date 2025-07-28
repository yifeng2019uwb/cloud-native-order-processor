package constants

import "time"

// Service names
const (
	UserService      = "user_service"
	InventoryService = "inventory_service"
)

// Rate limiting constants
const (
	UserServiceRateLimit      = 10  // 10 requests per minute
	InventoryServiceRateLimit = 100 // 100 requests per minute
	DefaultRateLimit          = 50  // 50 requests per minute
	RateLimitWindow           = time.Minute
)

// Security levels
const (
	SecurityLevelPublic        = "public"
	SecurityLevelAuthenticated = "authenticated"
	SecurityLevelAdmin         = "admin"
)

// HTTP status codes
const (
	StatusOK                  = 200
	StatusCreated             = 201
	StatusBadRequest          = 400
	StatusUnauthorized        = 401
	StatusForbidden           = 403
	StatusNotFound            = 404
	StatusTooManyRequests     = 429
	StatusInternalServerError = 500
)

// Gateway configuration
const (
	DefaultPort      = 8080
	DefaultHost      = "0.0.0.0"
	DefaultRedisHost = "localhost"
	DefaultRedisPort = 6379
)

// Time constants
const (
	DefaultTimeout = 30 * time.Second
	CacheTTL       = 5 * time.Minute
	SessionTTL     = 24 * time.Hour
)

// API paths
const (
	HealthPath       = "/health"
	UserAPIPath      = "/api/users"
	InventoryAPIPath = "/api/inventory"
)

// Headers
const (
	ContentTypeJSON     = "application/json"
	AuthorizationHeader = "Authorization"
	UserAgentHeader     = "User-Agent"
	XRequestIDHeader    = "X-Request-ID"
)

// Error codes
const (
	ErrorCodeValidation     = "VALIDATION_ERROR"
	ErrorCodeAuthentication = "AUTH_ERROR"
	ErrorCodeAuthorization  = "FORBIDDEN"
	ErrorCodeNotFound       = "NOT_FOUND"
	ErrorCodeRateLimit      = "RATE_LIMIT_EXCEEDED"
	ErrorCodeInternal       = "INTERNAL_ERROR"
	ErrorCodeServiceUnavailable = "SERVICE_UNAVAILABLE"
)
