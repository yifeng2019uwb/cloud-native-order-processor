package api

import (
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
			protectedAuth.Use(middleware.AuthMiddleware())
			{
				protectedAuth.GET("/profile", s.handleProxyRequest)
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
	// Get route configuration
	path := c.Request.URL.Path
	routeConfig, exists := s.proxyService.GetRouteConfig(path)

	if !exists {
		// Handle dynamic routes (like /assets/:id)
		basePath := s.getBasePath(path)
		routeConfig, exists = s.proxyService.GetRouteConfig(basePath)
		if !exists {
			s.handleError(c, http.StatusNotFound, models.ErrSvcUnavailable, "Route not found")
			return
		}
	}

	// Check authentication requirements
	if routeConfig.RequiresAuth {
		userRole := c.GetString(constants.ContextKeyUserRole)
		if userRole == constants.RolePublic {
			s.handleError(c, http.StatusUnauthorized, models.ErrAuthInvalidToken, "Authentication required")
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
			s.handleError(c, http.StatusForbidden, models.ErrPermInsufficient, "Insufficient permissions")
			return
		}
	}

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
			body = string(bodyBytes)
		}
	}

	// Prepare headers
	headers := make(map[string]string)
	for key, values := range c.Request.Header {
		headers[key] = values[0] // Take first value
	}

	// Create proxy request
	proxyReq := &models.ProxyRequest{
		Method:        c.Request.Method,
		Path:          path,
		Headers:       headers,
		Body:          body,
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
			Role:            constants.RolePublic,
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
