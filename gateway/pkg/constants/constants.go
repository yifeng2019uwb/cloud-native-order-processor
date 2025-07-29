package constants

import "time"

// Service names
const (
	UserService      = "user_service"
	InventoryService = "inventory_service"
	GatewayService   = "gateway"
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
	StatusNoContent           = 204
)

// Gateway configuration
const (
	DefaultPort      = 8080
	DefaultHost      = "0.0.0.0"
	DefaultRedisHost = "localhost"
	DefaultRedisPort = 6379
	DefaultRedisDB   = 0
	DefaultRedisSSL  = false
)

// Environment variable names
const (
	EnvGatewayPort         = "GATEWAY_PORT"
	EnvGatewayHost         = "GATEWAY_HOST"
	EnvRedisHost           = "REDIS_HOST"
	EnvRedisPort           = "REDIS_PORT"
	EnvRedisPassword       = "REDIS_PASSWORD"
	EnvRedisDB             = "REDIS_DB"
	EnvRedisSSL            = "REDIS_SSL"
	EnvUserServiceURL      = "USER_SERVICE_URL"
	EnvInventoryServiceURL = "INVENTORY_SERVICE_URL"
)

// Default service URLs
const (
	DefaultUserServiceURL      = "http://user-service:8000"
	DefaultInventoryServiceURL = "http://inventory-service:8001"
)

// Time constants
const (
	DefaultTimeout = 30 * time.Second
	CacheTTL       = 5 * time.Minute
	SessionTTL     = 24 * time.Hour
	RedisTimeout   = 5 * time.Second
)

// API paths
const (
	HealthPath       = "/health"
	UserAPIPath      = "/api/users"
	InventoryAPIPath = "/api/inventory"
	APIV1Path        = "/api/v1"
)

// API route paths
const (
	AuthLoginPath          = "/auth/login"
	AuthRegisterPath       = "/auth/register"
	AuthProfilePath        = "/auth/profile"
	AuthLogoutPath         = "/auth/logout"
	InventoryAssetsPath    = "/inventory/assets"
	InventoryAssetByIDPath = "/inventory/assets/:id"
)

// Headers
const (
	ContentTypeJSON     = "application/json"
	AuthorizationHeader = "Authorization"
	UserAgentHeader     = "User-Agent"
	XRequestIDHeader    = "X-Request-ID"
	XSessionIDHeader    = "X-Session-ID"
)

// Error codes
const (
	ErrorCodeValidation         = "VALIDATION_ERROR"
	ErrorCodeAuthentication     = "AUTH_ERROR"
	ErrorCodeAuthorization      = "FORBIDDEN"
	ErrorCodeNotFound           = "NOT_FOUND"
	ErrorCodeRateLimit          = "RATE_LIMIT_EXCEEDED"
	ErrorCodeInternal           = "INTERNAL_ERROR"
	ErrorCodeServiceUnavailable = "SERVICE_UNAVAILABLE"
)

// Application constants
const (
	AppName    = "order-processor-gateway"
	AppVersion = "1.0.0"
)

// Log messages
const (
	LogConfigLoadFailed     = "Failed to load configuration"
	LogRedisConnectFailed   = "Failed to connect to Redis"
	LogRedisConnectSuccess  = "Connected to Redis"
	LogRedisContinueWithout = "Continuing without Redis (some features will be disabled)"
	LogProxyInitSuccess     = "Proxy service initialized"
	LogServerStart          = "Starting Gateway server on port"
	LogServerStartFailed    = "Failed to start server"
)

// Service status messages
const (
	StatusHealthy         = "healthy"
	StatusDegradedNoRedis = "degraded (no Redis)"
)

// Service names for responses
const (
	ServiceNameUser      = "user-service"
	ServiceNameInventory = "inventory-service"
)

// Proxy messages
const (
	ProxyUserServiceNotImplemented      = "User service proxy - not implemented yet"
	ProxyInventoryServiceNotImplemented = "Inventory service proxy - not implemented yet"
	ProxyNotImplemented                 = "Proxy not implemented yet"
)

// CORS configuration
const (
	CORSAllowOrigin  = "*"
	CORSAllowMethods = "GET, POST, PUT, DELETE, OPTIONS"
	CORSAllowHeaders = "Origin, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization"
)

// Authentication constants
const (
	AuthSchemeBearer      = "Bearer"
	AuthPlaceholderUserID = "placeholder_user_id"
	AuthDefaultRole       = "user"
)

// Error messages
const (
	ErrorAuthHeaderRequired    = "Authorization header required"
	ErrorAuthHeaderInvalid     = "Invalid authorization header format"
	ErrorRateLimitExceeded     = "Rate limit exceeded"
	ErrorSessionInvalid        = "Invalid or expired session"
	ErrorRedisConnectionFailed = "failed to connect to Redis:"
)

// Redis key prefixes
const (
	RedisKeyPrefixSession   = "session:"
	RedisKeyPrefixRateLimit = "rate_limit:"
)

// Context keys
const (
	ContextKeyUserID   = "user_id"
	ContextKeyUserRole = "user_role"
	ContextKeySession  = "session"
)
