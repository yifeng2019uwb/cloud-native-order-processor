package utils

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// APIResponse represents a standardized API response
type APIResponse struct {
	Success   bool        `json:"success"`
	Data      interface{} `json:"data,omitempty"`
	Error     string      `json:"error,omitempty"`
	Message   string      `json:"message,omitempty"`
	Timestamp time.Time   `json:"timestamp"`
	RequestID string      `json:"request_id,omitempty"`
}

// SuccessResponse sends a successful response
func SuccessResponse(c *gin.Context, data interface{}, message string) {
	response := APIResponse{
		Success:   true,
		Data:      data,
		Message:   message,
		Timestamp: time.Now(),
		RequestID: c.GetString("request_id"),
	}
	c.JSON(http.StatusOK, response)
}

// ErrorResponse sends an error response
func ErrorResponse(c *gin.Context, statusCode int, error string, message string) {
	response := APIResponse{
		Success:   false,
		Error:     error,
		Message:   message,
		Timestamp: time.Now(),
		RequestID: c.GetString("request_id"),
	}
	c.JSON(statusCode, response)
}

// ProxyResponse forwards a response from backend service
// TODO: Implement response transformation and caching
func ProxyResponse(c *gin.Context, statusCode int, data interface{}) {
	// TODO: Transform response if needed
	// TODO: Cache response if appropriate
	// TODO: Add gateway-specific headers
	// TODO: Handle different content types

	c.JSON(statusCode, data)
}

// HealthResponse sends a health check response
func HealthResponse(c *gin.Context, serviceName string, status string) {
	response := map[string]interface{}{
		"status":      status,
		"service":     serviceName,
		"timestamp":   time.Now(),
		"version":     "1.0.0",       // TODO: Get from build info
		"environment": "development", // TODO: Get from config
	}
	c.JSON(http.StatusOK, response)
}
