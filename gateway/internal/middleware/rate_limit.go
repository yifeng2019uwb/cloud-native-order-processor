package middleware

import (
	"net/http"
	"time"

	"order-processor-gateway/internal/services"

	"github.com/gin-gonic/gin"
)

// RateLimitMiddleware creates rate limiting middleware using Redis
func RateLimitMiddleware(redisService *services.RedisService, limit int, window time.Duration) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Create rate limit key based on IP or user ID
		key := "rate_limit:" + c.ClientIP()

		// Check rate limit
		allowed, err := redisService.CheckRateLimit(c.Request.Context(), key, limit, window)
		if err != nil {
			// If Redis is down, allow request (fail open)
			c.Next()
			return
		}

		if !allowed {
			c.JSON(http.StatusTooManyRequests, gin.H{
				"error":       "Rate limit exceeded",
				"retry_after": window.Seconds(),
			})
			c.Abort()
			return
		}

		c.Next()
	}
}

// SessionMiddleware validates user sessions using Redis
func SessionMiddleware(redisService *services.RedisService) gin.HandlerFunc {
	return func(c *gin.Context) {
		sessionID := c.GetHeader("X-Session-ID")
		if sessionID == "" {
			// No session required for public endpoints
			c.Next()
			return
		}

		// Get session from Redis
		session, err := redisService.GetSession(c.Request.Context(), sessionID)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Invalid or expired session",
			})
			c.Abort()
			return
		}

		// Add session data to context
		c.Set("session", session)
		c.Next()
	}
}
