package middleware

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"order-processor-gateway/pkg/constants"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func setupAuthTestRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	return router
}

func TestAuthMiddleware(t *testing.T) {
	router := setupAuthTestRouter()
	router.Use(AuthMiddleware())
	router.GET("/test", func(c *gin.Context) {
		userID, exists := c.Get(constants.ContextKeyUserID)
		userRole, roleExists := c.Get(constants.ContextKeyUserRole)

		c.JSON(http.StatusOK, gin.H{
			"user_id":     userID,
			"user_role":   userRole,
			"exists":      exists,
			"role_exists": roleExists,
		})
	})

	t.Run("Missing Authorization Header", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, constants.ErrorAuthHeaderRequired, response["error"])
	})

	t.Run("Invalid Authorization Format", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, "InvalidFormat")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, constants.ErrorAuthHeaderInvalid, response["error"])
	})

	t.Run("Invalid Auth Scheme", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, "Basic token123")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, constants.ErrorAuthHeaderInvalid, response["error"])
	})

	t.Run("Valid Bearer Token", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" token123")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, constants.AuthPlaceholderUserID, response["user_id"])
		assert.Equal(t, constants.AuthDefaultRole, response["user_role"])
		assert.Equal(t, true, response["exists"])
		assert.Equal(t, true, response["role_exists"])
	})

	t.Run("Bearer Token with Space", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+"  token123  ")
		router.ServeHTTP(w, req)

		// Should fail because of extra spaces in token format
		assert.Equal(t, http.StatusUnauthorized, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, constants.ErrorAuthHeaderInvalid, response["error"])
	})
}

func TestRoleMiddleware(t *testing.T) {
	router := setupAuthTestRouter()
	router.Use(AuthMiddleware())
	router.Use(RoleMiddleware("admin"))
	router.GET("/admin", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "admin access"})
	})

	t.Run("Role Check with Valid Token", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/admin", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" token123")
		router.ServeHTTP(w, req)

		// Currently always allows (placeholder implementation)
		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "admin access", response["message"])
	})

	t.Run("Role Check without Token", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/admin", nil)
		router.ServeHTTP(w, req)

		// Should fail at auth middleware level
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestAuthMiddlewareContextValues(t *testing.T) {
	router := setupAuthTestRouter()
	router.Use(AuthMiddleware())
	router.GET("/context", func(c *gin.Context) {
		userID, exists := c.Get(constants.ContextKeyUserID)
		userRole, roleExists := c.Get(constants.ContextKeyUserRole)

		c.JSON(http.StatusOK, gin.H{
			"user_id":     userID,
			"user_role":   userRole,
			"exists":      exists,
			"role_exists": roleExists,
		})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/context", nil)
	req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" test-token")
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)

	// Verify context values are set correctly
	assert.Equal(t, constants.AuthPlaceholderUserID, response["user_id"])
	assert.Equal(t, constants.AuthDefaultRole, response["user_role"])
	assert.Equal(t, true, response["exists"])
	assert.Equal(t, true, response["role_exists"])
}

func BenchmarkAuthMiddleware(t *testing.B) {
	router := setupAuthTestRouter()
	router.Use(AuthMiddleware())
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	for i := 0; i < t.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" benchmark-token")
		router.ServeHTTP(w, req)
	}
}

func BenchmarkRoleMiddleware(t *testing.B) {
	router := setupAuthTestRouter()
	router.Use(AuthMiddleware())
	router.Use(RoleMiddleware("admin"))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	for i := 0; i < t.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" benchmark-token")
		router.ServeHTTP(w, req)
	}
}

func TestAuthMiddlewareEdgeCases(t *testing.T) {
	router := setupAuthTestRouter()
	router.Use(AuthMiddleware())
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	t.Run("Empty Bearer Token", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" ")
		router.ServeHTTP(w, req)

		// Current implementation allows empty tokens (placeholder)
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("Very Long Token", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		longToken := "very_long_token_" + string(make([]byte, 1000))
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" "+longToken)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("Special Characters in Token", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		specialToken := "token!@#$%^&*()_+-=[]{}|;':\",./<>?"
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" "+specialToken)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("Multiple Authorization Headers", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" token1")
		req.Header.Add(constants.AuthorizationHeader, constants.AuthSchemeBearer+" token2")
		router.ServeHTTP(w, req)

		// Should use the first header
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("Case Insensitive Authorization Header", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set("authorization", constants.AuthSchemeBearer+" token123")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("Bearer Token with Extra Spaces", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, "  "+constants.AuthSchemeBearer+"  token123  ")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestRoleMiddlewareEdgeCases(t *testing.T) {
	t.Run("Role Middleware with Different Roles", func(t *testing.T) {
		roles := []string{"admin", "user", "guest", "super_admin", ""}

		for _, role := range roles {
			t.Run("Role: "+role, func(t *testing.T) {
				router := setupAuthTestRouter()
				router.Use(AuthMiddleware())
				router.Use(RoleMiddleware(role))
				router.GET("/test", func(c *gin.Context) {
					c.JSON(http.StatusOK, gin.H{"message": "success"})
				})

				w := httptest.NewRecorder()
				req, _ := http.NewRequest("GET", "/test", nil)
				req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" token123")
				router.ServeHTTP(w, req)

				// Currently always allows (placeholder implementation)
				assert.Equal(t, http.StatusOK, w.Code)
			})
		}
	})

	t.Run("Role Middleware without Auth Middleware", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(RoleMiddleware("admin"))
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		// Current implementation allows access (placeholder)
		assert.Equal(t, http.StatusOK, w.Code)
	})
}

func TestAuthMiddlewareIntegration(t *testing.T) {
	t.Run("Auth with CORS", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(CORS())
		router.Use(AuthMiddleware())
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" token123")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
		assert.Equal(t, constants.CORSAllowOrigin, w.Header().Get("Access-Control-Allow-Origin"))
	})

	t.Run("Auth with Logger", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(Logger())
		router.Use(AuthMiddleware())
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" token123")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})
}
