package models

import (
	"time"
)

// RequestContext holds context information for incoming requests
// Used for logging, tracing, and security decisions
type RequestContext struct {
	RequestID   string          `json:"request_id"` // UUID v4 for unique identification
	Timestamp   time.Time       `json:"timestamp"`
	ServiceName string          `json:"service_name"`
	Security    SecurityContext `json:"security"`
	Audit       AuditContext    `json:"audit"`
}

// SecurityContext holds security-related information
type SecurityContext struct {
	IsAuthenticated bool   `json:"is_authenticated"`
	SecurityLevel   string `json:"security_level"` // constants.SecurityLevel*
	TokenHash       string `json:"token_hash"`     // Hash of JWT token for validation
	RateLimitKey    string `json:"rate_limit_key"` // Key for rate limiting (IP or IP:UserID)
}

// AuditContext holds audit information for logging and tracing
type AuditContext struct {
	IPHash        string `json:"ip_hash"`         // Hashed IP address for audit
	UserAgentHash string `json:"user_agent_hash"` // Hashed user agent for audit
	RequestHash   string `json:"request_hash"`    // Hash of request signature for integrity
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
	Key        string        `json:"key"`
	Limit      int           `json:"limit"`
	Remaining  int           `json:"remaining"`
	ResetTime  time.Time     `json:"reset_time"`
	WindowSize time.Duration `json:"window_size"`
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
