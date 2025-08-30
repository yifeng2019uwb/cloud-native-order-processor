package middleware

import (
	"fmt"
	"net/http"
	"strings"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/internal/services"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/logging"
	"order-processor-gateway/pkg/models"

	"github.com/gin-gonic/gin"
)

// Package-level logger instance
var logger = logging.NewBaseLogger(logging.GATEWAY)

// AuthMiddleware validates JWT tokens using the Auth Service and extracts user information
// Phase 2: Auth Service integration for centralized JWT validation
func AuthMiddleware(cfg *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		logger.Info(logging.REQUEST_START, "AuthMiddleware processing request", "", map[string]interface{}{
			"path":   c.Request.URL.Path,
			"method": c.Request.Method,
		})

		// Extract token from Authorization header
		authHeader := c.GetHeader(constants.AuthorizationHeader)
		logger.Info(logging.REQUEST_START, "Auth header extracted", "", map[string]interface{}{
			"auth_header": authHeader,
		})

		if authHeader == "" {
			// No auth header - set public role for unauthenticated users
			logger.Info(logging.REQUEST_END, "No auth header, setting public role", "", nil)
			c.Set(constants.ContextKeyUserRole, constants.RolePublic)
			c.Next()
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
		logger.Info(logging.REQUEST_END, "User context set successfully", userContext.Username, map[string]interface{}{
			"username": userContext.Username,
			"role":     userContext.Role,
		})

		c.Set(constants.ContextKeyUserID, userContext.Username)
		c.Set(constants.ContextKeyUserRole, userContext.Role)
		c.Set("user_context", userContext)

		c.Next()
	}
}

// Note: JWT validation is now handled by the Auth Service
// This function has been replaced by AuthServiceClient.ValidateToken()

// RoleMiddleware checks if user has required role
// Phase 1: Simple role-based access control
func RoleMiddleware(requiredRoles []string) gin.HandlerFunc {
	return func(c *gin.Context) {
		logger.Info(logging.REQUEST_START, "RoleMiddleware processing request", "", map[string]interface{}{
			"path":           c.Request.URL.Path,
			"required_roles": requiredRoles,
		})

		userRole := c.GetString(constants.ContextKeyUserRole)
		logger.Info(logging.REQUEST_START, "User role extracted", "", map[string]interface{}{
			"user_role": userRole,
		})

		// If no role restrictions, allow access
		if len(requiredRoles) == 0 {
			logger.Info(logging.REQUEST_END, "No role restrictions, allowing access", "", nil)
			c.Next()
			return
		}

		// If user has no role but roles are required, deny access
		if userRole == "" {
			logger.Error(logging.AUTH_FAILURE, "User has no role but roles are required", "", map[string]interface{}{
				"required_roles": requiredRoles,
			})
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
			logger.Error(logging.AUTH_FAILURE, "User role not found in required roles", "", map[string]interface{}{
				"user_role":      userRole,
				"required_roles": requiredRoles,
			})
			handleAuthError(c, models.ErrPermInsufficient, fmt.Sprintf("Insufficient permissions. Required roles: %v, User role: %s", requiredRoles, userRole))
			return
		}

		logger.Info(logging.REQUEST_END, "User role found in required roles, allowing access", "", map[string]interface{}{
			"user_role": userRole,
		})
		c.Next()
	}
}

// handleAuthError handles authentication and authorization errors
func handleAuthError(c *gin.Context, errorCode models.ErrorCode, message string) {
	logger.Error(logging.AUTH_FAILURE, "Authentication/authorization error", "", map[string]interface{}{
		"error_code": string(errorCode),
		"message":    message,
		"path":       c.Request.URL.Path,
		"method":     c.Request.Method,
	})

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
