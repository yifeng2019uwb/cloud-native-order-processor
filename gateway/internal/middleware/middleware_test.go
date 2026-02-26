package middleware

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strconv"
	"strings"
	"testing"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/internal/services"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/metrics"

	"github.com/alicebob/miniredis/v2"
	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func setupTestRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	return router
}

func TestCORS(t *testing.T) {
	router := setupTestRouter()
	router.Use(CORS())
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{constants.JSONFieldMessage: "cors test"})
	})

	t.Run("CORS Headers", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
		assert.Equal(t, constants.CORSAllowOrigin, w.Header().Get("Access-Control-Allow-Origin"))
		assert.Equal(t, constants.CORSAllowMethods, w.Header().Get("Access-Control-Allow-Methods"))
		assert.Equal(t, constants.CORSAllowHeaders, w.Header().Get("Access-Control-Allow-Headers"))
	})

	t.Run("OPTIONS Request", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest(constants.HTTPMethodOptions, "/test", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, constants.StatusNoContent, w.Code)
		assert.Equal(t, constants.CORSAllowOrigin, w.Header().Get("Access-Control-Allow-Origin"))
	})
}

func TestLogger(t *testing.T) {
	router := setupTestRouter()
	router.Use(Logger())
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{constants.JSONFieldMessage: "logger test"})
	})

	t.Run("Logger Middleware", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set("User-Agent", "test-agent")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})
}

func TestRecovery(t *testing.T) {
	router := setupTestRouter()
	router.Use(Recovery())
	router.GET("/panic", func(c *gin.Context) {
		panic("test panic")
	})
	router.GET("/normal", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{constants.JSONFieldMessage: "normal"})
	})

	t.Run("Recovery from Panic", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/panic", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusInternalServerError, w.Code)
	})

	t.Run("Normal Request After Panic", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/normal", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})
}

func TestMetricsHTTP(t *testing.T) {
	reg := prometheus.NewRegistry()
	gm := metrics.NewGatewayMetricsWithRegistry(reg)
	router := setupTestRouter()
	router.Use(MetricsHTTP(gm))
	router.GET(constants.HealthPath, func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{constants.JSONFieldStatus: constants.StatusHealthy})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodGet, constants.HealthPath, nil)
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	// MetricsHTTP runs c.Next() then RecordRequest; no way to assert metrics without reading registry
	_, err := reg.Gather()
	assert.NoError(t, err)
}

// newRedisServiceWithMiniredis returns a RedisService backed by miniredis (no real Redis).
func newRedisServiceWithMiniredis(t *testing.T) *services.RedisService {
	t.Helper()
	mr := miniredis.RunT(t)
	addr := mr.Addr()
	parts := strings.Split(addr, ":")
	require.Len(t, parts, 2, "miniredis addr")
	cfg := &config.RedisConfig{Host: parts[0], Port: parts[1], Password: "", DB: 0, SSL: false}
	svc, err := services.NewRedisService(cfg)
	require.NoError(t, err)
	t.Cleanup(func() { _ = svc.Close() })
	return svc
}

func TestRateLimitMiddleware(t *testing.T) {
	limit := constants.FailedLoginBlockThreshold + 5
	window := constants.RateLimitWindow

	t.Run("Middleware can be created", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		rateLimitMetrics := metrics.NewRateLimitMetricsWithRegistry(reg)
		var redisService *services.RedisService = nil
		mw := RateLimitMiddleware(redisService, limit, window, rateLimitMetrics)
		assert.NotNil(t, mw)
	})

	t.Run("With miniredis - request allowed and headers set", func(t *testing.T) {
		redisSvc := newRedisServiceWithMiniredis(t)
		router := setupTestRouter()
		router.Use(RateLimitMiddleware(redisSvc, limit, window, nil))
		router.GET(constants.HealthPath, func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{constants.JSONFieldStatus: constants.StatusHealthy})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest(http.MethodGet, constants.HealthPath, nil)
		req.RemoteAddr = "192.0.2.1:12345"
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
		assert.Equal(t, strconv.Itoa(limit), w.Header().Get(constants.RateLimitHeaderLimit))
		assert.NotEmpty(t, w.Header().Get(constants.RateLimitHeaderRemaining))
		assert.NotEmpty(t, w.Header().Get(constants.RateLimitHeaderReset))
	})

	t.Run("With miniredis - rate exceeded returns 429", func(t *testing.T) {
		redisSvc := newRedisServiceWithMiniredis(t)
		smallLimit := 2
		router := setupTestRouter()
		router.Use(RateLimitMiddleware(redisSvc, smallLimit, window, nil))
		router.GET(constants.APIV1Path+"/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{})
		})

		path := constants.APIV1Path + "/test"
		for i := 0; i < smallLimit; i++ {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest(http.MethodGet, path, nil)
			req.RemoteAddr = "192.0.2.2:12345"
			router.ServeHTTP(w, req)
			assert.Equal(t, http.StatusOK, w.Code, "request %d should be allowed", i+1)
		}

		w := httptest.NewRecorder()
		req, _ := http.NewRequest(http.MethodGet, path, nil)
		req.RemoteAddr = "192.0.2.2:12345"
		router.ServeHTTP(w, req)
		assert.Equal(t, http.StatusTooManyRequests, w.Code)
		var body map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &body)
		require.NoError(t, err)
		assert.Equal(t, constants.ErrorRateLimitExceeded, body[constants.JSONFieldError])
	})
}

// Test constants for session middleware
const (
	testSessionIDValue = "test-session-123"
	testPath           = "/test"
)

func TestSessionMiddleware(t *testing.T) {
	t.Run("No session header - passes through", func(t *testing.T) {
		redisSvc := newRedisServiceWithMiniredis(t)
		router := setupTestRouter()
		router.Use(SessionMiddleware(redisSvc))
		router.GET(testPath, func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{constants.JSONFieldMessage: "test"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest(http.MethodGet, testPath, nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("With miniredis - valid session sets context", func(t *testing.T) {
		redisSvc := newRedisServiceWithMiniredis(t)
		sessionData := map[string]interface{}{"user_id": "u1", "email": "u1@example.com"}
		err := redisSvc.StoreSession(context.Background(), testSessionIDValue, sessionData, time.Minute)
		require.NoError(t, err)

		router := setupTestRouter()
		router.Use(SessionMiddleware(redisSvc))
		var gotSession interface{}
		router.GET(testPath, func(c *gin.Context) {
			gotSession, _ = c.Get(constants.ContextKeySession)
			c.JSON(http.StatusOK, gin.H{constants.JSONFieldMessage: "ok"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest(http.MethodGet, testPath, nil)
		req.Header.Set(constants.XSessionIDHeader, testSessionIDValue)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
		require.NotNil(t, gotSession)
		sess, ok := gotSession.(map[string]interface{})
		require.True(t, ok)
		assert.Equal(t, "u1", sess["user_id"])
	})

	t.Run("With miniredis - invalid session returns 401", func(t *testing.T) {
		redisSvc := newRedisServiceWithMiniredis(t)
		router := setupTestRouter()
		router.Use(SessionMiddleware(redisSvc))
		router.GET(testPath, func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest(http.MethodGet, testPath, nil)
		req.Header.Set(constants.XSessionIDHeader, "nonexistent-session-id")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)
		var body map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &body)
		require.NoError(t, err)
		assert.Equal(t, constants.ErrorSessionInvalid, body[constants.JSONFieldError])
	})

	t.Run("Middleware can be created", func(t *testing.T) {
		redisService := &services.RedisService{}
		middleware := SessionMiddleware(redisService)
		assert.NotNil(t, middleware)
	})
}
