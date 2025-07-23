package api

import (
	"fmt"
	"net/http"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/internal/middleware"
	"order-processor-gateway/internal/services"

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
		// TODO: Add rate limiting middleware
		// s.router.Use(middleware.RateLimitMiddleware(s.redisService, 100, time.Minute))

		// TODO: Add session middleware
		// s.router.Use(middleware.SessionMiddleware(s.redisService))
	}

	// Health check endpoint
	s.router.GET("/health", s.healthCheck)

	// API routes
	api := s.router.Group("/api/v1")
	{
		// Public routes (no auth required)
		api.POST("/auth/login", s.proxyToUserService)
		api.POST("/auth/register", s.proxyToUserService)

		// Protected routes (auth required)
		protected := api.Group("")
		// TODO: Add authentication middleware
		// protected.Use(middleware.AuthMiddleware())
		{
			protected.GET("/auth/profile", s.proxyToUserService)
			protected.POST("/auth/logout", s.proxyToUserService)
			protected.GET("/inventory/assets", s.proxyToInventoryService)
			protected.GET("/inventory/assets/:id", s.proxyToInventoryService)
		}
	}
}

// healthCheck handles health check requests
func (s *Server) healthCheck(c *gin.Context) {
	status := "healthy"
	if s.redisService == nil {
		status = "degraded (no Redis)"
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  status,
		"service": "gateway",
		"redis":   s.redisService != nil,
	})
}

// proxyToUserService proxies requests to user service
func (s *Server) proxyToUserService(c *gin.Context) {
	// TODO: Implement actual proxy logic using s.proxyService
	// TODO: Add request/response transformation
	// TODO: Add caching logic
	// TODO: Add error handling and circuit breaker

	c.JSON(http.StatusOK, gin.H{
		"message": "User service proxy - not implemented yet",
		"service": "user-service",
		"path":    c.Request.URL.Path,
	})
}

// proxyToInventoryService proxies requests to inventory service
func (s *Server) proxyToInventoryService(c *gin.Context) {
	// TODO: Implement actual proxy logic using s.proxyService
	// TODO: Add request/response transformation
	// TODO: Add caching logic
	// TODO: Add error handling and circuit breaker

	c.JSON(http.StatusOK, gin.H{
		"message": "Inventory service proxy - not implemented yet",
		"service": "inventory-service",
		"path":    c.Request.URL.Path,
	})
}

// Start starts the HTTP server
func (s *Server) Start() error {
	addr := fmt.Sprintf("%s:%s", s.config.Server.Host, s.config.Server.Port)
	return s.router.Run(addr)
}
