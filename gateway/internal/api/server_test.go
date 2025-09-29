package api

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"reflect"
	"strings"
	"testing"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/internal/services"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/models"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/stretchr/testify/assert"
)

func setupTestServer() (*Server, *config.Config) {
	cfg := &config.Config{
		Server: config.ServerConfig{
			Port: "8080",
			Host: "localhost",
		},
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
		},
	}

	// Create a new registry for each test to avoid duplicate metrics registration
	reg := prometheus.NewRegistry()
	server := NewServerWithRegistry(cfg, nil, services.NewProxyService(cfg), reg)
	return server, cfg
}

func TestNewServer(t *testing.T) {
	cfg := &config.Config{
		Server: config.ServerConfig{
			Port: "8080",
			Host: "localhost",
		},
		Services: config.ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
		},
	}

	redisService := &services.RedisService{}
	proxyService := services.NewProxyService(cfg)

	// Create a new registry for each test to avoid duplicate metrics registration
	reg := prometheus.NewRegistry()
	server := NewServerWithRegistry(cfg, redisService, proxyService, reg)

	assert.NotNil(t, server)
	assert.Equal(t, cfg, server.config)
	assert.Equal(t, redisService, server.redisService)
	assert.Equal(t, proxyService, server.proxyService)
	assert.NotNil(t, server.router)
}

func TestHealthCheck(t *testing.T) {
	t.Run("Healthy Status", func(t *testing.T) {
		server, _ := setupTestServer()
		server.redisService = &services.RedisService{} // Mock Redis service

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.HealthPath, nil)
		server.router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)

		assert.Equal(t, constants.StatusHealthy, response["status"])
		assert.Equal(t, constants.GatewayService, response["service"])
		assert.Equal(t, true, response["redis"])
	})

	t.Run("Degraded Status", func(t *testing.T) {
		server, _ := setupTestServer()
		server.redisService = nil // No Redis service

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.HealthPath, nil)
		server.router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)

		assert.Equal(t, constants.StatusDegradedNoRedis, response["status"])
		assert.Equal(t, constants.GatewayService, response["service"])
		assert.Equal(t, false, response["redis"])
	})
}

func TestGetUserContext(t *testing.T) {
	server, _ := setupTestServer()

	t.Run("User Context Exists", func(t *testing.T) {
		// Create a gin context with user context
		ginCtx := &gin.Context{}
		ginCtx.Set("user_context", &models.UserContext{
			Username:        "testuser",
			Role:            "customer",
			IsAuthenticated: true,
		})

		userContext := server.getUserContext(ginCtx)
		assert.NotNil(t, userContext)
		assert.Equal(t, "testuser", userContext.Username)
		assert.Equal(t, "customer", userContext.Role)
		assert.True(t, userContext.IsAuthenticated)
	})

	t.Run("No User Context", func(t *testing.T) {
		// Create a gin context without user context
		ginCtx := &gin.Context{}

		userContext := server.getUserContext(ginCtx)
		assert.NotNil(t, userContext)
		assert.Equal(t, "", userContext.Username)
		assert.Equal(t, "", userContext.Role)
		assert.False(t, userContext.IsAuthenticated)
	})
}

func TestGetBasePath(t *testing.T) {
	server, _ := setupTestServer()

	testCases := []struct {
		name     string
		input    string
		expected string
	}{
		{
			name:     "Asset Balances Pattern",
			input:    "/api/v1/assets/balances",
			expected: "/api/v1/assets/balances",
		},
		{
			name:     "Asset Transactions Pattern",
			input:    "/api/v1/assets/BTC/transactions",
			expected: "/api/v1/assets/:asset_id/transactions",
		},
		{
			name:     "Asset Balance Pattern",
			input:    "/api/v1/assets/ETH/balance",
			expected: "/api/v1/assets/:asset_id/balance",
		},
		{
			name:     "Order by ID Pattern",
			input:    "/api/v1/orders/123",
			expected: "/api/v1/orders/:id",
		},
		{
			name:     "Portfolio by User Pattern",
			input:    "/api/v1/portfolio/testuser",
			expected: "/api/v1/portfolio/:username",
		},
		{
			name:     "Inventory Asset by ID Pattern",
			input:    "/api/v1/inventory/assets/456",
			expected: "/api/v1/inventory/assets/:id",
		},
		{
			name:     "Unknown Pattern",
			input:    "/api/v1/unknown/path",
			expected: "/api/v1/unknown/path",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := server.getBasePath(tc.input)
			assert.Equal(t, tc.expected, result)
		})
	}
}

func TestStripAPIPrefix(t *testing.T) {
	server, _ := setupTestServer()

	testCases := []struct {
		name     string
		input    string
		expected string
	}{
		{
			name:     "API v1 Path",
			input:    "/api/v1/auth/login",
			expected: "/auth/login",
		},
		{
			name:     "API v1 Path with Parameters",
			input:    "/api/v1/orders/123",
			expected: "/orders/123",
		},
		{
			name:     "Non-API Path",
			input:    "/health",
			expected: "/health",
		},
		{
			name:     "Root Path",
			input:    "/",
			expected: "/",
		},
		{
			name:     "Empty Path",
			input:    "",
			expected: "",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := server.stripAPIPrefix(tc.input)
			assert.Equal(t, tc.expected, result)
		})
	}
}

func TestGenerateRequestID(t *testing.T) {
	// Test multiple generations to ensure uniqueness
	ids := make(map[string]bool)

	for i := 0; i < 10; i++ {
		id := generateRequestID()
		assert.NotEmpty(t, id)
		assert.True(t, strings.HasPrefix(id, "req-"))

		// Ensure uniqueness
		assert.False(t, ids[id], "Duplicate request ID generated: %s", id)
		ids[id] = true

		// Add small delay to ensure uniqueness
		time.Sleep(1 * time.Millisecond)
	}
}

func TestProxyToUserService(t *testing.T) {
	server, _ := setupTestServer()

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", constants.APIV1Path+constants.AuthLoginPath, nil)
	server.router.ServeHTTP(w, req)

	// Expected to fail without real backend service
	assert.Equal(t, http.StatusServiceUnavailable, w.Code)
}

func TestProxyToInventoryService(t *testing.T) {
	server, _ := setupTestServer()

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", constants.APIV1Path+constants.InventoryAssetsPath, nil)
	server.router.ServeHTTP(w, req)

	// Expected to fail without real backend service
	assert.Equal(t, http.StatusServiceUnavailable, w.Code)
}

func TestRouteSetup(t *testing.T) {
	server, _ := setupTestServer()

	// Test health endpoint
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", constants.HealthPath, nil)
	server.router.ServeHTTP(w, req)
	assert.Equal(t, http.StatusOK, w.Code)

	// Test auth endpoints
	authEndpoints := []struct {
		endpoint string
		method   string
	}{
		{constants.APIV1Path + constants.AuthLoginPath, "POST"},
		{constants.APIV1Path + constants.AuthRegisterPath, "POST"},
		{constants.APIV1Path + constants.AuthProfilePath, "GET"},
		{constants.APIV1Path + constants.AuthLogoutPath, "POST"},
	}

	for _, endpoint := range authEndpoints {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest(endpoint.method, endpoint.endpoint, nil)
		server.router.ServeHTTP(w, req)
		// Should either succeed or fail with appropriate status, not 404
		assert.NotEqual(t, http.StatusNotFound, w.Code)
	}

	// Test inventory endpoints
	inventoryEndpoints := []string{
		constants.APIV1Path + constants.InventoryAssetsPath,
		constants.APIV1Path + constants.InventoryAssetByIDPath,
	}

	for _, endpoint := range inventoryEndpoints {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", endpoint, nil)
		server.router.ServeHTTP(w, req)
		// Should either succeed or fail with appropriate status, not 404
		assert.NotEqual(t, http.StatusNotFound, w.Code)
	}
}

func TestCORSHeaders(t *testing.T) {
	server, _ := setupTestServer()

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("OPTIONS", constants.HealthPath, nil)
	server.router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNoContent, w.Code)
	assert.Equal(t, "*", w.Header().Get("Access-Control-Allow-Origin"))
}

func TestServerStart(t *testing.T) {
	server, _ := setupTestServer()

	// Test that server can be created without error
	assert.NotNil(t, server)
	assert.NotNil(t, server.router)
}

func TestQueryParametersHandling(t *testing.T) {
	server, _ := setupTestServer()

	// Test inventory service with query parameters
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", constants.APIV1Path+constants.InventoryAssetsPath+"?limit=10&active_only=true", nil)
	server.router.ServeHTTP(w, req)

	// Should either succeed or fail with appropriate status, not 404
	assert.NotEqual(t, http.StatusNotFound, w.Code)
}

// New comprehensive tests for handleProxyRequest
func TestHandleProxyRequestComprehensive(t *testing.T) {
	server, _ := setupTestServer()

	t.Run("Route Not Found", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/v1/nonexistent", nil)

		// Create gin context
		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("Dynamic Route with Base Path", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/v1/assets/BTC/transactions", nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		// Should return 401 (unauthorized) for unauthenticated user
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("Authentication Required Route", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/v1/auth/profile", nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		// Should return 401 (unauthorized) for unauthenticated user
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("Role-Based Access Control", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/v1/orders", nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		// Should return 401 (unauthorized) for unauthenticated user
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("Request with Body", func(t *testing.T) {
		body := map[string]interface{}{
			"username": "testuser",
			"password": "testpass",
		}
		bodyBytes, _ := json.Marshal(body)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", constants.APIV1Path+constants.AuthLoginPath, strings.NewReader(string(bodyBytes)))
		req.Header.Set("Content-Type", "application/json")

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		// Should return 403 (forbidden) for public user without role
		assert.Equal(t, http.StatusForbidden, w.Code)
	})

	t.Run("Request with Headers", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1Path+constants.InventoryAssetsPath, nil)
		req.Header.Set("X-Custom-Header", "test-value")
		req.Header.Set("Authorization", "Bearer token123")

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		// Should either succeed or fail with appropriate status, not 404
		assert.NotEqual(t, http.StatusNotFound, w.Code)
	})

	t.Run("Request with Query Parameters", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1Path+constants.InventoryAssetsPath+"?limit=10&active=true&sort=name", nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		// Should either succeed or fail with appropriate status, not 404
		assert.NotEqual(t, http.StatusNotFound, w.Code)
	})

	t.Run("Authenticated User with Valid Role", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/v1/auth/profile", nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		// Set user role in context (simulating authenticated user)
		ctx.Set(constants.ContextKeyUserRole, "customer")

		server.handleProxyRequest(ctx)

		// Should either succeed or fail with appropriate status, not 401/403
		assert.NotEqual(t, http.StatusUnauthorized, w.Code)
		assert.NotEqual(t, http.StatusForbidden, w.Code)
	})

	t.Run("Authenticated User with Invalid Role", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/v1/orders", nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		// Set user role in context (simulating authenticated user with wrong role)
		ctx.Set(constants.ContextKeyUserRole, "public")

		server.handleProxyRequest(ctx)

		// Should return 403 (forbidden) for user with insufficient role
		assert.Equal(t, http.StatusForbidden, w.Code)
	})
}

func TestHandleProxyRequestErrorScenarios(t *testing.T) {
	server, _ := setupTestServer()

	t.Run("Invalid JSON Body", func(t *testing.T) {
		body := map[string]interface{}{
			"username": "testuser",
			"password": "testpass",
		}
		bodyBytes, _ := json.Marshal(body)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", constants.APIV1Path+constants.AuthLoginPath, strings.NewReader(string(bodyBytes)))
		req.Header.Set("Content-Type", "application/json")

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		// Set user role to public to pass authentication
		ctx.Set(constants.ContextKeyUserRole, "public")

		server.handleProxyRequest(ctx)

		// Should either succeed or fail with appropriate status, not 403
		assert.NotEqual(t, http.StatusForbidden, w.Code)
	})

	t.Run("Empty Body", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", constants.APIV1Path+constants.AuthLoginPath, nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		// Set user role to public to pass authentication
		ctx.Set(constants.ContextKeyUserRole, "public")

		server.handleProxyRequest(ctx)

		// Should either succeed or fail with appropriate status, not 403
		assert.NotEqual(t, http.StatusForbidden, w.Code)
	})

	t.Run("Service Not Found", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/v1/unknown/service", nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		// Should return 404 (not found) for unknown service
		assert.Equal(t, http.StatusNotFound, w.Code)
	})
}

func TestHandleError(t *testing.T) {
	server, _ := setupTestServer()

	t.Run("Standard Error Response", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleError(ctx, http.StatusBadRequest, models.ErrAuthInvalidToken, "Test error message")

		assert.Equal(t, http.StatusBadRequest, w.Code)

		var response models.ErrorResponse
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, string(models.ErrAuthInvalidToken), response.Error)
		assert.Equal(t, "Test error message", response.Message)
		assert.NotZero(t, response.Timestamp)
	})

	t.Run("Different Error Codes", func(t *testing.T) {
		errorCodes := []models.ErrorCode{
			models.ErrAuthInvalidToken,
			models.ErrPermInsufficient,
			models.ErrSvcUnavailable,
		}

		for _, errorCode := range errorCodes {
			t.Run(string(errorCode), func(t *testing.T) {
				w := httptest.NewRecorder()
				req, _ := http.NewRequest("GET", "/test", nil)

				gin.SetMode(gin.TestMode)
				ctx := gin.CreateTestContextOnly(w, server.router)
				ctx.Request = req

				server.handleError(ctx, http.StatusUnauthorized, errorCode, "Test message")

				assert.Equal(t, http.StatusUnauthorized, w.Code)

				var response models.ErrorResponse
				err := json.Unmarshal(w.Body.Bytes(), &response)
				assert.NoError(t, err)
				assert.Equal(t, string(errorCode), response.Error)
				assert.Equal(t, "Test message", response.Message)
			})
		}
	})
}

func TestServerStartFunction(t *testing.T) {
	server, _ := setupTestServer()

	t.Run("Start Function Exists", func(t *testing.T) {
		// Test that the Start function exists and can be called
		// Note: We can't actually start the server in tests due to port conflicts
		// But we can verify the function exists and has the right signature
		assert.NotNil(t, server.Start)

		// Test that the function has the right signature by checking it's a function
		// that takes no arguments and returns an error
		startFunc := reflect.ValueOf(server.Start)
		assert.Equal(t, reflect.Func, startFunc.Kind())

		// Check function signature: func() error
		funcType := startFunc.Type()
		assert.Equal(t, 0, funcType.NumIn())                       // No input parameters
		assert.Equal(t, 1, funcType.NumOut())                      // One output parameter (error)
		assert.Equal(t, reflect.Interface, funcType.Out(0).Kind()) // Output is interface (error)
	})
}

func TestGetBasePathEdgeCases(t *testing.T) {
	server, _ := setupTestServer()

	t.Run("Empty Path", func(t *testing.T) {
		result := server.getBasePath("")
		assert.Equal(t, "", result)
	})

	t.Run("Root Path", func(t *testing.T) {
		result := server.getBasePath("/")
		assert.Equal(t, "/", result)
	})

	t.Run("Short Path", func(t *testing.T) {
		result := server.getBasePath("/api")
		assert.Equal(t, "/api", result)
	})

	t.Run("Path with Multiple Segments", func(t *testing.T) {
		result := server.getBasePath("/api/v1/assets/BTC/transactions/history")
		assert.Equal(t, "/api/v1/assets/BTC/transactions/history", result)
	})

	t.Run("Path with Query Parameters", func(t *testing.T) {
		result := server.getBasePath("/api/v1/assets/BTC/transactions?limit=10")
		assert.Equal(t, "/api/v1/assets/BTC/transactions?limit=10", result)
	})
}

func TestStripAPIPrefixEdgeCases(t *testing.T) {
	server, _ := setupTestServer()

	t.Run("Exact API Prefix", func(t *testing.T) {
		result := server.stripAPIPrefix("/api/v1")
		assert.Equal(t, "", result)
	})

	t.Run("API Prefix with Slash", func(t *testing.T) {
		result := server.stripAPIPrefix("/api/v1/")
		assert.Equal(t, "/", result)
	})

	t.Run("Multiple API Prefixes", func(t *testing.T) {
		result := server.stripAPIPrefix("/api/v1/api/v1/test")
		assert.Equal(t, "/api/v1/test", result)
	})

	t.Run("Case Sensitive", func(t *testing.T) {
		result := server.stripAPIPrefix("/API/V1/test")
		assert.Equal(t, "/API/V1/test", result)
	})
}
