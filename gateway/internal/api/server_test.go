package api

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"net/http/httptest"
	"reflect"
	"strconv"
	"strings"
	"testing"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/internal/services"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/models"

	"github.com/alicebob/miniredis/v2"
	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func setupTestServer() (*Server, *config.Config) {
	cfg := &config.Config{
		Server: config.ServerConfig{
			Port: strconv.Itoa(constants.DefaultPort),
			Host: constants.DefaultHost,
		},
		Services: config.ServicesConfig{
			UserService:      constants.DefaultUserServiceURL,
			InventoryService: constants.DefaultInventoryServiceURL,
		},
	}

	// Create a new registry for each test to avoid duplicate metrics registration
	reg := prometheus.NewRegistry()
	server := NewServerWithRegistry(cfg, nil, services.NewProxyService(cfg), reg)
	return server, cfg
}

// errReader is an io.Reader that always returns an error (for testing body read failures).
type errReader struct{ err error }

func (e *errReader) Read(_ []byte) (int, error) { return 0, e.err }

func TestNewServer(t *testing.T) {
	cfg := &config.Config{
		Server: config.ServerConfig{
			Port: strconv.Itoa(constants.DefaultPort),
			Host: constants.DefaultHost,
		},
		Services: config.ServicesConfig{
			UserService:      constants.DefaultUserServiceURL,
			InventoryService: constants.DefaultInventoryServiceURL,
		},
	}

	redisService := &services.RedisService{}
	proxyService := services.NewProxyService(cfg)

	// Create a new registry for each test to avoid duplicate metrics registration
	reg := prometheus.NewRegistry()
	server := NewServerWithRegistry(cfg, redisService, proxyService, reg)

	assert.NotNil(t, server)
	assert.Equal(t, cfg, server.config)
	assert.Equal(t, proxyService, server.proxyService)
	assert.NotNil(t, server.router)
}

func TestNewServerSimple(t *testing.T) {
	cfg := &config.Config{
		Server: config.ServerConfig{
			Port: strconv.Itoa(constants.DefaultPort),
			Host: constants.DefaultHost,
		},
		Services: config.ServicesConfig{
			UserService:      constants.DefaultUserServiceURL,
			InventoryService: constants.DefaultInventoryServiceURL,
		},
	}

	redisService := &services.RedisService{}
	proxyService := services.NewProxyService(cfg)

	// Test NewServer (not NewServerWithRegistry)
	server := NewServer(cfg, redisService, proxyService)

	assert.NotNil(t, server)
	assert.Equal(t, cfg, server.config)
	assert.Equal(t, proxyService, server.proxyService)
	assert.NotNil(t, server.router)
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

func TestHealthCheck_ResponseShape(t *testing.T) {
	server, _ := setupTestServer()

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", constants.HealthPath, nil)
	server.router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	var body map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &body)
	assert.NoError(t, err)
	assert.Contains(t, body, constants.JSONFieldStatus)
	assert.Contains(t, body, constants.JSONFieldService)
	assert.Contains(t, body, constants.JSONFieldRedis)
	assert.Equal(t, constants.GatewayService, body[constants.JSONFieldService])
	// With nil redis from setupTestServer, status should be degraded
	assert.Equal(t, constants.StatusDegradedNoRedis, body[constants.JSONFieldStatus])
	assert.Equal(t, false, body[constants.JSONFieldRedis])
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
			name:     "Balance Asset by ID Pattern",
			input:    "/api/v1/balance/asset/BTC",
			expected: constants.BalanceAssetByIDPattern,
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

	// Expected to fail without real backend (503 or 403 when sandbox blocks)
	assert.Contains(t, []int{http.StatusServiceUnavailable, http.StatusForbidden}, w.Code)
}

func TestProxyToInventoryService(t *testing.T) {
	server, _ := setupTestServer()

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", constants.APIV1Path+constants.InventoryAssetsPath, nil)
	server.router.ServeHTTP(w, req)

	assert.Contains(t, []int{http.StatusServiceUnavailable, http.StatusForbidden}, w.Code)
}

func TestMetricsEndpoint(t *testing.T) {
	server, _ := setupTestServer()

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", constants.MetricsPath, nil)
	server.router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	assert.Contains(t, w.Header().Get("Content-Type"), "text/plain")
	// Prometheus endpoint should expose some metric (e.g. go_ or gateway_)
	body := w.Body.String()
	assert.True(t, strings.Contains(body, "go_") || strings.Contains(body, "gateway_") || len(body) > 100)
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
		req, _ := http.NewRequest("GET", constants.APIV1Path+"/nonexistent", nil)

		// Create gin context
		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		assert.Equal(t, constants.StatusNotFound, w.Code)
	})

	t.Run("Dynamic Route with Base Path", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1Path+"/assets/BTC/transactions", nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		assert.Equal(t, constants.StatusUnauthorized, w.Code)
	})

	t.Run("Authentication Required Route", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1AuthProfile, nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		assert.Equal(t, constants.StatusUnauthorized, w.Code)
	})

	t.Run("Protected route requires auth", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1Orders, nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		assert.Equal(t, constants.StatusUnauthorized, w.Code)
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

		assert.Contains(t, []int{constants.StatusServiceUnavailable, constants.StatusForbidden}, w.Code)
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

		assert.NotEqual(t, http.StatusNotFound, w.Code)
	})

	t.Run("Request with Query Parameters", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1InventoryAssets+"?limit=10&active=true&sort=name", nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		assert.NotEqual(t, http.StatusNotFound, w.Code)
	})

	t.Run("Authenticated User with Valid Role", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1AuthProfile, nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		// Set user role in context (simulating authenticated user)
		ctx.Set(constants.ContextKeyUserRole, "customer")

		server.handleProxyRequest(ctx)

		assert.NotEqual(t, http.StatusNotFound, w.Code)
	})

	t.Run("Authenticated User without Role", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1Orders, nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		// No role set - simulating request without auth
		// Should return 401 since orders requires auth

		server.handleProxyRequest(ctx)

		assert.Equal(t, constants.StatusUnauthorized, w.Code)
	})
}

func TestBlockedIPReturns403(t *testing.T) {
	mr := miniredis.RunT(t)
	addr := mr.Addr()
	parts := strings.Split(addr, ":")
	require.Len(t, parts, 2, "miniredis addr should be host:port")
	cfg := &config.Config{
		Server: config.ServerConfig{Port: strconv.Itoa(constants.DefaultPort), Host: constants.DefaultHost},
		Services: config.ServicesConfig{
			UserService: constants.DefaultUserServiceURL, InventoryService: constants.DefaultInventoryServiceURL,
			OrderService: constants.DefaultOrderServiceURL, AuthService: constants.DefaultAuthServiceURL, InsightsService: constants.DefaultInsightsServiceURL,
		},
		Redis:     config.RedisConfig{Host: parts[0], Port: parts[1], Password: "", DB: 0, SSL: false},
		RateLimit: config.RateLimitConfig{Limit: 10000, Window: constants.RateLimitWindow},
	}
	redisSvc, err := services.NewRedisService(&cfg.Redis)
	require.NoError(t, err)
	t.Cleanup(func() { _ = redisSvc.Close() })

	testIP := "192.0.2.100"
	ctx := context.Background()
	err = redisSvc.SetIPBlock(ctx, testIP, 60*time.Second)
	assert.NoError(t, err)

	reg := prometheus.NewRegistry()
	server := NewServerWithRegistry(cfg, redisSvc, services.NewProxyService(cfg), reg)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", constants.APIV1Path+constants.AuthLoginPath, strings.NewReader(`{"username":"u","password":"p"}`))
	req.Header.Set("Content-Type", "application/json")
	// Set RemoteAddr so Gin's ClientIP() returns our test IP (IP block check uses it)
	req.RemoteAddr = testIP + ":12345"

	server.router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusForbidden, w.Code, "blocked IP should get 403")
	var resp models.ErrorResponse
	err = json.Unmarshal(w.Body.Bytes(), &resp)
	assert.NoError(t, err)
	assert.Equal(t, string(models.ErrIPBlocked), resp.Error)
}

// TestHandleProxyRequest_BackendReturns5xx ensures gateway handles backend 5xx and records proxy error.
func TestHandleProxyRequest_BackendReturns5xx(t *testing.T) {
	backend := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
		_, _ = w.Write([]byte("internal error"))
	}))
	defer backend.Close()

	cfg := &config.Config{
		Server:   config.ServerConfig{Port: strconv.Itoa(constants.DefaultPort), Host: constants.DefaultHost},
		Services: config.ServicesConfig{
			UserService:      backend.URL,
			InventoryService: constants.DefaultInventoryServiceURL,
			OrderService:     constants.DefaultOrderServiceURL,
			AuthService:       constants.DefaultAuthServiceURL,
			InsightsService:  constants.DefaultInsightsServiceURL,
		},
		RateLimit: config.RateLimitConfig{Limit: 10000, Window: constants.RateLimitWindow},
	}
	reg := prometheus.NewRegistry()
	server := NewServerWithRegistry(cfg, nil, services.NewProxyService(cfg), reg)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", constants.APIV1AuthProfile, nil)
	gin.SetMode(gin.TestMode)
	ctx := gin.CreateTestContextOnly(w, server.router)
	ctx.Request = req
	ctx.Set(constants.ContextKeyUserRole, "customer")

	server.handleProxyRequest(ctx)

	assert.Equal(t, http.StatusInternalServerError, w.Code)
	assert.Contains(t, w.Body.String(), "internal error")
}

// TestHandleProxyRequest_Login401RecordsFailedLogin hits the RecordFailedLogin path when backend returns 401 on POST login.
func TestHandleProxyRequest_Login401RecordsFailedLogin(t *testing.T) {
	backend := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusUnauthorized)
		_, _ = w.Write([]byte(`{"error":"invalid_credentials"}`))
	}))
	defer backend.Close()

	mr := miniredis.RunT(t)
	addr := mr.Addr()
	parts := strings.Split(addr, ":")
	require.Len(t, parts, 2, "miniredis addr")
	cfg := &config.Config{
		Server:   config.ServerConfig{Port: strconv.Itoa(constants.DefaultPort), Host: constants.DefaultHost},
		Services: config.ServicesConfig{
			UserService:      backend.URL, // Auth routes (login) are proxied to UserService
			InventoryService: constants.DefaultInventoryServiceURL,
			OrderService:     constants.DefaultOrderServiceURL,
			AuthService:       constants.DefaultAuthServiceURL,
			InsightsService:  constants.DefaultInsightsServiceURL,
		},
		Redis:     config.RedisConfig{Host: parts[0], Port: parts[1], Password: "", DB: 0, SSL: false},
		RateLimit: config.RateLimitConfig{Limit: 10000, Window: constants.RateLimitWindow},
	}
	redisSvc, err := services.NewRedisService(&cfg.Redis)
	require.NoError(t, err)
	t.Cleanup(func() { _ = redisSvc.Close() })

	reg := prometheus.NewRegistry()
	server := NewServerWithRegistry(cfg, redisSvc, services.NewProxyService(cfg), reg)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", constants.APIV1AuthLogin, strings.NewReader(`{"username":"u","password":"p"}`))
	req.Header.Set("Content-Type", "application/json")
	req.RemoteAddr = "192.0.2.50:12345"
	gin.SetMode(gin.TestMode)
	ctx := gin.CreateTestContextOnly(w, server.router)
	ctx.Request = req

	server.handleProxyRequest(ctx)

	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestHandleProxyRequestErrorScenarios(t *testing.T) {
	server, _ := setupTestServer()

	t.Run("Valid JSON Body", func(t *testing.T) {
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

		// Set user context to pass authentication
		ctx.Set(constants.ContextKeyUserRole, "public")

		server.handleProxyRequest(ctx)

		assert.NotEqual(t, http.StatusNotFound, w.Code)
	})

	t.Run("Empty Body", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", constants.APIV1Path+constants.AuthLoginPath, nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		// Set user context to pass authentication
		ctx.Set(constants.ContextKeyUserRole, "public")

		server.handleProxyRequest(ctx)

		assert.NotEqual(t, http.StatusNotFound, w.Code)
	})

	t.Run("Service Not Found", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1Path+"/unknown/service", nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("Invalid JSON Body", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", constants.APIV1Path+constants.AuthLoginPath, strings.NewReader("invalid json {"))

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		assert.Equal(t, constants.StatusBadRequest, w.Code)

		var response models.ErrorResponse
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Contains(t, response.Message, "Invalid JSON body")
	})

	t.Run("Read Request Body Fails", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", constants.APIV1Path+constants.AuthLoginPath, nil)
		req.Body = io.NopCloser(&errReader{err: errors.New("read failed")})

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req

		server.handleProxyRequest(ctx)

		assert.Equal(t, constants.StatusBadRequest, w.Code)
		var response models.ErrorResponse
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Contains(t, response.Message, constants.ErrorReadRequestBody)
	})

	t.Run("Authenticated user when route has no role restriction", func(t *testing.T) {
		// Current routes use empty AllowedRoles, so any authenticated user is allowed
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1Orders, nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req
		ctx.Set(constants.ContextKeyUserRole, "guest") // Any authenticated user when AllowedRoles is empty

		server.handleProxyRequest(ctx)

		assert.Contains(t, []int{constants.StatusServiceUnavailable, constants.StatusForbidden}, w.Code)
	})

	t.Run("No Authentication with Required Auth Route", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1AuthProfile, nil)

		gin.SetMode(gin.TestMode)
		ctx := gin.CreateTestContextOnly(w, server.router)
		ctx.Request = req
		// No user role set

		server.handleProxyRequest(ctx)

		assert.Equal(t, constants.StatusUnauthorized, w.Code)

		var response models.ErrorResponse
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, string(models.ErrAuthInvalidToken), response.Error)
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

		server.handleError(ctx, constants.StatusBadRequest, models.ErrAuthInvalidToken, "Test error message")

		assert.Equal(t, constants.StatusBadRequest, w.Code)

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

	t.Run("Balance by Asset ID", func(t *testing.T) {
		result := server.getBasePath("/api/v1/assets/BTC/balance")
		assert.Equal(t, "/api/v1/assets/:asset_id/balance", result)
	})

	t.Run("Asset Transactions by ID", func(t *testing.T) {
		result := server.getBasePath("/api/v1/assets/ETH/transactions")
		assert.Equal(t, "/api/v1/assets/:asset_id/transactions", result)
	})

	t.Run("Order by ID", func(t *testing.T) {
		result := server.getBasePath("/api/v1/orders/12345")
		assert.Equal(t, "/api/v1/orders/:id", result)
	})

	t.Run("Inventory Asset by ID", func(t *testing.T) {
		result := server.getBasePath("/api/v1/inventory/assets/67890")
		assert.Equal(t, "/api/v1/inventory/assets/:id", result)
	})

	t.Run("Portfolio by Username", func(t *testing.T) {
		result := server.getBasePath("/api/v1/portfolio/user123")
		assert.Equal(t, "/api/v1/portfolio/:username", result)
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
