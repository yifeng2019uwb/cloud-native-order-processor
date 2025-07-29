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
	EnvJWTSecretKey        = "JWT_SECRET_KEY"
	EnvJWTAlgorithm        = "JWT_ALGORITHM"
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

// Phase 1: API routing paths
const (
	// API v1 base path
	APIV1BasePath = "/api/v1"

	// Auth service paths
	APIV1AuthPath     = "/api/v1/auth"
	APIV1AuthLogin    = "/api/v1/auth/login"
	APIV1AuthRegister = "/api/v1/auth/register"
	APIV1AuthProfile  = "/api/v1/auth/me"
	APIV1AuthLogout   = "/api/v1/auth/logout"

	// Inventory service paths
	APIV1InventoryPath    = "/api/v1/inventory"
	APIV1InventoryAssets  = "/api/v1/inventory/assets"
	APIV1InventoryAssetID = "/api/v1/inventory/assets/:id"
)

// Phase 1: User roles and permissions
const (
	// User roles
	RolePublic   = "public"   // Unauthenticated user
	RoleCustomer = "customer" // Basic authenticated user
	RoleVIP      = "vip"      // Premium user (future)
	RoleAdmin    = "admin"    // System administrator

	// Default role for new users
	DefaultUserRole = RoleCustomer
)

// Headers
const (
	ContentTypeJSON     = "application/json"
	AuthorizationHeader = "Authorization"
	UserAgentHeader     = "User-Agent"
	XRequestIDHeader    = "X-Request-ID"
	XSessionIDHeader    = "X-Session-ID"

	// Phase 1: User context headers (added to backend requests)
	XUserIDHeader        = "X-User-ID"
	XUserRoleHeader      = "X-User-Role"
	XAuthenticatedHeader = "X-Authenticated"
	XSourceHeader        = "X-Source"
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

// Phase 1: JWT configuration
const (
	DefaultJWTSecretKey = "dev-secret-key-change-in-production" // TODO: Use environment variable
	DefaultJWTAlgorithm = "HS256"
)

// Phase 1: Circuit breaker configuration (TODO - Phase 2)
const (
// CircuitBreakerFailureThreshold = 5  // Number of failures before opening circuit
// CircuitBreakerTimeout          = 60 * time.Second // Time to wait before trying again
)

// Phase 1: Route configuration
var (
	// RouteConfigs defines the routing configuration for API endpoints
	RouteConfigs = map[string]RouteConfig{
		// Auth service routes
		APIV1AuthLogin: {
			Path:         APIV1AuthLogin,
			RequiresAuth: false,                // Login doesn't require authentication
			AllowedRoles: []string{RolePublic}, // Only public (unauthenticated) users can access
		},
		APIV1AuthRegister: {
			Path:         APIV1AuthRegister,
			RequiresAuth: false,                // Registration doesn't require authentication
			AllowedRoles: []string{RolePublic}, // Only public (unauthenticated) users can access
		},
		APIV1AuthProfile: {
			Path:         APIV1AuthProfile,
			RequiresAuth: true, // Profile requires authentication
			AllowedRoles: []string{RoleCustomer, RoleVIP, RoleAdmin},
		},
		APIV1AuthLogout: {
			Path:         APIV1AuthLogout,
			RequiresAuth: true, // Logout requires authentication
			AllowedRoles: []string{RoleCustomer, RoleVIP, RoleAdmin},
		},

		// Inventory service routes
		APIV1InventoryAssets: {
			Path:         APIV1InventoryAssets,
			RequiresAuth: false,      // Public inventory browsing
			AllowedRoles: []string{}, // Empty means public access (no role required)
		},
		APIV1InventoryAssetID: {
			Path:         APIV1InventoryAssetID,
			RequiresAuth: false,      // Public asset details
			AllowedRoles: []string{}, // Empty means public access (no role required)
		},
	}
)

// RouteConfig defines routing configuration for API endpoints
type RouteConfig struct {
	Path         string   `json:"path"`
	RequiresAuth bool     `json:"requires_auth"`
	AllowedRoles []string `json:"allowed_roles"`
}
