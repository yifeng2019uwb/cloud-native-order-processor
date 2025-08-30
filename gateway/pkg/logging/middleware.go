package logging

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// LoggingMiddleware creates a logging middleware for Gin
func LoggingMiddleware(logger *BaseLogger) gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()

		// Generate request ID if not present
		requestID := c.GetHeader("X-Request-ID")
		if requestID == "" {
			requestID = generateRequestID()
			c.Header("X-Request-ID", requestID)
		}

		// Set request ID in logger
		logger.SetRequestID(requestID)

		// Log request start
		logger.Info(REQUEST_START, "Incoming request", "", map[string]interface{}{
			"method":     c.Request.Method,
			"path":       c.Request.URL.Path,
			"ip":         c.ClientIP(),
			"user_agent": c.Request.UserAgent(),
		})

		// Process request
		c.Next()

		// Calculate duration
		duration := time.Since(start)

		// Log request end
		logger.Info(REQUEST_END, "Request completed", "", map[string]interface{}{
			"method":      c.Request.Method,
			"path":        c.Request.URL.Path,
			"status":      c.Writer.Status(),
			"duration_ms": duration.Milliseconds(),
		})
	}
}

// AuthLoggingMiddleware logs authentication events
func AuthLoggingMiddleware(logger *BaseLogger) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Log auth start
		logger.Info(REQUEST_START, "Authentication check", "", map[string]interface{}{
			"method": c.Request.Method,
			"path":   c.Request.URL.Path,
		})

		c.Next()

		// Check if auth failed
		if c.Writer.Status() == http.StatusUnauthorized {
			logger.Error(AUTH_FAILURE, "Authentication failed", "", map[string]interface{}{
				"method": c.Request.Method,
				"path":   c.Request.URL.Path,
				"ip":     c.ClientIP(),
			})
		}
	}
}

// generateRequestID generates a simple request ID
func generateRequestID() string {
	return "req-" + time.Now().Format("20060102150405")
}
