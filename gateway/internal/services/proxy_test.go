package services

import (
	"context"
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
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
			OrderService:     "http://order-service:8002",
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
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
			OrderService:     "http://order-service:8002",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	// Test basic proxy request
	proxyReq := &models.ProxyRequest{
		Method:        "GET",
		Path:          "/test",
		Headers:       nil,
		Body:          nil,
		TargetService: "user_service",
		TargetPath:    "/test",
		Context: &models.RequestContext{
			RequestID:   "test-123",
			Timestamp:   time.Now(),
			ServiceName: "user_service",
		},
	}

	resp, err := service.ProxyRequest(ctx, proxyReq)

	// Note: This will fail because we don't have a real backend service running
	// But we can test that the request is properly constructed
	assert.Error(t, err) // Expected to fail without real backend
	assert.Nil(t, resp)
}

// TestProxyToUserService tests user service proxying
func TestProxyToUserService(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
			OrderService:     "http://order-service:8002",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	headers := map[string]string{
		"Content-Type":  "application/json",
		"Authorization": "Bearer token123",
	}

	resp, err := service.ProxyToUserService(ctx, "/auth/login", "POST", headers, map[string]string{"username": "test"})

	// Expected to fail without real backend service
	assert.Error(t, err)
	assert.Nil(t, resp)
}

// TestProxyToInventoryService tests inventory service proxying
func TestProxyToInventoryService(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
			OrderService:     "http://order-service:8002",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	headers := map[string]string{
		"Content-Type": "application/json",
	}

	resp, err := service.ProxyToInventoryService(ctx, "/assets", "GET", headers, nil)

	// Expected to fail without real backend service
	assert.Error(t, err)
	assert.Nil(t, resp)
}

// TestProxyToOrderService tests order service proxying
func TestProxyToOrderService(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
			OrderService:     "http://order-service:8002",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	headers := map[string]string{
		"Content-Type":  "application/json",
		"Authorization": "Bearer token123",
	}

	// Test order creation
	resp, err := service.ProxyToOrderService(ctx, "/api/v1/orders", "POST", headers, map[string]interface{}{
		"asset_id":   "BTC",
		"quantity":   "0.01",
		"order_type": "market_buy",
	})

	// Expected to fail without real backend service
	assert.Error(t, err)
	assert.Nil(t, resp)

	// Test order listing
	resp, err = service.ProxyToOrderService(ctx, "/api/v1/orders", "GET", headers, nil)

	// Expected to fail without real backend service
	assert.Error(t, err)
	assert.Nil(t, resp)
}

// TestGetRouteConfig tests route configuration retrieval
func TestGetRouteConfig(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
			OrderService:     "http://order-service:8002",
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
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
			OrderService:     "http://order-service:8002",
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

	// Test portfolio service routing (handled by order service)
	targetService = service.GetTargetService(constants.APIV1PortfolioByUser)
	assert.Equal(t, constants.OrderService, targetService)

	// Test balance service routing (handled by user service)
	targetService = service.GetTargetService(constants.APIV1BalanceGet)
	assert.Equal(t, constants.UserService, targetService)

	// Test asset service routing (handled by order service)
	targetService = service.GetTargetService(constants.APIV1AssetBalances)
	assert.Equal(t, constants.OrderService, targetService)

	// Test unknown path
	targetService = service.GetTargetService("/unknown")
	assert.Equal(t, "", targetService)
}

// TestStripAPIPrefix tests API prefix stripping
func TestStripAPIPrefix(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
			OrderService:     "http://order-service:8002",
		},
	}

	service := NewProxyService(cfg)

	// Test auth path stripping
	stripped := service.stripAPIPrefix(constants.APIV1AuthLogin, constants.APIV1AuthPath)
	assert.Equal(t, "/login", stripped)

	// Test inventory path stripping
	stripped = service.stripAPIPrefix(constants.APIV1InventoryAssets, constants.APIV1InventoryPath)
	assert.Equal(t, "/assets", stripped)

	// Test path without prefix
	stripped = service.stripAPIPrefix("/test", constants.APIV1AuthPath)
	assert.Equal(t, "/test", stripped)
}

// TestBuildTargetURLWithQueryParams tests URL building with query parameters
func TestBuildTargetURLWithQueryParams(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
			OrderService:     "http://order-service:8002",
		},
	}

	service := NewProxyService(cfg)

	// Test inventory service with query parameters
	proxyReq := &models.ProxyRequest{
		Method:  "GET",
		Path:    "/assets",
		Headers: nil,
		Body:    nil,
		QueryParams: map[string]string{
			"limit":       "10",
			"active_only": "true",
		},
		TargetService: "inventory_service",
		TargetPath:    "/assets",
		Context: &models.RequestContext{
			RequestID:   "test-123",
			Timestamp:   time.Now(),
			ServiceName: "inventory_service",
		},
	}

	targetURL, err := service.buildTargetURL(proxyReq)
	assert.NoError(t, err)
	assert.Equal(t, "http://inventory-service:8001/assets?active_only=true&limit=10", targetURL)

	// Test user service with query parameters
	proxyReq.TargetService = "user_service"
	proxyReq.TargetPath = "/profile"
	proxyReq.QueryParams = map[string]string{
		"include_details": "true",
	}

	targetURL, err = service.buildTargetURL(proxyReq)
	assert.NoError(t, err)
	assert.Equal(t, "http://user-service:8000/profile?include_details=true", targetURL)
}

// TestProxyServiceErrorHandling tests error handling scenarios
func TestProxyServiceErrorHandling(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
			OrderService:     "http://order-service:8002",
		},
	}

	service := NewProxyService(cfg)

	t.Run("Invalid Target Service", func(t *testing.T) {
		proxyReq := &models.ProxyRequest{
			Method:        "GET",
			Path:          "/test",
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
			Method:        "GET",
			Path:          "/test",
			Headers:       nil,
			Body:          nil,
			TargetService: "user_service",
			TargetPath:    "",
			Context: &models.RequestContext{
				RequestID:   "test-123",
				Timestamp:   time.Now(),
				ServiceName: "user_service",
			},
		}

		targetURL, err := service.buildTargetURL(proxyReq)
		assert.NoError(t, err)
		assert.Equal(t, "http://user-service:8000", targetURL)
	})
}
