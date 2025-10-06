package middleware

import (
	"net/http"
	"strconv"
	"time"

	"order-processor-gateway/internal/services"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/metrics"

	"github.com/gin-gonic/gin"
)

// RateLimitMiddleware creates rate limiting middleware using Redis with metrics
func RateLimitMiddleware(redisService *services.RedisService, limit int, window time.Duration, metrics *metrics.RateLimitMetrics) gin.HandlerFunc {
	return func(c *gin.Context) {
		clientIP := c.ClientIP()
		endpoint := c.FullPath()
		method := c.Request.Method

		// Create rate limit key based on IP
		key := constants.RedisKeyPrefixRateLimit + clientIP

		// Check rate limit
		allowed, remaining, resetTime, err := redisService.CheckRateLimitWithDetails(c.Request.Context(), key, limit, window)
		if err != nil {
			// If Redis is down, allow request (fail open)
			if metrics != nil {
				metrics.RecordRequest(method, endpoint, "500", clientIP)
			}
			c.Next()
			return
		}

		// Add rate limit headers to response
		c.Header(constants.RateLimitHeaderLimit, strconv.Itoa(limit))
		c.Header(constants.RateLimitHeaderRemaining, strconv.FormatInt(remaining, 10))
		c.Header(constants.RateLimitHeaderReset, strconv.FormatInt(resetTime, 10))

		if !allowed {
			// Record rate limit violation
			if metrics != nil {
				metrics.RecordRateLimitViolation(clientIP, endpoint)
				metrics.UpdateRateLimitRemaining(clientIP, endpoint, remaining)
				metrics.UpdateRateLimitReset(clientIP, endpoint, resetTime)
			}

			c.JSON(http.StatusTooManyRequests, gin.H{
				constants.JSONFieldError:      constants.ErrorRateLimitExceeded,
				constants.JSONFieldRetryAfter: window.Seconds(),
				constants.JSONFieldLimit:      limit,
				constants.JSONFieldRemaining:  remaining,
				constants.JSONFieldResetTime:  resetTime,
			})
			c.Abort()
			return
		}

		// Update metrics for allowed request
		if metrics != nil {
			metrics.UpdateRateLimitRemaining(clientIP, endpoint, remaining)
			metrics.UpdateRateLimitReset(clientIP, endpoint, resetTime)
		}

		c.Next()
	}
}

// SessionMiddleware validates user sessions using Redis
func SessionMiddleware(redisService *services.RedisService) gin.HandlerFunc {
	return func(c *gin.Context) {
		sessionID := c.GetHeader(constants.XSessionIDHeader)
		if sessionID == "" {
			// No session required for public endpoints
			c.Next()
			return
		}

		// Get session from Redis
		session, err := redisService.GetSession(c.Request.Context(), sessionID)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{
				constants.JSONFieldError: constants.ErrorSessionInvalid,
			})
			c.Abort()
			return
		}

		// Add session data to context
		c.Set(constants.ContextKeySession, session)
		c.Next()
	}
}
