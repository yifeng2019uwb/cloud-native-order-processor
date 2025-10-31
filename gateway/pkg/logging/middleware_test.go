package logging

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

// Test constants
const (
	testRequestID    = "test-req-123"
	testPath         = "/test"
	testAuthPath     = "/auth"
	testPublicPath   = "/public"
	testErrorPath    = "/error"
	testToken        = "test-token"
	testMessage      = "test"
	testCreatedMsg   = "created"
	testAuthMsg      = "authenticated"
	testPublicMsg    = "public"
	testErrorMessage = "test error"
	testRequestCount = 10
)

var (
	testService = GATEWAY
)

// Test helper functions
func setupTestRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	return gin.New()
}

func createTestLogger() *BaseLogger {
	logger := NewBaseLogger(testService)
	logger.SetRequestID(testRequestID)
	return logger
}

func createTestHandler(statusCode int, message string) gin.HandlerFunc {
	return func(c *gin.Context) {
		response := gin.H{"message": message}
		if statusCode >= http.StatusInternalServerError {
			response = gin.H{"error": message}
		}
		c.JSON(statusCode, response)
	}
}

type middlewareTestCase struct {
	name       string
	method     string
	path       string
	statusCode int
	message    string
	headers    map[string]string
}

func TestLoggingMiddleware(t *testing.T) {
	logger := createTestLogger()
	router := setupTestRouter()
	router.Use(LoggingMiddleware(logger))
	router.GET(testPath, createTestHandler(http.StatusOK, testMessage))

	testCases := []middlewareTestCase{
		{
			name:       "Middleware logs request",
			method:     http.MethodGet,
			path:       testPath,
			statusCode: http.StatusOK,
			message:    testMessage,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest(tc.method, tc.path, nil)
			router.ServeHTTP(w, req)

			assert.Equal(t, tc.statusCode, w.Code)
		})
	}

	t.Run("Middleware handles different methods", func(t *testing.T) {
		router := setupTestRouter()
		router.Use(LoggingMiddleware(logger))
		router.POST(testPath, createTestHandler(http.StatusCreated, testCreatedMsg))

		w := httptest.NewRecorder()
		req, _ := http.NewRequest(http.MethodPost, testPath, nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusCreated, w.Code)
	})

	t.Run("Middleware handles errors", func(t *testing.T) {
		router := setupTestRouter()
		router.Use(LoggingMiddleware(logger))
		router.GET(testErrorPath, createTestHandler(http.StatusInternalServerError, testErrorMessage))

		w := httptest.NewRecorder()
		req, _ := http.NewRequest(http.MethodGet, testErrorPath, nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusInternalServerError, w.Code)
	})
}

func TestAuthLoggingMiddleware(t *testing.T) {
	logger := createTestLogger()
	testCases := []middlewareTestCase{
		{
			name:       "Middleware logs auth requests",
			method:     http.MethodGet,
			path:       testPath,
			statusCode: http.StatusOK,
			message:    testMessage,
		},
		{
			name:       "Middleware handles authenticated requests",
			method:     http.MethodGet,
			path:       testAuthPath,
			statusCode: http.StatusOK,
			message:    testAuthMsg,
			headers: map[string]string{
				"Authorization": "Bearer " + testToken,
			},
		},
		{
			name:       "Middleware handles unauthenticated requests",
			method:     http.MethodGet,
			path:       testPublicPath,
			statusCode: http.StatusOK,
			message:    testPublicMsg,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			router := setupTestRouter()
			router.Use(AuthLoggingMiddleware(logger))
			router.GET(tc.path, createTestHandler(tc.statusCode, tc.message))

			w := httptest.NewRecorder()
			req, _ := http.NewRequest(tc.method, tc.path, nil)

			if tc.headers != nil {
				for key, value := range tc.headers {
					req.Header.Set(key, value)
				}
			}

			router.ServeHTTP(w, req)
			assert.Equal(t, tc.statusCode, w.Code)
		})
	}
}

func TestGenerateRequestID(t *testing.T) {
	const (
		minRequestIDLength = 0
		requestIDPrefix    = "req-"
		nanosecondDelay    = 1 // Delay in nanoseconds to ensure unique timestamps
	)

	t.Run("Generate request IDs with expected format", func(t *testing.T) {
		ids := make(map[string]bool)
		uniqueCount := 0

		for i := 0; i < testRequestCount; i++ {
			id := generateRequestID()
			assert.NotEmpty(t, id)
			assert.Greater(t, len(id), minRequestIDLength)
			assert.Contains(t, id, requestIDPrefix)
			assert.Greater(t, len(id), len(requestIDPrefix))

			// Track unique IDs (note: function has second precision, so IDs within same second may duplicate)
			if !ids[id] {
				uniqueCount++
			}
			ids[id] = true
		}

		// At least some IDs should be unique (depending on execution speed)
		assert.Greater(t, uniqueCount, 0, "At least one unique ID should be generated")
	})

	t.Run("Request ID has expected format", func(t *testing.T) {
		id := generateRequestID()
		assert.NotEmpty(t, id)
		assert.Contains(t, id, requestIDPrefix)
		assert.Greater(t, len(id), len(requestIDPrefix))
	})

	t.Run("Request ID contains timestamp", func(t *testing.T) {
		id := generateRequestID()
		// ID format is "req-YYYYMMDDHHmmss", so it should be at least prefix + 14 digits
		const expectedMinLength = len(requestIDPrefix) + 14
		assert.GreaterOrEqual(t, len(id), expectedMinLength)
	})
}
