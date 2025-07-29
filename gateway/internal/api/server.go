package api

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/internal/middleware"
	"order-processor-gateway/internal/services"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/models"

	"github.com/gin-gonic/gin"
)

// Server represents the API server
type Server struct {
	config       *config.Config
	router       *gin.Engine
	redisService *services.RedisService
	proxyService *services.ProxyService
}

// NewServer creates a new API server
func NewServer(cfg *config.Config, redisService *services.RedisService, proxyService *services.ProxyService) *Server {
	server := &Server{
		config:       cfg,
		router:       gin.Default(),
		redisService: redisService,
		proxyService: proxyService,
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

	// Add auth middleware globally to set user roles for all routes
	s.router.Use(middleware.AuthMiddleware(s.config))

	// Add Redis-based middleware if Redis is available
	if s.redisService != nil {
		// Phase 2: Add rate limiting middleware
		// s.router.Use(middleware.RateLimitMiddleware(s.redisService, 100, time.Minute))

		// Phase 2: Add session middleware
		// s.router.Use(middleware.SessionMiddleware(s.redisService))
	}

	// Health check endpoint
	s.router.GET(constants.HealthPath, s.healthCheck)

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
				protectedAuth.GET("/me", s.handleProxyRequest)
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
	}
}

// healthCheck handles health check requests
func (s *Server) healthCheck(c *gin.Context) {
	status := constants.StatusHealthy
	if s.redisService == nil {
		status = constants.StatusDegradedNoRedis
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  status,
		"service": constants.GatewayService,
		"redis":   s.redisService != nil,
	})
}

// handleProxyRequest handles all proxy requests with routing and error handling
// Phase 1: Basic proxy logic with simple error handling
func (s *Server) handleProxyRequest(c *gin.Context) {
	fmt.Printf("🔍 STEP 2: handleProxyRequest START - Path: %s, Method: %s\n", c.Request.URL.Path, c.Request.Method)

	// Get route configuration
	path := c.Request.URL.Path
	fmt.Printf("🔍 STEP 2.1: handleProxyRequest - Looking up route config for path: %s\n", path)
	routeConfig, exists := s.proxyService.GetRouteConfig(path)

		if !exists {
		// Handle dynamic routes (like /assets/:id)
		fmt.Printf("🔍 STEP 2.2: handleProxyRequest - Route not found, trying basePath\n")
		basePath := s.getBasePath(path)
		routeConfig, exists = s.proxyService.GetRouteConfig(basePath)
		if !exists {
			fmt.Printf("🔍 STEP 2.3: handleProxyRequest - Route not found, returning 404\n")
			s.handleError(c, http.StatusNotFound, models.ErrSvcUnavailable, "Route not found")
			return
		}
	}

	fmt.Printf("🔍 STEP 2.4: handleProxyRequest - Route config found: Path=%s, RequiresAuth=%t, AllowedRoles=%v\n",
		routeConfig.Path, routeConfig.RequiresAuth, routeConfig.AllowedRoles)

	// Check if routeConfig is nil
	if routeConfig == nil {
		fmt.Printf("🔍 STEP 2.5: handleProxyRequest - routeConfig is nil!\n")
		s.handleError(c, http.StatusNotFound, models.ErrSvcUnavailable, "Route config is nil")
		return
	}

		fmt.Printf("🔍 STEP 2.6: handleProxyRequest - About to check authentication requirements. RequiresAuth=%t\n", routeConfig.RequiresAuth)

	// Check authentication requirements
	if routeConfig.RequiresAuth {
		userRole := c.GetString(constants.ContextKeyUserRole)
		fmt.Printf("🔍 STEP 2.7: handleProxyRequest - Authentication required, userRole='%s'\n", userRole)
		if userRole == "" {
			fmt.Printf("🔍 STEP 2.8: handleProxyRequest - No userRole, returning 401\n")
			s.handleError(c, http.StatusUnauthorized, models.ErrAuthInvalidToken, "Authentication required")
			return
		}
	} else {
		fmt.Printf("🔍 STEP 2.9: handleProxyRequest - No authentication required\n")
	}

	fmt.Printf("🔍 STEP 2.10: handleProxyRequest - About to check role permissions. AllowedRoles=%v\n", routeConfig.AllowedRoles)

	// Check role permissions
	if len(routeConfig.AllowedRoles) > 0 {
		userRole := c.GetString(constants.ContextKeyUserRole)
		fmt.Printf("🔍 STEP 2.11: handleProxyRequest - userRole='%s', allowedRoles=%v\n", userRole, routeConfig.AllowedRoles)
		hasPermission := false
		for _, role := range routeConfig.AllowedRoles {
			if role == userRole {
				hasPermission = true
				break
			}
		}
		if !hasPermission {
			fmt.Printf("🔍 STEP 2.12: handleProxyRequest - Permission denied - userRole '%s' not in allowedRoles %v\n", userRole, routeConfig.AllowedRoles)
			s.handleError(c, http.StatusForbidden, models.ErrPermInsufficient, "Insufficient permissions")
			return
		}
		fmt.Printf("🔍 STEP 2.13: handleProxyRequest - Permission granted for userRole '%s'\n", userRole)
	} else {
		fmt.Printf("🔍 STEP 2.14: handleProxyRequest - No role restrictions, allowing access\n")
	}
	// If AllowedRoles is empty, allow access (any role including public)

	// Determine target service
	targetService := s.proxyService.GetTargetService(path)
	if targetService == "" {
		s.handleError(c, http.StatusNotFound, models.ErrSvcUnavailable, "Service not found")
		return
	}

	// Prepare request body
	var body interface{}
	if c.Request.Body != nil {
		bodyBytes, err := io.ReadAll(c.Request.Body)
		if err != nil {
			s.handleError(c, http.StatusBadRequest, models.ErrSvcUnavailable, "Failed to read request body")
			return
		}
		if len(bodyBytes) > 0 {
			// Parse JSON body to preserve structure
			if err := json.Unmarshal(bodyBytes, &body); err != nil {
				s.handleError(c, http.StatusBadRequest, models.ErrSvcUnavailable, "Invalid JSON body")
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
		s.handleError(c, http.StatusServiceUnavailable, models.ErrSvcUnavailable, fmt.Sprintf("Backend service error: %v", err))
		return
	}
	defer resp.Body.Close()

	// Copy response headers
	for key, values := range resp.Header {
		for _, value := range values {
			c.Header(key, value)
		}
	}

	// Copy response body
	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		s.handleError(c, http.StatusInternalServerError, models.ErrSvcUnavailable, "Failed to read response body")
		return
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
	userContext, exists := c.Get("user_context")
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
	// Handle dynamic routes like /assets/:id -> /assets
	parts := strings.Split(path, "/")
	if len(parts) > 0 {
		// Remove the last part if it looks like an ID
		lastPart := parts[len(parts)-1]
		if len(lastPart) > 0 && !strings.Contains(lastPart, "/") {
			return strings.Join(parts[:len(parts)-1], "/")
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
