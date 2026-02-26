package constants

import "time"

// Service names
const (
	UserService      = "user_service"
	InventoryService = "inventory_service"
	OrderService     = "order_service"
	AuthService      = "auth_service"
	InsightsService  = "insights_service"
	GatewayService   = "gateway"
)

// Rate limiting constants
const (
	UserServiceRateLimit      = 5000  // 5000 requests per minute
	InventoryServiceRateLimit = 7500  // 7500 requests per minute
	OrderServiceRateLimit     = 3000  // 3000 requests per minute
	DefaultRateLimit          = 3000  // 3000 requests per minute (default for services without specific limits)
	GatewayRateLimit          = 10000 // 10000 requests per minute (default for gateway, configurable)
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
	StatusNoContent           = 204
	StatusBadRequest          = 400
	StatusUnauthorized        = 401
	StatusForbidden           = 403
	StatusNotFound            = 404
	StatusConflict            = 409
	StatusUnprocessableEntity = 422
	StatusTooManyRequests     = 429
	StatusInternalServerError = 500
	StatusServiceUnavailable  = 503
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
	EnvGatewayRateLimit    = "GATEWAY_RATE_LIMIT" // Requests per minute
	EnvUserServiceURL      = "USER_SERVICE_URL"
	EnvInventoryServiceURL = "INVENTORY_SERVICE_URL"
	EnvOrderServiceURL     = "ORDER_SERVICE_URL"
	EnvAuthServiceURL      = "AUTH_SERVICE_URL"
	EnvInsightsServiceURL  = "INSIGHTS_SERVICE_URL"
	EnvBlockDurationSeconds     = "GATEWAY_BLOCK_DURATION_SECONDS"     // IP block TTL; default 300. Set 86400 in production.
	EnvFailedLoginWindowSeconds = "GATEWAY_FAILED_LOGIN_WINDOW_SECONDS" // Failure count window; default 300. Set 86400 in production.
)

// Default service URLs
const (
	DefaultUserServiceURL      = "http://user_service:8000"
	DefaultInventoryServiceURL = "http://inventory_service:8001"
	DefaultOrderServiceURL     = "http://order_service:8002"
	DefaultAuthServiceURL      = "http://auth_service:8003"
	DefaultInsightsServiceURL  = "http://insights_service:8004"
)

// Time constants
const (
	DefaultTimeout = 30 * time.Second
	CacheTTL       = 5 * time.Minute
	SessionTTL     = 24 * time.Hour
	RedisTimeout   = 5 * time.Second
)

// Service label values for gateway HTTP metrics (grouping requests by path type)
const (
	ServiceLabelHealth  = "health"
	ServiceLabelMetrics = "metrics"
)

// API paths
const (
	HealthPath       = "/health"
	MetricsPath      = "/metrics"
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
	APIV1AuthProfile  = "/api/v1/auth/profile"
	APIV1AuthLogout   = "/api/v1/auth/logout"

	// Inventory service paths
	APIV1InventoryPath    = "/api/v1/inventory"
	APIV1InventoryAssets  = "/api/v1/inventory/assets"
	APIV1InventoryAssetID = "/api/v1/inventory/assets/:id"

	// Order service paths
	APIV1OrderPath = "/api/v1/orders"
	APIV1Orders    = "/api/v1/orders" // Handles both POST (create) and GET (list)
	APIV1OrderByID = "/api/v1/orders/:id"

	// Portfolio service paths
	APIV1PortfolioPath = "/api/v1/portfolio"

	// Balance service paths
	APIV1BalancePath         = "/api/v1/balance"
	APIV1BalanceGet          = "/api/v1/balance"
	APIV1BalanceDeposit      = "/api/v1/balance/deposit"
	APIV1BalanceWithdraw     = "/api/v1/balance/withdraw"
	APIV1BalanceTransactions = "/api/v1/balance/transactions"
	APIV1AssetBalanceByID    = "/api/v1/balance/asset/:asset_id"

	// Asset service paths
	APIV1AssetPath             = "/api/v1/assets"
	APIV1AssetTransactionsByID = "/api/v1/assets/:asset_id/transactions"

	// Insights service paths
	APIV1InsightsPath      = "/api/v1/insights"
	APIV1InsightsPortfolio = "/api/v1/insights/portfolio"

	// CNY service paths (user service)
	APIV1CNYPath  = "/api/v1/cny"
	APIV1CNYClaim = "/api/v1/cny/claim"
)

// Path patterns for dynamic route matching
const (
	// Asset patterns
	AssetBalancesPattern     = "/api/v1/assets/balances"
	AssetTransactionsPattern = "/api/v1/assets/:asset_id/transactions"
	AssetBalancePattern      = "/api/v1/assets/:asset_id/balance"

	// Order patterns
	OrderByIDPattern = "/api/v1/orders/:id"

	// Portfolio patterns
	PortfolioByUserPattern = "/api/v1/portfolio/:username"

	// Inventory patterns
	InventoryAssetByIDPattern = "/api/v1/inventory/assets/:id"

	// Balance patterns
	BalanceAssetByIDPattern = "/api/v1/balance/asset/:asset_id"
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
	XAuthServiceHeader   = "X-Auth-Service"
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
	LogConfigLoadFailed            = "Failed to load configuration"
	LogRedisConnectFailed          = "Failed to connect to Redis"
	LogRedisConnectSuccess         = "Connected to Redis"
	LogRedisContinueWithout        = "Continuing without Redis (some features will be disabled)"
	LogProxyInitSuccess            = "Proxy service initialized"
	LogServerStart                 = "Starting Gateway server on port"
	LogServerStartFailed           = "Failed to start server"
	LogLookingUpRouteConfig        = "Looking up route config"
	LogRouteNotFoundTryingBasePath = "Route not found, trying basePath"
	LogRouteNotFoundReturning404   = "Route not found, returning 404"
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

// JSON field names
const (
	JSONFieldPath          = "path"
	JSONFieldMethod        = "method"
	JSONFieldStatus        = "status"
	JSONFieldService       = "service"
	JSONFieldRedis         = "redis"
	JSONFieldMessage       = "message"
	JSONFieldError         = "error"
	JSONFieldSuccess       = "success"
	JSONFieldUserRole      = "user_role"
	JSONFieldAuthHeader    = "auth_header"
	JSONFieldUsername      = "username"
	JSONFieldRole          = "role"
	JSONFieldRequiredRoles = "required_roles"
	JSONFieldAllowedRoles  = "allowed_roles"
	JSONFieldRequiresAuth  = "requires_auth"
	JSONFieldInputPath     = "input_path"
	JSONFieldResult        = "result"
	JSONFieldRetryAfter    = "retry_after"
	JSONFieldLimit         = "limit"
	JSONFieldRemaining     = "remaining"
	JSONFieldResetTime     = "reset_time"
)

// Context keys
const (
	ContextKeyUserContext      = "user_context"
	ContextKeyProxyErrorTarget = "proxy_error_target" // set by handler; middleware records gateway_proxy_errors_total
	ContextKeyProxyErrorType   = "proxy_error_type"   // request_failed | 500 | 502 | 503
)

// Header values
const (
	HeaderValueTrue    = "true"
	HeaderValueGateway = "gateway"
)

// Rate limit header names
const (
	RateLimitHeaderLimit     = "X-RateLimit-Limit"
	RateLimitHeaderRemaining = "X-RateLimit-Remaining"
	RateLimitHeaderReset     = "X-RateLimit-Reset"
)

// Circuit breaker field names
const (
	CircuitBreakerFieldState        = "state"
	CircuitBreakerFieldFailureCount = "failure_count"
	CircuitBreakerFieldServiceName  = "service_name"
)

// Prometheus metric names (3-metric plan: requests, errors, latency)
const (
	MetricGatewayRequestsTotal  = "gateway_requests_total"
	MetricGatewayErrorsTotal    = "gateway_errors_total"
	MetricGatewayRequestLatency = "gateway_request_latency_seconds"
	// Legacy / rate-limit (rate_limit_metrics.go still references these)
	MetricRequestsTotal            = "gateway_requests_total" // rate-limit package
	MetricHTTPRequestsTotal        = "gateway_http_requests_total"
	MetricHTTPRequestLatency       = "gateway_http_request_latency_seconds"
	MetricHTTPErrorsTotal          = "gateway_http_errors_total"
	MetricProxyErrorsTotal         = "gateway_proxy_errors_total"
	MetricRateLimitViolationsTotal = "gateway_rate_limit_violations_total"
	MetricRateLimitRemaining       = "gateway_rate_limit_remaining"
)

// Prometheus label names
const (
	LabelMethod        = "method"
	LabelPath          = "path"
	LabelStatusCode    = "status_code"
	LabelService       = "service"
	LabelTargetService = "target_service"
	LabelErrorType     = "error_type"
	LabelEndpoint      = "endpoint"
	LabelStatus        = "status"
	LabelClientIP      = "client_ip"
)

// Auth service constants
const (
	AuthValidatePath  = "/internal/auth/validate"
	AuthTokenField    = "token"
	AuthValidField    = "valid"
	AuthMessageField  = "message"
	AuthUserField     = "user"
	AuthMetadataField = "metadata"
	AuthRoleField     = "role"
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

	// Server error messages
	ErrorRouteNotFound   = "Route not found"
	ErrorAuthRequired    = "Authentication required"
	ErrorInsufficientPerms = "Insufficient permissions"
	ErrorServiceNotFound   = "Service not found"
	ErrorReadRequestBody   = "Failed to read request body"
	ErrorInvalidJSONBody   = "Invalid JSON body"
	ErrorReadResponseBody  = "Failed to read response body"
	ErrorBackendService    = "Backend service error: %v"
	ErrorIPBlocked         = "Access denied: IP blocked"
)

// Redis key prefixes and keys
const (
	RedisKeyPrefixSession   = "session:"
	RedisKeyPrefixRateLimit = "rate_limit:"
	// RedisKeyPrefixIPBlock is the Redis key prefix for per-IP block with TTL. Key: ip_block:<ip>. Ops: SET ip_block:<ip> 1 EX <seconds> to block (e.g. EX 300 for 5 min, EX 86400 for 24hr).
	RedisKeyPrefixIPBlock   = "ip_block:"
	RedisKeyPrefixLoginFail = "login_fail:" // per-IP failed login count; triggers IP block after threshold
)

// Failed login tracking (SEC-011). Block IP after FailedLoginBlockThreshold failed logins in a sliding window; when block is set, login_fail TTL is set to BlockDurationSeconds so the count is removed when the block expires.
const (
	// FailedLoginBlockThreshold: block IP after 5 failed logins
	FailedLoginBlockThreshold = 5
	// BlockDurationSeconds: default 300s (5 min) for dev/test. Set GATEWAY_BLOCK_DURATION_SECONDS=86400 in production for 24hr block.
	BlockDurationSeconds = 300
	// FailedLoginWindowSeconds: sliding window for counting failed logins. Set GATEWAY_FAILED_LOGIN_WINDOW_SECONDS=86400 in production.
	FailedLoginWindowSeconds = 300
)

// Context keys
const (
	ContextKeyUserID   = "user_id"
	ContextKeyUserRole = "user_role"
	ContextKeySession  = "session"
)

// Circuit breaker configuration
const (
	// Circuit breaker states
	CircuitBreakerStateClosed   = "closed"
	CircuitBreakerStateOpen     = "open"
	CircuitBreakerStateHalfOpen = "half-open"

	// Circuit breaker thresholds
	CircuitBreakerFailureThreshold = 5                // Number of failures before opening circuit
	CircuitBreakerTimeout          = 60 * time.Second // Time to wait before trying again
	CircuitBreakerSuccessThreshold = 3                // Number of successes to close circuit from half-open
)

// Phase 1: Route configuration
var (
	// RouteConfigs defines the routing configuration for API endpoints
	RouteConfigs = map[string]RouteConfig{
		// Auth service routes
		APIV1AuthLogin: {
			Path:         APIV1AuthLogin,
			RequiresAuth: false,      // Login doesn't require authentication
			AllowedRoles: []string{}, // Public access - no role needed
		},
		APIV1AuthRegister: {
			Path:         APIV1AuthRegister,
			RequiresAuth: false,      // Registration doesn't require authentication
			AllowedRoles: []string{}, // Public access - no role needed
		},
		APIV1AuthProfile: {
			Path:         APIV1AuthProfile,
			RequiresAuth: true,       // Profile requires authentication
			AllowedRoles: []string{}, // No role restrictions - just need to be authenticated
		},
		APIV1AuthLogout: {
			Path:         APIV1AuthLogout,
			RequiresAuth: true,       // Logout requires authentication
			AllowedRoles: []string{}, // No role restrictions - just need to be authenticated
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

		// Order service routes (all require auth)
		APIV1Orders: {
			Path:         APIV1Orders,
			RequiresAuth: true,
			AllowedRoles: []string{}, // No role restrictions - just need to be authenticated
		},
		APIV1OrderByID: {
			Path:         APIV1OrderByID,
			RequiresAuth: true,
			AllowedRoles: []string{}, // No role restrictions - just need to be authenticated
		},

		// Portfolio service routes (all require auth)
		APIV1PortfolioPath: {
			Path:         APIV1PortfolioPath,
			RequiresAuth: true,
			AllowedRoles: []string{}, // No role restrictions - just need to be authenticated
		},

		// Balance service routes (all require auth)
		APIV1BalanceGet: {
			Path:         APIV1BalanceGet,
			RequiresAuth: true,
			AllowedRoles: []string{}, // No role restrictions - just need to be authenticated
		},
		APIV1BalanceDeposit: {
			Path:         APIV1BalanceDeposit,
			RequiresAuth: true,
			AllowedRoles: []string{}, // No role restrictions - just need to be authenticated
		},
		APIV1BalanceWithdraw: {
			Path:         APIV1BalanceWithdraw,
			RequiresAuth: true,
			AllowedRoles: []string{}, // No role restrictions - just need to be authenticated
		},
		APIV1BalanceTransactions: {
			Path:         APIV1BalanceTransactions,
			RequiresAuth: true,
			AllowedRoles: []string{}, // No role restrictions - just need to be authenticated
		},

		// Asset balance service routes (all require auth)
		APIV1AssetBalanceByID: {
			Path:         APIV1AssetBalanceByID,
			RequiresAuth: true,
			AllowedRoles: []string{}, // No role restrictions - just need to be authenticated
		},
		APIV1AssetTransactionsByID: {
			Path:         APIV1AssetTransactionsByID,
			RequiresAuth: true,
			AllowedRoles: []string{}, // No role restrictions - just need to be authenticated
		},

		// Insights service routes (all require auth)
		APIV1InsightsPortfolio: {
			Path:         APIV1InsightsPortfolio,
			RequiresAuth: true,
			AllowedRoles: []string{}, // No role restrictions - just need to be authenticated
		},

		// CNY service routes (require auth)
		APIV1CNYClaim: {
			Path:         APIV1CNYClaim,
			RequiresAuth: true,
			AllowedRoles: []string{},
		},
	}
)

// RouteConfig defines routing configuration for API endpoints
type RouteConfig struct {
	Path         string   `json:"path"`
	RequiresAuth bool     `json:"requires_auth"`
	AllowedRoles []string `json:"allowed_roles"`
}
