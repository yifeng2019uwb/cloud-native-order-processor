package middleware

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/pkg/constants"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt"
	"github.com/stretchr/testify/assert"
)

// Test JWT configuration
var testJWTConfig = &config.Config{
	JWT: config.JWTConfig{
		SecretKey: "test-secret-key-for-testing-only",
		Algorithm: "HS256",
	},
}

// generateTestJWT creates a valid JWT token for testing
func generateTestJWT(username, role string, expiresIn time.Duration) (string, error) {
	claims := JWTClaims{
		Username: username,
		Role:     role,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: time.Now().Add(expiresIn).Unix(),
			IssuedAt:  time.Now().Unix(),
			Issuer:    "test-gateway",
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(testJWTConfig.JWT.SecretKey))
}

// generateExpiredJWT creates an expired JWT token for testing
func generateExpiredJWT(username, role string) (string, error) {
	claims := JWTClaims{
		Username: username,
		Role:     role,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: time.Now().Add(-1 * time.Hour).Unix(), // Expired 1 hour ago
			IssuedAt:  time.Now().Add(-2 * time.Hour).Unix(),
			Issuer:    "test-gateway",
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(testJWTConfig.JWT.SecretKey))
}

func setupAuthTestRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	router.Use(gin.Recovery())
	return router
}

func TestAuthMiddleware(t *testing.T) {
	router := setupAuthTestRouter()
	router.Use(AuthMiddleware(testJWTConfig))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	t.Run("Missing Authorization Header - Public User", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		// Should allow access as public user
		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "success", response["message"])
	})

	t.Run("Invalid Authorization Format", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, "invalid-format")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "AUTH_001", response["error"])
		assert.Contains(t, response["message"], "Invalid authorization header format")
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
		assert.Equal(t, "AUTH_001", response["error"])
		assert.Contains(t, response["message"], "Invalid authorization header format")
	})

	t.Run("Valid Bearer Token", func(t *testing.T) {
		token, err := generateTestJWT("testuser", "customer", time.Hour)
		assert.NoError(t, err)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" "+token)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "success", response["message"])
	})

	t.Run("Expired Bearer Token", func(t *testing.T) {
		token, err := generateExpiredJWT("testuser", "customer")
		assert.NoError(t, err)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" "+token)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)

		var response map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "AUTH_001", response["error"])
		assert.Contains(t, response["message"], "Token validation failed")
	})

	t.Run("Invalid JWT Token", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" invalid.jwt.token")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "AUTH_001", response["error"])
		assert.Contains(t, response["message"], "Token validation failed")
	})

	t.Run("Bearer Token with Extra Spaces", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, "  "+constants.AuthSchemeBearer+"  token123  ")
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "AUTH_001", response["error"])
		assert.Contains(t, response["message"], "Invalid authorization header format")
	})
}

func TestRoleMiddleware(t *testing.T) {
	router := setupAuthTestRouter()
	router.Use(AuthMiddleware(testJWTConfig))
	router.Use(RoleMiddleware([]string{"admin"}))
	router.GET("/admin", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "admin access"})
	})

	t.Run("Role Check with Valid Admin Token", func(t *testing.T) {
		token, err := generateTestJWT("adminuser", "admin", time.Hour)
		assert.NoError(t, err)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/admin", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" "+token)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "admin access", response["message"])
	})

	t.Run("Role Check with Non-Admin Token", func(t *testing.T) {
		token, err := generateTestJWT("customeruser", "customer", time.Hour)
		assert.NoError(t, err)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/admin", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" "+token)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)

		var response map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "PERM_001", response["error"])
		assert.Contains(t, response["message"], "Insufficient permissions")
	})

	t.Run("Role Check without Token - Public User", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/admin", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "PERM_001", response["error"])
		assert.Contains(t, response["message"], "Insufficient permissions")
	})
}

func TestAuthMiddlewareContextValues(t *testing.T) {
	router := setupAuthTestRouter()
	router.Use(AuthMiddleware(testJWTConfig))
	router.GET("/context", func(c *gin.Context) {
		userID, exists := c.Get(constants.ContextKeyUserID)
		userRole, roleExists := c.Get(constants.ContextKeyUserRole)
		userContext, contextExists := c.Get("user_context")

		c.JSON(http.StatusOK, gin.H{
			"user_id":        userID,
			"user_role":      userRole,
			"exists":         exists,
			"role_exists":    roleExists,
			"context_exists": contextExists,
			"user_context":   userContext,
		})
	})

	t.Run("With Valid Token", func(t *testing.T) {
		token, err := generateTestJWT("testuser", "customer", time.Hour)
		assert.NoError(t, err)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/context", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" "+token)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)

		// Verify context values are set correctly
		assert.Equal(t, "testuser", response["user_id"])
		assert.Equal(t, "customer", response["user_role"])
		assert.Equal(t, true, response["exists"])
		assert.Equal(t, true, response["role_exists"])
		assert.Equal(t, true, response["context_exists"])

		// Verify user context object
		userContext, ok := response["user_context"].(map[string]interface{})
		assert.True(t, ok)
		assert.Equal(t, "testuser", userContext["username"])
		assert.Equal(t, "customer", userContext["role"])
		assert.Equal(t, true, userContext["is_authenticated"])
	})

	t.Run("Without Token - Public User", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/context", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)

		// Verify public user context values
		assert.Equal(t, nil, response["user_id"])          // user_id is not set for public users
		assert.Equal(t, "public", response["user_role"])   // Public users get RolePublic
		assert.Equal(t, false, response["exists"])         // user_id context is not set for public users
		assert.Equal(t, true, response["role_exists"])     // Role is set for public users
		assert.Equal(t, false, response["context_exists"]) // No user context object
	})
}

func TestRoleMiddlewareEdgeCases(t *testing.T) {
	t.Run("Role Middleware with Different Roles", func(t *testing.T) {
		roles := []string{"admin", "customer", "vip"}

		for _, role := range roles {
			t.Run("Role: "+role, func(t *testing.T) {
				router := setupAuthTestRouter()
				router.Use(AuthMiddleware(testJWTConfig))
				router.Use(RoleMiddleware([]string{role}))
				router.GET("/test", func(c *gin.Context) {
					c.JSON(http.StatusOK, gin.H{"message": "success"})
				})

				token, err := generateTestJWT("testuser", role, time.Hour)
				assert.NoError(t, err)

				w := httptest.NewRecorder()
				req, _ := http.NewRequest("GET", "/test", nil)
				req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" "+token)
				router.ServeHTTP(w, req)

				assert.Equal(t, http.StatusOK, w.Code)
			})
		}
	})

	t.Run("Role Middleware without Auth Middleware", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(RoleMiddleware([]string{"admin"}))
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		router.ServeHTTP(w, req)

		// Should fail because no auth middleware to set user role
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestAuthMiddlewareIntegration(t *testing.T) {
	t.Run("Auth with CORS", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(CORS())
		router.Use(AuthMiddleware(testJWTConfig))
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		token, err := generateTestJWT("testuser", "customer", time.Hour)
		assert.NoError(t, err)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" "+token)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
		assert.Equal(t, constants.CORSAllowOrigin, w.Header().Get("Access-Control-Allow-Origin"))
	})

	t.Run("Auth with Logger", func(t *testing.T) {
		router := setupAuthTestRouter()
		router.Use(Logger())
		router.Use(AuthMiddleware(testJWTConfig))
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		token, err := generateTestJWT("testuser", "customer", time.Hour)
		assert.NoError(t, err)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" "+token)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})
}

func TestJWTTokenGeneration(t *testing.T) {
	t.Run("Generate Valid Token", func(t *testing.T) {
		token, err := generateTestJWT("testuser", "customer", time.Hour)
		assert.NoError(t, err)
		assert.NotEmpty(t, token)

		// Verify token can be parsed
		parsedToken, err := jwt.ParseWithClaims(token, &JWTClaims{}, func(token *jwt.Token) (interface{}, error) {
			return []byte(testJWTConfig.JWT.SecretKey), nil
		})
		assert.NoError(t, err)
		assert.True(t, parsedToken.Valid)

		claims, ok := parsedToken.Claims.(*JWTClaims)
		assert.True(t, ok)
		assert.Equal(t, "testuser", claims.Username)
		assert.Equal(t, "customer", claims.Role)
	})

	t.Run("Generate Expired Token", func(t *testing.T) {
		token, err := generateExpiredJWT("testuser", "customer")
		assert.NoError(t, err)
		assert.NotEmpty(t, token)

		// Verify token is expired
		parsedToken, err := jwt.ParseWithClaims(token, &JWTClaims{}, func(token *jwt.Token) (interface{}, error) {
			return []byte(testJWTConfig.JWT.SecretKey), nil
		})
		// Should get an error for expired token
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "token is expired")
		assert.False(t, parsedToken.Valid)
	})
}

func BenchmarkAuthMiddleware(b *testing.B) {
	router := setupAuthTestRouter()
	router.Use(AuthMiddleware(testJWTConfig))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	token, err := generateTestJWT("testuser", "customer", time.Hour)
	if err != nil {
		b.Fatalf("Failed to generate test token: %v", err)
	}

	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" "+token)
		router.ServeHTTP(w, req)
	}
}

func BenchmarkRoleMiddleware(b *testing.B) {
	router := setupAuthTestRouter()
	router.Use(AuthMiddleware(testJWTConfig))
	router.Use(RoleMiddleware([]string{"admin"}))
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	token, err := generateTestJWT("adminuser", "admin", time.Hour)
	if err != nil {
		b.Fatalf("Failed to generate test token: %v", err)
	}

	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set(constants.AuthorizationHeader, constants.AuthSchemeBearer+" "+token)
		router.ServeHTTP(w, req)
	}
}
