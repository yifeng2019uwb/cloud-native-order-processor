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
	assert.Equal(t, constants.DefaultTimeout, service.client.Timeout)
}

func TestProxyRequest(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	// Test placeholder implementation
	proxyReq := &models.ProxyRequest{
		Method:        "GET",
		Path:          "/test",
		Headers:       nil,
		Body:          nil,
		TargetService: "test_service",
		TargetPath:    "/test",
		Context: &models.RequestContext{
			RequestID:   "test-123",
			Timestamp:   time.Now(),
			ServiceName: "test_service",
		},
	}
	resp, err := service.ProxyRequest(ctx, proxyReq)

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.Equal(t, 200, resp.StatusCode)
}

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

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.Equal(t, 200, resp.StatusCode)
}

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

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.Equal(t, 200, resp.StatusCode)
}

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

func TestProxyRequestWithDifferentMethods(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	methods := []string{"GET", "POST", "PUT", "DELETE", "PATCH"}

	for _, method := range methods {
		t.Run("Method: "+method, func(t *testing.T) {
			resp, err := service.ProxyRequest(ctx, "http://test-service:8000", "/test", method, nil, nil)

			assert.NoError(t, err)
			assert.NotNil(t, resp)
			assert.Equal(t, 200, resp.StatusCode)
		})
	}
}

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

	resp, err := service.ProxyRequest(ctx, "http://test-service:8000", "/test", "POST", headers, nil)

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.Equal(t, 200, resp.StatusCode)
}

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

	resp, err := service.ProxyRequest(ctx, "http://test-service:8000", "/test", "POST", nil, body)

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.Equal(t, 200, resp.StatusCode)
}

func BenchmarkProxyRequest(b *testing.B) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	for i := 0; i < b.N; i++ {
		_, err := service.ProxyRequest(ctx, "http://test-service:8000", "/test", "GET", nil, nil)
		if err != nil {
			b.Fatalf("ProxyRequest failed: %v", err)
		}
	}
}

func BenchmarkProxyToUserService(b *testing.B) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	for i := 0; i < b.N; i++ {
		_, err := service.ProxyToUserService(ctx, "/auth/login", "POST", nil, nil)
		if err != nil {
			b.Fatalf("ProxyToUserService failed: %v", err)
		}
	}
}

func BenchmarkProxyToInventoryService(b *testing.B) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
		},
	}

	service := NewProxyService(cfg)
	ctx := context.Background()

	for i := 0; i < b.N; i++ {
		_, err := service.ProxyToInventoryService(ctx, "/assets", "GET", nil, nil)
		if err != nil {
			b.Fatalf("ProxyToInventoryService failed: %v", err)
		}
	}
}

func TestProxyServiceEdgeCases(t *testing.T) {
	t.Run("ProxyRequest with Empty URL", func(t *testing.T) {
		cfg := &config.Config{
			Services: config.ServicesConfig{
				UserService:      "http://user-service:8000",
				InventoryService: "http://inventory-service:8001",
			},
		}

		service := NewProxyService(cfg)
		ctx := context.Background()

		resp, err := service.ProxyRequest(ctx, "", "/test", "GET", nil, nil)

		// Should handle empty URL gracefully
		assert.NoError(t, err)
		assert.NotNil(t, resp)
	})

	t.Run("ProxyRequest with Empty Path", func(t *testing.T) {
		cfg := &config.Config{
			Services: config.ServicesConfig{
				UserService:      "http://user-service:8000",
				InventoryService: "http://inventory-service:8001",
			},
		}

		service := NewProxyService(cfg)
		ctx := context.Background()

		resp, err := service.ProxyRequest(ctx, "http://test-service:8000", "", "GET", nil, nil)

		assert.NoError(t, err)
		assert.NotNil(t, resp)
	})

	t.Run("ProxyRequest with Invalid Method", func(t *testing.T) {
		cfg := &config.Config{
			Services: config.ServicesConfig{
				UserService:      "http://user-service:8000",
				InventoryService: "http://inventory-service:8001",
			},
		}

		service := NewProxyService(cfg)
		ctx := context.Background()

		resp, err := service.ProxyRequest(ctx, "http://test-service:8000", "/test", "INVALID_METHOD", nil, nil)

		// Should handle invalid method gracefully
		assert.NoError(t, err)
		assert.NotNil(t, resp)
	})

	t.Run("ProxyRequest with Very Long Headers", func(t *testing.T) {
		cfg := &config.Config{
			Services: config.ServicesConfig{
				UserService:      "http://user-service:8000",
				InventoryService: "http://inventory-service:8001",
			},
		}

		service := NewProxyService(cfg)
		ctx := context.Background()

		longHeaders := map[string]string{
			"X-Very-Long-Header": string(make([]byte, 1000)),
			"X-Another-Long":     string(make([]byte, 500)),
		}

		resp, err := service.ProxyRequest(ctx, "http://test-service:8000", "/test", "GET", longHeaders, nil)

		assert.NoError(t, err)
		assert.NotNil(t, resp)
	})

	t.Run("ProxyRequest with Complex Body", func(t *testing.T) {
		cfg := &config.Config{
			Services: config.ServicesConfig{
				UserService:      "http://user-service:8000",
				InventoryService: "http://inventory-service:8001",
			},
		}

		service := NewProxyService(cfg)
		ctx := context.Background()

		complexBody := map[string]interface{}{
			"nested": map[string]interface{}{
				"deep": map[string]interface{}{
					"structure": []interface{}{
						"item1",
						map[string]interface{}{"key": "value"},
						[]string{"a", "b", "c"},
					},
				},
			},
			"array": []interface{}{
				1, 2, 3, "string", true, nil,
			},
		}

		resp, err := service.ProxyRequest(ctx, "http://test-service:8000", "/test", "POST", nil, complexBody)

		assert.NoError(t, err)
		assert.NotNil(t, resp)
	})
}

func TestProxyServiceErrorHandling(t *testing.T) {
	t.Run("ProxyRequest with Invalid URL", func(t *testing.T) {
		cfg := &config.Config{
			Services: config.ServicesConfig{
				UserService:      "http://user-service:8000",
				InventoryService: "http://inventory-service:8001",
			},
		}

		service := NewProxyService(cfg)
		ctx := context.Background()

		resp, err := service.ProxyRequest(ctx, "invalid-url", "/test", "GET", nil, nil)

		// Should handle invalid URL gracefully
		assert.NoError(t, err)
		assert.NotNil(t, resp)
	})

	t.Run("ProxyRequest with Non-existent Service", func(t *testing.T) {
		cfg := &config.Config{
			Services: config.ServicesConfig{
				UserService:      "http://user-service:8000",
				InventoryService: "http://inventory-service:8001",
			},
		}

		service := NewProxyService(cfg)
		ctx := context.Background()

		resp, err := service.ProxyRequest(ctx, "http://non-existent-service:9999", "/test", "GET", nil, nil)

		// Should handle non-existent service gracefully
		assert.NoError(t, err)
		assert.NotNil(t, resp)
	})
}

func TestProxyServiceIntegration(t *testing.T) {
	t.Run("ProxyToUserService with Different Endpoints", func(t *testing.T) {
		cfg := &config.Config{
			Services: config.ServicesConfig{
				UserService:      "http://user-service:8000",
				InventoryService: "http://inventory-service:8001",
			},
		}

		service := NewProxyService(cfg)
		ctx := context.Background()

		endpoints := []string{
			"/auth/login",
			"/auth/register",
			"/users/profile",
			"/users/settings",
			"/auth/logout",
		}

		for _, endpoint := range endpoints {
			t.Run("Endpoint: "+endpoint, func(t *testing.T) {
				resp, err := service.ProxyToUserService(ctx, endpoint, "GET", nil, nil)

				assert.NoError(t, err)
				assert.NotNil(t, resp)
			})
		}
	})

	t.Run("ProxyToInventoryService with Different Endpoints", func(t *testing.T) {
		cfg := &config.Config{
			Services: config.ServicesConfig{
				UserService:      "http://user-service:8000",
				InventoryService: "http://inventory-service:8001",
			},
		}

		service := NewProxyService(cfg)
		ctx := context.Background()

		endpoints := []string{
			"/assets",
			"/assets/123",
			"/categories",
			"/search",
			"/analytics",
		}

		for _, endpoint := range endpoints {
			t.Run("Endpoint: "+endpoint, func(t *testing.T) {
				resp, err := service.ProxyToInventoryService(ctx, endpoint, "GET", nil, nil)

				assert.NoError(t, err)
				assert.NotNil(t, resp)
			})
		}
	})
}

func TestProxyServicePerformance(t *testing.T) {
	t.Run("Concurrent Proxy Requests", func(t *testing.T) {
		cfg := &config.Config{
			Services: config.ServicesConfig{
				UserService:      "http://user-service:8000",
				InventoryService: "http://inventory-service:8001",
			},
		}

		service := NewProxyService(cfg)
		ctx := context.Background()

		// Run concurrent requests
		results := make(chan error, 10)
		for i := 0; i < 10; i++ {
			go func() {
				_, err := service.ProxyRequest(ctx, "http://test-service:8000", "/test", "GET", nil, nil)
				results <- err
			}()
		}

		// Collect results
		for i := 0; i < 10; i++ {
			err := <-results
			assert.NoError(t, err)
		}
	})
}
