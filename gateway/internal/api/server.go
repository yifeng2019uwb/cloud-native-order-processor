package api

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"strings"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/internal/middleware"
	"order-processor-gateway/internal/services"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/logging"
	"order-processor-gateway/pkg/metrics"
	"order-processor-gateway/pkg/models"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// Server represents the API server
type Server struct {
	config       *config.Config
	router       *gin.Engine
	redisService *services.RedisService
	proxyService *services.ProxyService
	logger       *logging.BaseLogger
	metrics      *metrics.GatewayMetrics
}

// NewServer creates a new API server
func NewServer(cfg *config.Config, redisService *services.RedisService, proxyService *services.ProxyService) *Server {
	return NewServerWithRegistry(cfg, redisService, proxyService, nil)
}

// NewServerWithRegistry creates a new API server with a custom metrics registry (for testing)
func NewServerWithRegistry(cfg *config.Config, redisService *services.RedisService, proxyService *services.ProxyService, reg prometheus.Registerer) *Server {
	server := &Server{
		config:       cfg,
		router:       gin.Default(),
		redisService: redisService,
		proxyService: proxyService,
		logger:       logging.NewBaseLogger(logging.GATEWAY),
		metrics:      metrics.NewGatewayMetricsWithRegistry(reg),
	}

	server.setupRoutes()
	return server
}

// setupRoutes configures all routes and middleware
func (s *Server) setupRoutes() {
	// Add basic middleware
	s.router.Use(middleware.CORS())
	s.router.Use(middleware.Logger())
	s.router.Use(middleware.Recovery())

	// Add auth middleware globally to set user roles for all routes (SEC-011: IP block check when Redis available)
	s.router.Use(middleware.AuthMiddleware(s.config, s.redisService))

	// Add Redis-based middleware if Redis is available
	if s.redisService != nil {
		// Add rate limiting middleware with metrics (configurable via GATEWAY_RATE_LIMIT env var)
		s.router.Use(middleware.RateLimitMiddleware(s.redisService, s.config.RateLimit.Limit, s.config.RateLimit.Window, nil))

		// Phase 2: Add session middleware
		// s.router.Use(middleware.SessionMiddleware(s.redisService))
	}

	// Record HTTP request count and duration for every request (gateway_http_*)
	s.router.Use(middleware.MetricsHTTP(s.metrics))

	// Health check endpoint
	s.router.GET(constants.HealthPath, s.healthCheck)

	// Metrics endpoint for Prometheus (excludes *_created to avoid 1.77G timestamp in Grafana)
	s.router.GET(constants.MetricsPath, gin.WrapH(promhttp.HandlerFor(metrics.Handler(), promhttp.HandlerOpts{})))

	// API v1 routes
	api := s.router.Group(constants.APIV1Path)
	{
		// Auth service routes
		auth := api.Group("/auth")
		{
			// Public auth routes (no auth required)
			auth.POST("/login", s.handleProxyRequest)
			auth.POST("/register", s.handleProxyRequest)

			// Protected auth routes (auth required)
			protectedAuth := auth.Group("")
			{
				protectedAuth.GET("/profile", s.handleProxyRequest)
				protectedAuth.PUT("/profile", s.handleProxyRequest)
				protectedAuth.POST("/logout", s.handleProxyRequest)
			}
		}

		// Inventory service routes
		inventory := api.Group("/inventory")
		{
			// Public inventory routes (no auth required)
			inventory.GET("/assets", s.handleProxyRequest)
			inventory.GET("/assets/:id", s.handleProxyRequest)
		}

		// Order service routes (all require auth)
		orders := api.Group("/orders")
		{
			orders.POST("", s.handleProxyRequest)    // Create order
			orders.GET("/:id", s.handleProxyRequest) // Get order details
			orders.GET("", s.handleProxyRequest)     // List user orders
		}

		// Portfolio service routes (require auth)
		portfolio := api.Group("/portfolio")
		{
			portfolio.GET("", s.handleProxyRequest) // Get user portfolio
		}

		// Balance service routes (all require auth)
		balance := api.Group("/balance")
		{
			balance.GET("", s.handleProxyRequest)                 // Get balance
			balance.POST("/deposit", s.handleProxyRequest)        // Deposit funds
			balance.POST("/withdraw", s.handleProxyRequest)       // Withdraw funds
			balance.GET("/transactions", s.handleProxyRequest)    // Transaction history
			balance.GET("/asset/:asset_id", s.handleProxyRequest) // Get specific asset balance
		}

		// Asset service routes (all require auth)
		assets := api.Group("/assets")
		{
			assets.GET("/balances", s.handleProxyRequest)               // Get all asset balances
			assets.GET("/:asset_id/transactions", s.handleProxyRequest) // Get asset transactions
		}

		// Insights service routes (all require auth)
		insights := api.Group("/insights")
		{
			insights.GET("/portfolio", s.handleProxyRequest) // Get portfolio insights
		}

		// CNY service routes (require auth)
		cny := api.Group("/cny")
		{
			cny.POST("/claim", s.handleProxyRequest) // Claim CNY red pocket
		}
	}
}

// healthCheck handles health check requests
func (s *Server) healthCheck(c *gin.Context) {
	status := constants.StatusHealthy
	if s.redisService == nil {
		status = constants.StatusDegradedNoRedis
	}

	c.JSON(http.StatusOK, gin.H{
		constants.JSONFieldStatus:  status,
		constants.JSONFieldService: constants.GatewayService,
		constants.JSONFieldRedis:   s.redisService != nil,
	})
}

// handleProxyRequest handles all proxy requests with routing and error handling
// Phase 1: Basic proxy logic with simple error handling
func (s *Server) handleProxyRequest(c *gin.Context) {
	// Get route configuration
	path := c.Request.URL.Path
	routeConfig, exists := s.proxyService.GetRouteConfig(path)

	if !exists {
		// Handle dynamic routes (like /assets/:id)
		basePath := s.getBasePath(path)
		routeConfig, exists = s.proxyService.GetRouteConfig(basePath)
		if !exists {
			s.handleError(c, http.StatusNotFound, models.ErrSvcUnavailable, constants.ErrorRouteNotFound)
			return
		}
	}

	// Check if routeConfig is nil before accessing its properties
	if routeConfig == nil {
		s.logger.Error(logging.AUTH_FAILURE, "Route config is nil", "", map[string]interface{}{
			constants.JSONFieldPath: path,
		})
		s.handleError(c, http.StatusNotFound, models.ErrSvcUnavailable, constants.ErrorRouteConfigNil)
		return
	}

	// Check authentication requirements
	if routeConfig.RequiresAuth {
		userRole := c.GetString(constants.ContextKeyUserRole)
		if userRole == "" {
			s.logger.Error(logging.AUTH_FAILURE, "Authentication required but no user role", "", map[string]interface{}{
				constants.JSONFieldPath: path,
			})
			s.handleError(c, http.StatusUnauthorized, models.ErrAuthInvalidToken, constants.ErrorAuthRequired)
			return
		}
	}

	// Check role permissions
	if len(routeConfig.AllowedRoles) > 0 {
		userRole := c.GetString(constants.ContextKeyUserRole)
		hasPermission := false
		for _, role := range routeConfig.AllowedRoles {
			if role == userRole {
				hasPermission = true
				break
			}
		}
		if !hasPermission {
			s.logger.Error(logging.AUTH_FAILURE, "Permission denied", "", map[string]interface{}{
				constants.JSONFieldPath:         path,
				constants.JSONFieldUserRole:     userRole,
				constants.JSONFieldAllowedRoles: routeConfig.AllowedRoles,
			})
			s.handleError(c, http.StatusForbidden, models.ErrPermInsufficient, constants.ErrorInsufficientPerms)
			return
		}
	}
	// If AllowedRoles is empty, allow access (any role including public)

	// Determine target service
	targetService := s.proxyService.GetTargetService(path)
	if targetService == "" {
		s.handleError(c, http.StatusNotFound, models.ErrSvcUnavailable, constants.ErrorServiceNotFound)
		return
	}

	// Prepare request body
	var body interface{}
	if c.Request.Body != nil {
		bodyBytes, err := io.ReadAll(c.Request.Body)
		if err != nil {
			s.handleError(c, http.StatusBadRequest, models.ErrSvcUnavailable, constants.ErrorReadRequestBody)
			return
		}
		if len(bodyBytes) > 0 {
			// Parse JSON body to preserve structure
			if err := json.Unmarshal(bodyBytes, &body); err != nil {
				s.handleError(c, http.StatusBadRequest, models.ErrSvcUnavailable, constants.ErrorInvalidJSONBody)
				return
			}
		}
	}

	// Prepare headers
	headers := make(map[string]string)
	for key, values := range c.Request.Header {
		headers[key] = values[0] // Take first value
	}

	// Prepare query parameters
	queryParams := make(map[string]string)
	for key, values := range c.Request.URL.Query() {
		if len(values) > 0 {
			queryParams[key] = values[0] // Take first value
		}
	}

	// Create proxy request
	proxyReq := &models.ProxyRequest{
		Method:        c.Request.Method,
		Path:          path,
		Headers:       headers,
		Body:          body,
		QueryParams:   queryParams,
		TargetService: targetService,
		TargetPath:    s.stripAPIPrefix(path),
		Context: &models.RequestContext{
			RequestID:   generateRequestID(),
			Timestamp:   time.Now(),
			ServiceName: targetService,
			User:        s.getUserContext(c),
		},
	}

	// Forward request to backend service
	resp, err := s.proxyService.ProxyRequest(c.Request.Context(), proxyReq)
	if err != nil {
		s.metrics.RecordProxyError(targetService, "request_failed")
		s.logger.Error(logging.PROXY_FAILURE, "Proxy request failed", "", map[string]interface{}{
			"target_service": targetService,
			"path":           path,
			"error":          err.Error(),
		})
		s.handleError(c, http.StatusServiceUnavailable, models.ErrSvcUnavailable, fmt.Sprintf(constants.ErrorBackendService, err))
		return
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 500 {
		s.metrics.RecordProxyError(targetService, strconv.Itoa(resp.StatusCode))
		s.logger.Error(logging.BACKEND_5XX, "Backend returned 5xx", "", map[string]interface{}{
			"target_service": targetService,
			"path":           path,
			"status_code":    resp.StatusCode,
		})
	}

	// Save rate limit headers before copying backend headers (they may be overwritten)
	rateLimitLimit := c.Writer.Header().Get(constants.RateLimitHeaderLimit)
	rateLimitRemaining := c.Writer.Header().Get(constants.RateLimitHeaderRemaining)
	rateLimitReset := c.Writer.Header().Get(constants.RateLimitHeaderReset)

	// Copy response headers from backend
	for key, values := range resp.Header {
		for _, value := range values {
			c.Header(key, value)
		}
	}

	// Restore rate limit headers (they take precedence over backend headers)
	if rateLimitLimit != "" {
		c.Header(constants.RateLimitHeaderLimit, rateLimitLimit)
	}
	if rateLimitRemaining != "" {
		c.Header(constants.RateLimitHeaderRemaining, rateLimitRemaining)
	}
	if rateLimitReset != "" {
		c.Header(constants.RateLimitHeaderReset, rateLimitReset)
	}

	// Copy response body
	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		s.handleError(c, http.StatusInternalServerError, models.ErrSvcUnavailable, constants.ErrorReadResponseBody)
		return
	}

	// SEC-011: record failed login for IP block. On 5th 401 from login, set ip_block:<ip> so next request gets 403.
	if s.redisService != nil && path == constants.APIV1AuthLogin && c.Request.Method == http.MethodPost && resp.StatusCode == http.StatusUnauthorized {
		if err := s.redisService.RecordFailedLogin(c.Request.Context(), c.ClientIP()); err != nil {
			s.logger.Info(logging.REQUEST_END, "RecordFailedLogin failed (non-fatal)", "", map[string]interface{}{
				"client_ip": c.ClientIP(),
				"error":     err.Error(),
			})
		}
	}

	// Return response
	c.Data(resp.StatusCode, resp.Header.Get("Content-Type"), bodyBytes)
}

// handleError handles errors with standardized error responses
func (s *Server) handleError(c *gin.Context, statusCode int, errorCode models.ErrorCode, message string) {
	errorResponse := models.ErrorResponse{
		Error:     string(errorCode),
		Message:   message,
		Code:      string(errorCode),
		Timestamp: time.Now(),
	}

	c.JSON(statusCode, errorResponse)
}

// getUserContext extracts user context from gin context
func (s *Server) getUserContext(c *gin.Context) *models.UserContext {
	userContext, exists := c.Get(constants.ContextKeyUserContext)
	if !exists {
		return &models.UserContext{
			Username:        "",
			Role:            "", // No role for unauthenticated users
			IsAuthenticated: false,
		}
	}
	return userContext.(*models.UserContext)
}

// getBasePath extracts the base path for dynamic routes
func (s *Server) getBasePath(path string) string {
	// Check for known dynamic route patterns
	switch {
	case strings.HasPrefix(path, constants.AssetBalancesPattern):
		// /api/v1/assets/balances -> /api/v1/assets/balances (exact match)
		return constants.AssetBalancesPattern

	case strings.HasPrefix(path, constants.APIV1AssetsPrefix) && strings.HasSuffix(path, constants.TransactionsSuffix):
		// /api/v1/assets/AAVE/transactions -> /api/v1/assets/:asset_id/transactions
		return constants.AssetTransactionsPattern

	case strings.HasPrefix(path, constants.APIV1AssetsPrefix) && strings.HasSuffix(path, constants.BalanceSuffix):
		// /api/v1/assets/AAVE/balance -> /api/v1/assets/:asset_id/balance
		return constants.AssetBalancePattern

	case strings.HasPrefix(path, constants.APIV1OrdersPrefix):
		// /api/v1/orders/123 -> /api/v1/orders/:id
		parts := strings.Split(path, constants.PathSeparator)
		if len(parts) == 5 { // /api/v1/orders/{id}
			return constants.OrderByIDPattern
		}

	case strings.HasPrefix(path, constants.APIV1PortfolioPrefix):
		// /api/v1/portfolio/username -> /api/v1/portfolio/:username
		parts := strings.Split(path, constants.PathSeparator)
		if len(parts) == 5 { // /api/v1/portfolio/{username}
			return constants.PortfolioByUserPattern
		}

	case strings.HasPrefix(path, constants.APIV1InventoryPrefix):
		// /api/v1/inventory/assets/123 -> /api/v1/inventory/assets/:id
		parts := strings.Split(path, constants.PathSeparator)
		if len(parts) == 6 { // /api/v1/inventory/assets/{id}
			return constants.InventoryAssetByIDPattern
		}

	case strings.HasPrefix(path, constants.APIV1BalancePrefix):
		// /api/v1/balance/asset/BTC -> /api/v1/balance/asset/:asset_id
		parts := strings.Split(path, constants.PathSeparator)
		if len(parts) == 6 { // /api/v1/balance/asset/{asset_id}
			return constants.BalanceAssetByIDPattern
		}
	}

	return path
}

// stripAPIPrefix removes the API prefix from the path
func (s *Server) stripAPIPrefix(path string) string {
	if strings.HasPrefix(path, constants.APIV1Path) {
		return strings.TrimPrefix(path, constants.APIV1Path)
	}
	return path
}

// generateRequestID generates a simple request ID
// Phase 2: Use UUID v4 for better uniqueness
func generateRequestID() string {
	return fmt.Sprintf("req-%d", time.Now().UnixNano())
}

// Start starts the HTTP server
func (s *Server) Start() error {
	addr := fmt.Sprintf("%s:%s", s.config.Server.Host, s.config.Server.Port)
	return s.router.Run(addr)
}
