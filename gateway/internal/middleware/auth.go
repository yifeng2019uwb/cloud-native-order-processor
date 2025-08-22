package middleware

import (
	"fmt"
	"net/http"
	"strings"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/internal/services"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/models"

	"github.com/gin-gonic/gin"
)

// AuthMiddleware validates JWT tokens using the Auth Service and extracts user information
// Phase 2: Auth Service integration for centralized JWT validation
func AuthMiddleware(cfg *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		fmt.Printf("🔍 STEP 1: AuthMiddleware START - Path: %s, Method: %s\n", c.Request.URL.Path, c.Request.Method)

		// Extract token from Authorization header
		authHeader := c.GetHeader(constants.AuthorizationHeader)
		fmt.Printf("🔍 STEP 1.1: AuthMiddleware - authHeader: '%s'\n", authHeader)

		if authHeader == "" {
			// No auth header - set public role for unauthenticated users
			fmt.Printf("🔍 STEP 1.2: AuthMiddleware - No auth header, setting RolePublic\n")
			c.Set(constants.ContextKeyUserRole, constants.RolePublic)
			fmt.Printf("🔍 STEP 1.3: AuthMiddleware - RolePublic set, calling c.Next()\n")
			c.Next()
			fmt.Printf("🔍 STEP 1.4: AuthMiddleware END\n")
			return
		}

		// Check if token starts with "Bearer "
		tokenParts := strings.Split(authHeader, " ")
		if len(tokenParts) != 2 || tokenParts[0] != constants.AuthSchemeBearer {
			handleAuthError(c, models.ErrAuthInvalidToken, "Invalid authorization header format")
			return
		}

		tokenString := tokenParts[1]

		// Validate JWT token using Auth Service
		authClient := services.NewAuthServiceClient(cfg)
		userContext, err := authClient.ValidateToken(c.Request.Context(), tokenString)
		if err != nil {
			handleAuthError(c, models.ErrAuthInvalidToken, fmt.Sprintf("Token validation failed: %v", err))
			return
		}

		// Add user information to context
		fmt.Printf("🔍 STEP 1.5: AuthMiddleware - Setting user context: username=%s, role=%s\n", userContext.Username, userContext.Role)
		c.Set(constants.ContextKeyUserID, userContext.Username)
		c.Set(constants.ContextKeyUserRole, userContext.Role)
		c.Set("user_context", userContext)

		fmt.Printf("🔍 STEP 1.6: AuthMiddleware - User context set, calling c.Next()\n")
		c.Next()
		fmt.Printf("🔍 STEP 1.7: AuthMiddleware END\n")
	}
}

// Note: JWT validation is now handled by the Auth Service
// This function has been replaced by AuthServiceClient.ValidateToken()

// RoleMiddleware checks if user has required role
// Phase 1: Simple role-based access control
func RoleMiddleware(requiredRoles []string) gin.HandlerFunc {
	return func(c *gin.Context) {
		fmt.Printf("DEBUG: RoleMiddleware called for path: %s\n", c.Request.URL.Path)
		userRole := c.GetString(constants.ContextKeyUserRole)
		fmt.Printf("DEBUG: RoleMiddleware - userRole: '%s', requiredRoles: %v\n", userRole, requiredRoles)

		// If no role restrictions, allow access
		if len(requiredRoles) == 0 {
			fmt.Printf("DEBUG: RoleMiddleware - No role restrictions, allowing access\n")
			c.Next()
			return
		}

		// If user has no role but roles are required, deny access
		if userRole == "" {
			fmt.Printf("DEBUG: RoleMiddleware - User has no role but roles are required, denying access\n")
			handleAuthError(c, models.ErrPermInsufficient, fmt.Sprintf("Insufficient permissions. Required roles: %v, User role: none", requiredRoles))
			return
		}

		// Check if user has required role
		hasRole := false
		for _, role := range requiredRoles {
			if role == userRole {
				hasRole = true
				break
			}
		}

		if !hasRole {
			fmt.Printf("DEBUG: RoleMiddleware - User role '%s' not found in required roles, denying access\n", userRole)
			handleAuthError(c, models.ErrPermInsufficient, fmt.Sprintf("Insufficient permissions. Required roles: %v, User role: %s", requiredRoles, userRole))
			return
		}

		fmt.Printf("DEBUG: RoleMiddleware - User role '%s' found in required roles, allowing access\n", userRole)
		c.Next()
	}
}

// handleAuthError handles authentication and authorization errors
func handleAuthError(c *gin.Context, errorCode models.ErrorCode, message string) {
	errorResponse := models.ErrorResponse{
		Error:     string(errorCode),
		Message:   message,
		Code:      string(errorCode),
		Timestamp: time.Now(),
	}

	c.JSON(http.StatusUnauthorized, errorResponse)
	c.Abort()
}

// Note: Token hashing and blacklist functionality moved to Auth Service
// Phase 2: Redis blacklist check (TODO - implement in Auth Service)
// Phase 3: Advanced features (Future - implement in Auth Service)
// - OAuth2 integration
// - API key authentication
// - Multi-factor authentication
// - Advanced role hierarchies
// - Permission-based access control
