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

// AuthMiddleware validates JWT tokens using the Auth Service and extracts user information.
// If redisService is non-nil, checks client IP against Redis blocked_ips set first (SEC-011); blocked IPs get 403.
func AuthMiddleware(cfg *config.Config, redisService *services.RedisService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// SEC-011: IP block check (before token validation). Skip if Redis not available.
		if redisService != nil {
			clientIP := c.ClientIP()
			blocked, err := redisService.IsIPBlocked(c.Request.Context(), clientIP)
			if err != nil {
				// Redis error: fail open (allow request) to avoid blocking all traffic
				logger.Info(logging.REQUEST_START, "IP block check failed, allowing request", "", map[string]interface{}{
					"client_ip": clientIP,
					"error":     err.Error(),
				})
			} else if blocked {
				handleIPBlocked(c, clientIP)
				return
			}
		}

		// Extract token from Authorization header
		authHeader := c.GetHeader(constants.AuthorizationHeader)

		if authHeader == "" {
			// No auth header - don't set any role, let the route handler decide
			// Protected routes will check for empty role and return 401
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
		c.Set(constants.ContextKeyUserID, userContext.Username)
		c.Set(constants.ContextKeyUserRole, userContext.Role)
		c.Set(constants.ContextKeyUserContext, userContext)

		c.Next()
	}
}

// Note: JWT validation is now handled by the Auth Service
// This function has been replaced by AuthServiceClient.ValidateToken()

// RoleMiddleware checks if user is authenticated (requiredRoles empty = any authenticated user allowed)
func RoleMiddleware(requiredRoles []string) gin.HandlerFunc {
	return func(c *gin.Context) {
		logger.Info(logging.REQUEST_START, "RoleMiddleware processing request", "", map[string]interface{}{
			constants.JSONFieldPath:          c.Request.URL.Path,
			constants.JSONFieldRequiredRoles: requiredRoles,
		})

		userRole := c.GetString(constants.ContextKeyUserRole)
		logger.Info(logging.REQUEST_START, "User role extracted", "", map[string]interface{}{
			constants.JSONFieldUserRole: userRole,
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
				constants.JSONFieldRequiredRoles: requiredRoles,
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
				constants.JSONFieldUserRole:      userRole,
				constants.JSONFieldRequiredRoles: requiredRoles,
			})
			handleAuthError(c, models.ErrPermInsufficient, fmt.Sprintf("Insufficient permissions. Required roles: %v, User role: %s", requiredRoles, userRole))
			return
		}

		logger.Info(logging.REQUEST_END, "User role found in required roles, allowing access", "", map[string]interface{}{
			constants.JSONFieldUserRole: userRole,
		})
		c.Next()
	}
}

// handleAuthError handles authentication and authorization errors (401)
func handleAuthError(c *gin.Context, errorCode models.ErrorCode, message string) {
	logger.Error(logging.AUTH_FAILURE, "Authentication/authorization error", "", map[string]interface{}{
		"error_code":               string(errorCode),
		constants.JSONFieldMessage: message,
		constants.JSONFieldPath:    c.Request.URL.Path,
		constants.JSONFieldMethod:  c.Request.Method,
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

// handleIPBlocked responds with 403 Forbidden for blocked IPs (SEC-011)
func handleIPBlocked(c *gin.Context, clientIP string) {
	logger.Error(logging.AUTH_FAILURE, "Request from blocked IP", "", map[string]interface{}{
		"client_ip": clientIP,
		constants.JSONFieldPath:    c.Request.URL.Path,
		constants.JSONFieldMethod:  c.Request.Method,
	})

	errorResponse := models.ErrorResponse{
		Error:     string(models.ErrIPBlocked),
		Message:   constants.ErrorIPBlocked,
		Code:      string(models.ErrIPBlocked),
		Timestamp: time.Now(),
	}

	c.JSON(http.StatusForbidden, errorResponse)
	c.Abort()
}
