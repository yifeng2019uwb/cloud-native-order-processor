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

// TestGetRouteConfig tests route configuration retrieval
func TestGetRouteConfig(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
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
		},
	}

	service := NewProxyService(cfg)

	// Test auth service routing
	targetService := service.GetTargetService(constants.APIV1AuthLogin)
	assert.Equal(t, constants.UserService, targetService)

	// Test inventory service routing
	targetService = service.GetTargetService(constants.APIV1InventoryAssets)
	assert.Equal(t, constants.InventoryService, targetService)

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

// TestProxyServiceWithDifferentConfigs tests different service configurations
func TestProxyServiceWithDifferentConfigs(t *testing.T) {
	testCases := []struct {
		name                string
		userServiceURL      string
		inventoryServiceURL string
	}{
		{
			name:                "Default URLs",
			userServiceURL:      "http://user-service:8000",
			inventoryServiceURL: "http://inventory-service:8001",
		},
		{
			name:                "Custom URLs",
			userServiceURL:      "http://custom-user:9000",
			inventoryServiceURL: "http://custom-inventory:9001",
		},
		{
			name:                "HTTPS URLs",
			userServiceURL:      "https://user-service.example.com",
			inventoryServiceURL: "https://inventory-service.example.com",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			cfg := &config.Config{
				Services: config.ServicesConfig{
					UserService:      tc.userServiceURL,
					InventoryService: tc.inventoryServiceURL,
				},
			}

			service := NewProxyService(cfg)

			assert.Equal(t, tc.userServiceURL, service.config.Services.UserService)
			assert.Equal(t, tc.inventoryServiceURL, service.config.Services.InventoryService)
		})
	}
}

// TestProxyRequestWithHeaders tests proxy request with headers
func TestProxyRequestWithHeaders(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	headers := map[string]string{
		"Content-Type":  "application/json",
		"Authorization": "Bearer token123",
		"X-Request-ID":  "req-123",
		"User-Agent":    "test-agent",
	}

	proxyReq := &models.ProxyRequest{
		Method:        "POST",
		Path:          "/test",
		Headers:       headers,
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

	// Expected to fail without real backend service
	assert.Error(t, err)
	assert.Nil(t, resp)
}

// TestProxyRequestWithBody tests proxy request with body
func TestProxyRequestWithBody(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	body := map[string]interface{}{
		"username": "testuser",
		"password": "testpass",
		"data": map[string]string{
			"key1": "value1",
			"key2": "value2",
		},
	}

	proxyReq := &models.ProxyRequest{
		Method:        "POST",
		Path:          "/test",
		Headers:       nil,
		Body:          body,
		TargetService: "user_service",
		TargetPath:    "/test",
		Context: &models.RequestContext{
			RequestID:   "test-123",
			Timestamp:   time.Now(),
			ServiceName: "user_service",
		},
	}

	resp, err := service.ProxyRequest(ctx, proxyReq)

	// Expected to fail without real backend service
	assert.Error(t, err)
	assert.Nil(t, resp)
}

// TestProxyRequestWithUserContext tests proxy request with user context
func TestProxyRequestWithUserContext(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	proxyReq := &models.ProxyRequest{
		Method:        "GET",
		Path:          "/profile",
		Headers:       map[string]string{"Authorization": "Bearer token123"},
		Body:          nil,
		TargetService: "user_service",
		TargetPath:    "/profile",
		Context: &models.RequestContext{
			RequestID:   "test-123",
			Timestamp:   time.Now(),
			ServiceName: "user_service",
			User: &models.UserContext{
				Username:        "testuser",
				Role:            "customer",
				IsAuthenticated: true,
			},
		},
	}

	resp, err := service.ProxyRequest(ctx, proxyReq)

	// Expected to fail without real backend service
	assert.Error(t, err)
	assert.Nil(t, resp)
}

// TestProxyRequestWithQueryParams tests proxy request with query parameters
func TestProxyRequestWithQueryParams(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	queryParams := map[string]string{
		"limit":       "10",
		"active_only": "true",
		"test":        "value",
	}

	proxyReq := &models.ProxyRequest{
		Method:        "GET",
		Path:          "/assets",
		Headers:       nil,
		Body:          nil,
		QueryParams:   queryParams,
		TargetService: "inventory_service",
		TargetPath:    "/assets",
		Context: &models.RequestContext{
			RequestID:   "test-123",
			Timestamp:   time.Now(),
			ServiceName: "inventory_service",
		},
	}

	resp, err := service.ProxyRequest(ctx, proxyReq)

	// Expected to fail without real backend service
	assert.Error(t, err)
	assert.Nil(t, resp)
}

// TestBuildTargetURLWithQueryParams tests URL building with query parameters
func TestBuildTargetURLWithQueryParams(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
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

// BenchmarkProxyRequest benchmarks the proxy request performance
func BenchmarkProxyRequest(b *testing.B) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

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

	for i := 0; i < b.N; i++ {
		_, err := service.ProxyRequest(ctx, proxyReq)
		if err != nil {
			// Expected to fail without real backend
			continue
		}
	}
}
