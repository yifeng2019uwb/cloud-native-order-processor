package middleware

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/models"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

var testConfig *config.Config

func init() {
	testConfig = &config.Config{
		Services: config.ServicesConfig{
			AuthService: "http://localhost:8003",
		},
	}
}

func setupAuthTestRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	return router
}

func TestAuthMiddleware(t *testing.T) {
	router := setupAuthTestRouter()
	router.Use(AuthMiddleware(testConfig))
	router.GET("/test", func(c *gin.Context) {
		userID, userIDExists := c.Get(constants.ContextKeyUserID)
		userRole, userRoleExists := c.Get(constants.ContextKeyUserRole)
		userContext, userContextExists := c.Get(constants.ContextKeyUserContext)

		c.JSON(http.StatusOK, gin.H{
			constants.JSONFieldUsername: userID,
			"user_id_exists":            userIDExists,
			"user_role":                 userRole,
			"user_role_exists":          userRoleExists,
			"user_context":              userContext,
			"user_context_exists":       userContextExists,
		})
	})

	t.Run("No Auth Header", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)

		// No auth header - no user context set at all
		assert.Equal(t, false, response["user_id_exists"])
		assert.Equal(t, false, response["user_role_exists"])
		assert.Equal(t, false, response["user_context_exists"])
	})

	t.Run("Invalid Auth Header Format", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, "InvalidFormat token123")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("Empty Bearer Token", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" ")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("Valid Bearer Token Format", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" valid.token.here")
		router.ServeHTTP(w, req)

		// Should return 401 for invalid token format
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("Multiple Auth Headers", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" token1")
		req.Header.Add(constants.AuthorizationHeader, constants.AuthSchemeBearer+" token2")
		router.ServeHTTP(w, req)

		// Should handle multiple headers gracefully
		assert.NotEqual(t, http.StatusInternalServerError, w.Code)
	})

	t.Run("Auth Header with Special Characters", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" token.with.dots_and-dashes")
		router.ServeHTTP(w, req)

		// Should handle special characters in token
		assert.NotEqual(t, http.StatusInternalServerError, w.Code)
	})

	t.Run("Auth Header with Spaces", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" token with spaces")
		router.ServeHTTP(w, req)

		// Should handle spaces in token
		assert.NotEqual(t, http.StatusInternalServerError, w.Code)
	})

	t.Run("Auth Header with Empty Token", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer)
		router.ServeHTTP(w, req)

		// Should return 401 for empty token
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("Auth Header with Only Bearer", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, "Bearer")
		router.ServeHTTP(w, req)

		// Should return 401 for only "Bearer" without token
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("Auth Header with Tab Separator", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+"\ttoken")
		router.ServeHTTP(w, req)

		// Should handle tab separator
		assert.NotEqual(t, http.StatusInternalServerError, w.Code)
	})

	t.Run("Auth Header with Newline Separator", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+"\ntoken")
		router.ServeHTTP(w, req)

		// Should handle newline separator
		assert.NotEqual(t, http.StatusInternalServerError, w.Code)
	})
}

func TestRoleMiddleware(t *testing.T) {
	router := setupAuthTestRouter()
	router.Use(func(c *gin.Context) {
		c.Set(constants.ContextKeyUserRole, "customer")
		c.Next()
	})
	router.Use(RoleMiddleware([]string{"customer", "admin"}))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	t.Run("User with Valid Role", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("User with Invalid Role", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(func(c *gin.Context) {
			c.Set(constants.ContextKeyUserRole, "guest")
			c.Next()
		})
		router.Use(RoleMiddleware([]string{"customer", "admin"}))
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)

		var response models.ErrorResponse
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "PERM_001", response.Error)
		assert.Contains(t, response.Message, "Insufficient permissions")
		assert.Contains(t, response.Message, "guest")
	})

	t.Run("User with Admin Role", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(func(c *gin.Context) {
			c.Set(constants.ContextKeyUserRole, "admin")
			c.Next()
		})
		router.Use(RoleMiddleware([]string{"customer", "admin"}))
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("User with VIP Role", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(func(c *gin.Context) {
			c.Set(constants.ContextKeyUserRole, "vip")
			c.Next()
		})
		router.Use(RoleMiddleware([]string{"customer", "admin", "vip"}))
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("User with Public Role", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(func(c *gin.Context) {
			c.Set(constants.ContextKeyUserRole, "public")
			c.Next()
		})
		router.Use(RoleMiddleware([]string{"customer", "admin"}))
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("User with Empty Role", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(func(c *gin.Context) {
			c.Set(constants.ContextKeyUserRole, "")
			c.Next()
		})
		router.Use(RoleMiddleware([]string{"customer", "admin"}))
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("User with No Role Set", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(RoleMiddleware([]string{"customer", "admin"}))
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("Empty Allowed Roles", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(func(c *gin.Context) {
			c.Set(constants.ContextKeyUserRole, "customer")
			c.Next()
		})
		router.Use(RoleMiddleware([]string{}))
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		// Should allow access when no roles are specified
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("Nil Allowed Roles", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(func(c *gin.Context) {
			c.Set(constants.ContextKeyUserRole, "customer")
			c.Next()
		})
		router.Use(RoleMiddleware(nil))
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		// Should allow access when roles is nil
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("Case Sensitive Role Matching", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(func(c *gin.Context) {
			c.Set(constants.ContextKeyUserRole, "Customer") // Capital C
			c.Next()
		})
		router.Use(RoleMiddleware([]string{"customer", "admin"})) // Lowercase c
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		// Should be case sensitive and deny access
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("Role with Special Characters", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(func(c *gin.Context) {
			c.Set(constants.ContextKeyUserRole, "user-123")
			c.Next()
		})
		router.Use(RoleMiddleware([]string{"user-123", "admin"}))
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		// Should allow access for role with special characters
		assert.Equal(t, http.StatusOK, w.Code)
	})
}

func TestHandleAuthError(t *testing.T) {
	router := setupAuthTestRouter()

	router.GET("/error", func(c *gin.Context) {
		handleAuthError(c, models.ErrAuthInvalidToken, "Test error message")
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/error", nil)
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusUnauthorized, w.Code)

	var response models.ErrorResponse
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.Equal(t, "AUTH_001", response.Error)
	assert.Equal(t, "Test error message", response.Message)
}
