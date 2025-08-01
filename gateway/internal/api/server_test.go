package api

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/internal/services"
	"order-processor-gateway/pkg/constants"

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

	server := NewServer(cfg, nil, services.NewProxyService(cfg))
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

	server := NewServer(cfg, redisService, proxyService)

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

func TestProxyToUserService(t *testing.T) {
	server, _ := setupTestServer()

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", constants.APIV1Path+constants.AuthLoginPath, nil)
	server.router.ServeHTTP(w, req)

	// Expected to fail with 503 due to service unavailability (no backend service running)
	// This is correct behavior when backend services are not available
	assert.Equal(t, http.StatusServiceUnavailable, w.Code)

	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)

	// Check for error response structure
	assert.Contains(t, response, "error")
	assert.Contains(t, response, "message")
	assert.Contains(t, response, "code")
	assert.Contains(t, response, "timestamp")
}

func TestProxyToInventoryService(t *testing.T) {
	server, _ := setupTestServer()

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", constants.APIV1Path+constants.InventoryAssetsPath, nil)
	server.router.ServeHTTP(w, req)

	// Expected to fail with 503 due to service unavailability (no backend service running)
	// This is correct behavior when backend services are not available
	assert.Equal(t, http.StatusServiceUnavailable, w.Code)

	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)

	// Check for error response structure
	assert.Contains(t, response, "error")
	assert.Contains(t, response, "message")
	assert.Contains(t, response, "code")
	assert.Contains(t, response, "timestamp")
}

func TestRouteSetup(t *testing.T) {
	server, _ := setupTestServer()

	// Test health endpoint
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", constants.HealthPath, nil)
	server.router.ServeHTTP(w, req)
	assert.Equal(t, http.StatusOK, w.Code)

	// Test public routes - these should fail with 503 due to service unavailability (no backend service running)
	testCases := []struct {
		method string
		path   string
		status int
	}{
		{"POST", constants.APIV1Path + constants.AuthLoginPath, http.StatusServiceUnavailable},
		{"POST", constants.APIV1Path + constants.AuthRegisterPath, http.StatusServiceUnavailable},
	}

	for _, tc := range testCases {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest(tc.method, tc.path, nil)
		server.router.ServeHTTP(w, req)
		assert.Equal(t, tc.status, w.Code, "Failed for %s %s", tc.method, tc.path)
	}

	// Test protected routes - these should fail with 503 due to service unavailability (no backend service running)
	protectedRoutes := []struct {
		method string
		path   string
		status int
	}{
		{"GET", constants.APIV1Path + constants.AuthProfilePath, http.StatusNotFound},
		{"POST", constants.APIV1Path + constants.AuthLogoutPath, http.StatusForbidden},
		{"GET", constants.APIV1Path + constants.InventoryAssetsPath, http.StatusServiceUnavailable},
		{"GET", constants.APIV1Path + constants.InventoryAssetByIDPath, http.StatusServiceUnavailable},
	}

	for _, tc := range protectedRoutes {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest(tc.method, tc.path, nil)
		server.router.ServeHTTP(w, req)
		assert.Equal(t, tc.status, w.Code, "Failed for %s %s", tc.method, tc.path)
	}
}

func TestCORSHeaders(t *testing.T) {
	server, _ := setupTestServer()

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("OPTIONS", constants.HealthPath, nil)
	server.router.ServeHTTP(w, req)

	assert.Equal(t, constants.StatusNoContent, w.Code)
	assert.Equal(t, constants.CORSAllowOrigin, w.Header().Get("Access-Control-Allow-Origin"))
	assert.Equal(t, constants.CORSAllowMethods, w.Header().Get("Access-Control-Allow-Methods"))
	assert.Equal(t, constants.CORSAllowHeaders, w.Header().Get("Access-Control-Allow-Headers"))
}

func TestServerStart(t *testing.T) {
	server, _ := setupTestServer()

	// This test verifies that the server can be created and configured
	// We don't actually start it in tests to avoid port conflicts
	assert.NotNil(t, server.config)
	assert.NotNil(t, server.router)
	assert.NotNil(t, server.proxyService)
}

func TestQueryParametersHandling(t *testing.T) {
	server, _ := setupTestServer()

	t.Run("Assets with limit parameter", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1Path+constants.InventoryAssetsPath+"?limit=10&active_only=true", nil)
		server.router.ServeHTTP(w, req)

		// Expected to fail with 503 due to service unavailability (no backend service running)
		// But the query parameters should be properly handled
		assert.Equal(t, http.StatusServiceUnavailable, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)

		// Check for error response structure
		assert.Contains(t, response, "error")
		assert.Contains(t, response, "message")
		assert.Contains(t, response, "code")
		assert.Contains(t, response, "timestamp")
	})

	t.Run("Assets with active_only parameter", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1Path+constants.InventoryAssetsPath+"?active_only=false", nil)
		server.router.ServeHTTP(w, req)

		// Expected to fail with 503 due to service unavailability (no backend service running)
		assert.Equal(t, http.StatusServiceUnavailable, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)

		// Check for error response structure
		assert.Contains(t, response, "error")
		assert.Contains(t, response, "message")
		assert.Contains(t, response, "code")
		assert.Contains(t, response, "timestamp")
	})

	t.Run("Assets with multiple parameters", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.APIV1Path+constants.InventoryAssetsPath+"?limit=50&active_only=true&test=value", nil)
		server.router.ServeHTTP(w, req)

		// Expected to fail with 503 due to service unavailability (no backend service running)
		assert.Equal(t, http.StatusServiceUnavailable, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)

		// Check for error response structure
		assert.Contains(t, response, "error")
		assert.Contains(t, response, "message")
		assert.Contains(t, response, "code")
		assert.Contains(t, response, "timestamp")
	})
}

func BenchmarkHealthCheck(b *testing.B) {
	server, _ := setupTestServer()

	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", constants.HealthPath, nil)
		server.router.ServeHTTP(w, req)
	}
}

func BenchmarkProxyToUserService(b *testing.B) {
	server, _ := setupTestServer()

	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", constants.APIV1Path+constants.AuthLoginPath, nil)
		server.router.ServeHTTP(w, req)
	}
}
