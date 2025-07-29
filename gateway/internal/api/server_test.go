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

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Equal(t, constants.ProxyUserServiceNotImplemented, response["message"])
	assert.Equal(t, constants.ServiceNameUser, response["service"])
	assert.Equal(t, constants.APIV1Path+constants.AuthLoginPath, response["path"])
}

func TestProxyToInventoryService(t *testing.T) {
	server, _ := setupTestServer()

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", constants.APIV1Path+constants.InventoryAssetsPath, nil)
	server.router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Equal(t, constants.ProxyInventoryServiceNotImplemented, response["message"])
	assert.Equal(t, constants.ServiceNameInventory, response["service"])
	assert.Equal(t, constants.APIV1Path+constants.InventoryAssetsPath, response["path"])
}

func TestRouteSetup(t *testing.T) {
	server, _ := setupTestServer()

	// Test health endpoint
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", constants.HealthPath, nil)
	server.router.ServeHTTP(w, req)
	assert.Equal(t, http.StatusOK, w.Code)

	// Test public routes
	testCases := []struct {
		method string
		path   string
		status int
	}{
		{"POST", constants.APIV1Path + constants.AuthLoginPath, http.StatusOK},
		{"POST", constants.APIV1Path + constants.AuthRegisterPath, http.StatusOK},
	}

	for _, tc := range testCases {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest(tc.method, tc.path, nil)
		server.router.ServeHTTP(w, req)
		assert.Equal(t, tc.status, w.Code, "Failed for %s %s", tc.method, tc.path)
	}

	// Test protected routes (should work without auth for now)
	protectedRoutes := []struct {
		method string
		path   string
		status int
	}{
		{"GET", constants.APIV1Path + constants.AuthProfilePath, http.StatusOK},
		{"POST", constants.APIV1Path + constants.AuthLogoutPath, http.StatusOK},
		{"GET", constants.APIV1Path + constants.InventoryAssetsPath, http.StatusOK},
		{"GET", constants.APIV1Path + constants.InventoryAssetByIDPath, http.StatusOK},
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
