package middleware

import (
	"net/http"
	"strings"

	"order-processor-gateway/pkg/constants"

	"github.com/gin-gonic/gin"
)

// AuthMiddleware validates JWT tokens and extracts user information
// TODO: Implement JWT token validation logic
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Extract token from Authorization header
		authHeader := c.GetHeader(constants.AuthorizationHeader)
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": constants.ErrorAuthHeaderRequired,
			})
			c.Abort()
			return
		}

		// Check if token starts with "Bearer "
		tokenParts := strings.Split(authHeader, " ")
		if len(tokenParts) != 2 || tokenParts[0] != constants.AuthSchemeBearer {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": constants.ErrorAuthHeaderInvalid,
			})
			c.Abort()
			return
		}

		_ = tokenParts[1] // token variable - TODO: Validate JWT token

		// TODO: Validate JWT token
		// TODO: Extract user claims from token
		// TODO: Check if token is blacklisted in Redis
		// TODO: Add user information to context

		// Placeholder: Always allow for now
		c.Set(constants.ContextKeyUserID, constants.AuthPlaceholderUserID)
		c.Set(constants.ContextKeyUserRole, constants.AuthDefaultRole)

		c.Next()
	}
}

// RoleMiddleware checks if user has required role
// TODO: Implement role-based access control
func RoleMiddleware(requiredRole string) gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Get user role from context (set by AuthMiddleware)
		// TODO: Check if user has required role
		// TODO: Return 403 Forbidden if role check fails

		// Placeholder: Always allow for now
		c.Next()
	}
}
