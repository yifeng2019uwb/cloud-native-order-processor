package api

import (
	"fmt"
	"net/http"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/internal/middleware"
	"order-processor-gateway/internal/services"
	"order-processor-gateway/pkg/constants"

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
	s.router.GET(constants.HealthPath, s.healthCheck)

	// API routes
	api := s.router.Group(constants.APIV1Path)
	{
		// Public routes (no auth required)
		api.POST(constants.AuthLoginPath, s.proxyToUserService)
		api.POST(constants.AuthRegisterPath, s.proxyToUserService)

		// Protected routes (auth required)
		protected := api.Group("")
		// TODO: Add authentication middleware
		// protected.Use(middleware.AuthMiddleware())
		{
			protected.GET(constants.AuthProfilePath, s.proxyToUserService)
			protected.POST(constants.AuthLogoutPath, s.proxyToUserService)
			protected.GET(constants.InventoryAssetsPath, s.proxyToInventoryService)
			protected.GET(constants.InventoryAssetByIDPath, s.proxyToInventoryService)
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

// proxyToUserService proxies requests to user service
func (s *Server) proxyToUserService(c *gin.Context) {
	// TODO: Implement actual proxy logic using s.proxyService
	// TODO: Add request/response transformation
	// TODO: Add caching logic
	// TODO: Add error handling and circuit breaker

	c.JSON(http.StatusOK, gin.H{
		"message": constants.ProxyUserServiceNotImplemented,
		"service": constants.ServiceNameUser,
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
		"message": constants.ProxyInventoryServiceNotImplemented,
		"service": constants.ServiceNameInventory,
		"path":    c.Request.URL.Path,
	})
}

// Start starts the HTTP server
func (s *Server) Start() error {
	addr := fmt.Sprintf("%s:%s", s.config.Server.Host, s.config.Server.Port)
	return s.router.Run(addr)
}
