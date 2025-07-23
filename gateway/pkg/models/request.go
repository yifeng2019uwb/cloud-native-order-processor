package models

import (
	"time"
)

// RequestContext holds context information for incoming requests
type RequestContext struct {
	RequestID   string            `json:"request_id"`
	UserID      string            `json:"user_id,omitempty"`
	UserRole    string            `json:"user_role,omitempty"`
	IPAddress   string            `json:"ip_address"`
	UserAgent   string            `json:"user_agent"`
	Timestamp   time.Time         `json:"timestamp"`
	Headers     map[string]string `json:"headers"`
	ServiceName string            `json:"service_name"`
}

// ProxyRequest represents a request to be proxied to backend services
type ProxyRequest struct {
	Method      string            `json:"method"`
	Path        string            `json:"path"`
	Headers     map[string]string `json:"headers"`
	Body        interface{}       `json:"body,omitempty"`
	QueryParams map[string]string `json:"query_params,omitempty"`
	Context     *RequestContext   `json:"context"`
}

// RateLimitInfo holds rate limiting information
type RateLimitInfo struct {
	Key        string    `json:"key"`
	Limit      int       `json:"limit"`
	Remaining  int       `json:"remaining"`
	ResetTime  time.Time `json:"reset_time"`
	WindowSize int       `json:"window_size"`
}

// SessionInfo holds user session information
type SessionInfo struct {
	SessionID  string                 `json:"session_id"`
	UserID     string                 `json:"user_id"`
	UserRole   string                 `json:"user_role"`
	ExpiresAt  time.Time              `json:"expires_at"`
	Data       map[string]interface{} `json:"data"`
	LastAccess time.Time              `json:"last_access"`
}
