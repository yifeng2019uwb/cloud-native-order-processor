package services

import (
	"context"
	"net/http"
	"strings"
	"testing"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/models"

	"github.com/stretchr/testify/assert"
)

// TestNewProxyService tests proxy service creation
func TestNewProxyService(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      constants.DefaultUserServiceURL,
			InventoryService: constants.DefaultInventoryServiceURL,
			OrderService:     constants.DefaultOrderServiceURL,
		},
	}

	service := NewProxyService(cfg)

	assert.NotNil(t, service)
	assert.Equal(t, cfg, service.config)
	assert.NotNil(t, service.client)
}

// TestProxyRequest tests the new struct-based ProxyRequest
func TestProxyRequest(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      constants.DefaultUserServiceURL,
			InventoryService: constants.DefaultInventoryServiceURL,
			OrderService:     constants.DefaultOrderServiceURL,
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	// Test basic proxy request
	proxyReq := &models.ProxyRequest{
		Method:        http.MethodGet,
		Path:          constants.APIV1Path + "/test",
		Headers:       nil,
		Body:          nil,
		TargetService: constants.UserService,
		TargetPath:    "/test",
		Context: &models.RequestContext{
			RequestID:   "test-123",
			Timestamp:   time.Now(),
			ServiceName: constants.UserService,
		},
	}

	resp, err := service.ProxyRequest(ctx, proxyReq)

	// Note: This will fail because we don't have a real backend service running
	// But we can test that the request is properly constructed
	assert.Error(t, err) // Expected to fail without real backend
	assert.Nil(t, resp)
}

// TestGetRouteConfig tests route configuration retrieval
func TestGetRouteConfig(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      constants.DefaultUserServiceURL,
			InventoryService: constants.DefaultInventoryServiceURL,
			OrderService:     constants.DefaultOrderServiceURL,
		},
	}

	service := NewProxyService(cfg)

	// Test existing route
	routeConfig, exists := service.GetRouteConfig(constants.APIV1AuthLogin)
	assert.True(t, exists)
	assert.NotNil(t, routeConfig)
	assert.Equal(t, constants.APIV1AuthLogin, routeConfig.Path)
	assert.False(t, routeConfig.RequiresAuth) // Login should not require auth

	// Test non-existing route
	routeConfig, exists = service.GetRouteConfig("/non-existing")
	assert.False(t, exists)
	assert.Nil(t, routeConfig)
}

// TestGetTargetService tests target service determination
func TestGetTargetService(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      constants.DefaultUserServiceURL,
			InventoryService: constants.DefaultInventoryServiceURL,
			OrderService:     constants.DefaultOrderServiceURL,
		},
	}

	service := NewProxyService(cfg)

	// Test auth service routing
	targetService := service.GetTargetService(constants.APIV1AuthLogin)
	assert.Equal(t, constants.UserService, targetService)

	// Test inventory service routing
	targetService = service.GetTargetService(constants.APIV1InventoryAssets)
	assert.Equal(t, constants.InventoryService, targetService)

	// Test order service routing
	targetService = service.GetTargetService(constants.APIV1Orders)
	assert.Equal(t, constants.OrderService, targetService)

	// Test portfolio service routing (handled by user service)
	targetService = service.GetTargetService(constants.APIV1PortfolioPath)
	assert.Equal(t, constants.UserService, targetService)

	// Test balance service routing (handled by user service)
	targetService = service.GetTargetService(constants.APIV1BalanceGet)
	assert.Equal(t, constants.UserService, targetService)

	// Test asset balance routing (handled by user service)
	targetService = service.GetTargetService(constants.APIV1AssetBalanceByID)
	assert.Equal(t, constants.UserService, targetService)

	// Test unknown path
	targetService = service.GetTargetService("/unknown")
	assert.Equal(t, "", targetService)
}

// TestBuildTargetURLWithQueryParams tests URL building with query parameters
func TestBuildTargetURLWithQueryParams(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      constants.DefaultUserServiceURL,
			InventoryService: constants.DefaultInventoryServiceURL,
			OrderService:     constants.DefaultOrderServiceURL,
		},
	}

	service := NewProxyService(cfg)

	// Test inventory service with query parameters
	proxyReq := &models.ProxyRequest{
		Method:  http.MethodGet,
		Path:    constants.APIV1InventoryAssets,
		Headers: nil,
		Body:    nil,
		QueryParams: map[string]string{
			"limit":       "10",
			"active_only": "true",
		},
		TargetService: constants.InventoryService,
		TargetPath:    "/assets",
		Context: &models.RequestContext{
			RequestID:   "test-123",
			Timestamp:   time.Now(),
			ServiceName: constants.InventoryService,
		},
	}

	targetURL, err := service.buildTargetURL(proxyReq)
	assert.NoError(t, err)
	assert.Equal(t, constants.DefaultInventoryServiceURL+"/assets?active_only=true&limit=10", targetURL)

	// Test user service with query parameters
	proxyReq.TargetService = constants.UserService
	proxyReq.TargetPath = constants.AuthProfilePath
	proxyReq.QueryParams = map[string]string{
		"include_details": "true",
	}

	targetURL, err = service.buildTargetURL(proxyReq)
	assert.NoError(t, err)
	assert.Equal(t, constants.DefaultUserServiceURL+constants.AuthProfilePath+"?include_details=true", targetURL)
}

// TestProxyServiceErrorHandling tests error handling scenarios
func TestProxyServiceErrorHandling(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      constants.DefaultUserServiceURL,
			InventoryService: constants.DefaultInventoryServiceURL,
			OrderService:     constants.DefaultOrderServiceURL,
		},
	}

	service := NewProxyService(cfg)

	t.Run("Invalid Target Service", func(t *testing.T) {
		proxyReq := &models.ProxyRequest{
			Method:        http.MethodGet,
			Path:          constants.APIV1Path + "/test",
			Headers:       nil,
			Body:          nil,
			TargetService: "invalid_service",
			TargetPath:    "/test",
			Context: &models.RequestContext{
				RequestID:   "test-123",
				Timestamp:   time.Now(),
				ServiceName: "invalid_service",
			},
		}

		_, err := service.buildTargetURL(proxyReq)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "unknown target service")
	})

	t.Run("Empty Target Path", func(t *testing.T) {
		proxyReq := &models.ProxyRequest{
			Method:        http.MethodGet,
			Path:          constants.APIV1Path + "/test",
			Headers:       nil,
			Body:          nil,
			TargetService: constants.UserService,
			TargetPath:    "",
			Context: &models.RequestContext{
				RequestID:   "test-123",
				Timestamp:   time.Now(),
				ServiceName: constants.UserService,
			},
		}

		targetURL, err := service.buildTargetURL(proxyReq)
		assert.NoError(t, err)
		assert.Equal(t, constants.DefaultUserServiceURL, targetURL)
	})
}

func TestGetCircuitBreakerStatus(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      constants.DefaultUserServiceURL,
			InventoryService: constants.DefaultInventoryServiceURL,
			OrderService:     constants.DefaultOrderServiceURL,
			AuthService:      constants.DefaultAuthServiceURL,
			InsightsService:  constants.DefaultInsightsServiceURL,
		},
	}
	service := NewProxyService(cfg)

	status := service.GetCircuitBreakerStatus()

	assert.Contains(t, status, constants.UserService)
	assert.Contains(t, status, constants.InventoryService)
	assert.Contains(t, status, constants.OrderService)
	assert.Contains(t, status, constants.AuthService)
	assert.Contains(t, status, constants.InsightsService)

	for _, m := range status {
		assert.Contains(t, m, constants.CircuitBreakerFieldState)
		assert.Contains(t, m, constants.CircuitBreakerFieldFailureCount)
		assert.Contains(t, m, constants.CircuitBreakerFieldServiceName)
		assert.Equal(t, constants.CircuitBreakerStateClosed, m[constants.CircuitBreakerFieldState])
	}
}

func TestBuildTargetURL_InsightsAndAuth(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      constants.DefaultUserServiceURL,
			InventoryService: constants.DefaultInventoryServiceURL,
			OrderService:     constants.DefaultOrderServiceURL,
			AuthService:      constants.DefaultAuthServiceURL,
			InsightsService:  constants.DefaultInsightsServiceURL,
		},
	}
	service := NewProxyService(cfg)

	t.Run("InsightsService", func(t *testing.T) {
		backendPath := strings.TrimPrefix(constants.APIV1InsightsPortfolio, constants.APIV1Path)
		proxyReq := &models.ProxyRequest{
			Method:        http.MethodGet,
			Path:          constants.APIV1InsightsPortfolio,
			TargetService: constants.InsightsService,
			TargetPath:    backendPath,
			Context:       &models.RequestContext{RequestID: "req-1", Timestamp: time.Now(), ServiceName: constants.InsightsService},
		}
		targetURL, err := service.buildTargetURL(proxyReq)
		assert.NoError(t, err)
		assert.Equal(t, constants.DefaultInsightsServiceURL+backendPath, targetURL)
	})

	t.Run("AuthService", func(t *testing.T) {
		proxyReq := &models.ProxyRequest{
			Method:        http.MethodPost,
			Path:          constants.APIV1AuthLogin,
			TargetService: constants.AuthService,
			TargetPath:    constants.AuthLoginPath,
			Context:       &models.RequestContext{RequestID: "req-1", Timestamp: time.Now(), ServiceName: constants.AuthService},
		}
		targetURL, err := service.buildTargetURL(proxyReq)
		assert.NoError(t, err)
		assert.Equal(t, constants.DefaultAuthServiceURL+constants.AuthLoginPath, targetURL)
	})
}

func TestProxyRequest_NoCircuitBreakerForService_ReturnsError(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      constants.DefaultUserServiceURL,
			InventoryService: constants.DefaultInventoryServiceURL,
			OrderService:     constants.DefaultOrderServiceURL,
		},
	}
	service := NewProxyService(cfg)
	ctx := context.Background()

	proxyReq := &models.ProxyRequest{
		Method:        http.MethodGet,
		Path:          constants.APIV1Path + "/test",
		TargetService: "nonexistent_service",
		TargetPath:    "/test",
		Context:       &models.RequestContext{RequestID: "req-1", Timestamp: time.Now(), ServiceName: "nonexistent_service"},
	}

	resp, err := service.ProxyRequest(ctx, proxyReq)

	assert.Error(t, err)
	assert.Nil(t, resp)
	assert.Contains(t, err.Error(), "no circuit breaker found")
}
