package models

import (
	"time"
)

// APIResponse represents a standardized API response
// Used for all API responses including success, error, and proxy responses
type APIResponse struct {
	Success   bool        `json:"success"`
	Data      interface{} `json:"data,omitempty"`
	Error     string      `json:"error,omitempty"`
	Message   string      `json:"message,omitempty"`
	Timestamp time.Time   `json:"timestamp"`
	RequestID string      `json:"request_id,omitempty"`
}

// ErrorInfo represents detailed error information
type ErrorInfo struct {
	Code    string `json:"code"`              // Error code (e.g., "VALIDATION_ERROR", "AUTH_ERROR")
	Message string `json:"message"`           // Human-readable error message
	Details string `json:"details,omitempty"` // Additional error details
}
