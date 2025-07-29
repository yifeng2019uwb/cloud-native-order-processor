package middleware

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"net/http"
	"strings"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/models"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt"
)

// JWTClaims represents the claims in a JWT token
type JWTClaims struct {
	Username string `json:"sub"`
	Role     string `json:"role"`
	jwt.StandardClaims
}

// AuthMiddleware validates JWT tokens and extracts user information
// Phase 1: Simple JWT validation with basic error handling
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

		// Validate JWT token
		userContext, err := validateJWT(tokenString, cfg)
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

// validateJWT validates a JWT token and returns user context
// Phase 1: Simple JWT validation
// Phase 2: Add Redis blacklist check
func validateJWT(tokenString string, cfg *config.Config) (*models.UserContext, error) {
	// Parse and validate token
	token, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (interface{}, error) {
		// Validate signing method
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(cfg.JWT.SecretKey), nil
	})

	if err != nil {
		return nil, fmt.Errorf("failed to parse token: %w", err)
	}

	// Extract claims
	claims, ok := token.Claims.(*JWTClaims)
	if !ok || !token.Valid {
		return nil, fmt.Errorf("invalid token claims")
	}

	// Check if token is expired
	if claims.ExpiresAt < time.Now().Unix() {
		return nil, fmt.Errorf("token expired")
	}

	// Phase 2: Check Redis blacklist
	// if isTokenBlacklisted(tokenString) {
	//     return nil, fmt.Errorf("token is blacklisted")
	// }

	// Create user context
	userContext := &models.UserContext{
		Username:        claims.Username,
		Role:            claims.Role,
		IsAuthenticated: true,
	}

	// Set default role if not present
	if userContext.Role == "" {
		userContext.Role = constants.DefaultUserRole
	}

	return userContext, nil
}

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

// hashToken creates a hash of the token for logging/audit purposes
// Phase 1: Simple SHA256 hash for security
func hashToken(token string) string {
	hash := sha256.Sum256([]byte(token))
	return hex.EncodeToString(hash[:])
}

// Phase 2: Redis blacklist check (TODO)
// func isTokenBlacklisted(tokenHash string) bool {
//     // Check Redis for blacklisted token
//     // Return true if token is blacklisted
//     return false
// }

// Phase 3: Advanced features (Future - simple comments)
// - OAuth2 integration
// - API key authentication
// - Multi-factor authentication
// - Advanced role hierarchies
// - Permission-based access control
