package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"order-processor-gateway/pkg/constants"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
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
