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
		c.JSON(http.StatusOK, gin.H{"message": "test"})
	})

	t.Run("CORS Headers Set", func(t *testing.T) {
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
		req, _ := http.NewRequest("OPTIONS", "/test", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, constants.StatusNoContent, w.Code)
		assert.Equal(t, constants.CORSAllowOrigin, w.Header().Get("Access-Control-Allow-Origin"))
		assert.Equal(t, constants.CORSAllowMethods, w.Header().Get("Access-Control-Allow-Methods"))
		assert.Equal(t, constants.CORSAllowHeaders, w.Header().Get("Access-Control-Allow-Headers"))
	})

	t.Run("Different HTTP Method", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/test", nil)
		router.ServeHTTP(w, req)

		// Should return 404 since POST route doesn't exist, but CORS headers should still be set
		assert.Equal(t, http.StatusNotFound, w.Code)
		assert.Equal(t, constants.CORSAllowOrigin, w.Header().Get("Access-Control-Allow-Origin"))
		assert.Equal(t, constants.CORSAllowMethods, w.Header().Get("Access-Control-Allow-Methods"))
		assert.Equal(t, constants.CORSAllowHeaders, w.Header().Get("Access-Control-Allow-Headers"))
	})

	t.Run("Multiple CORS Requests", func(t *testing.T) {
		methods := []string{"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"}

		for _, method := range methods {
			t.Run("Method: "+method, func(t *testing.T) {
				w := httptest.NewRecorder()
				req, _ := http.NewRequest(method, "/test", nil)
				router.ServeHTTP(w, req)

				// CORS headers should be set regardless of method
				assert.Equal(t, constants.CORSAllowOrigin, w.Header().Get("Access-Control-Allow-Origin"))
				assert.Equal(t, constants.CORSAllowMethods, w.Header().Get("Access-Control-Allow-Methods"))
				assert.Equal(t, constants.CORSAllowHeaders, w.Header().Get("Access-Control-Allow-Headers"))
			})
		}
	})

	t.Run("CORS with Custom Headers", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("OPTIONS", "/test", nil)
		req.Header.Set("Access-Control-Request-Headers", "Content-Type, Authorization")
		router.ServeHTTP(w, req)

		assert.Equal(t, constants.StatusNoContent, w.Code)
		assert.Equal(t, constants.CORSAllowOrigin, w.Header().Get("Access-Control-Allow-Origin"))
		assert.Equal(t, constants.CORSAllowMethods, w.Header().Get("Access-Control-Allow-Methods"))
		assert.Equal(t, constants.CORSAllowHeaders, w.Header().Get("Access-Control-Allow-Headers"))
	})
}

func TestLogger(t *testing.T) {
	router := setupTestRouter()
	router.Use(Logger())
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "test"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/test", nil)
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	// Logger middleware should not affect the response
	assert.Equal(t, `{"message":"test"}`, w.Body.String())
}

func TestRecovery(t *testing.T) {
	router := setupTestRouter()
	router.Use(Recovery())
	router.GET("/panic", func(c *gin.Context) {
		panic("test panic")
	})
	router.GET("/normal", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "normal"})
	})

	t.Run("Normal Request", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/normal", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
		assert.Equal(t, `{"message":"normal"}`, w.Body.String())
	})

	t.Run("Panic Recovery", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/panic", nil)
		router.ServeHTTP(w, req)

		// Recovery should handle the panic and return 500
		assert.Equal(t, http.StatusInternalServerError, w.Code)
	})
}

func BenchmarkCORS(b *testing.B) {
	router := setupTestRouter()
	router.Use(CORS())
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "test"})
	})

	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)
	}
}

func BenchmarkLogger(b *testing.B) {
	router := setupTestRouter()
	router.Use(Logger())
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "test"})
	})

	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)
	}
}

func BenchmarkRecovery(b *testing.B) {
	router := setupTestRouter()
	router.Use(Recovery())
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "test"})
	})

	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)
	}
}
