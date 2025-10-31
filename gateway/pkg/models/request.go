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

	// Phase 1: Simple user context
	User *UserContext `json:"user,omitempty"`
}

// UserContext holds user information extracted from JWT
// Phase 1: Simple user context with basic role system
type UserContext struct {
	Username        string `json:"username"`
	Role            string `json:"role"` // "public", "customer", "vip", "admin"
	IsAuthenticated bool   `json:"is_authenticated"`
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
// Phase 1: Simple proxy request structure
type ProxyRequest struct {
	// Core request information
	Method      string            `json:"method"`
	Path        string            `json:"path"` // e.g., "/api/v1/auth/login"
	Headers     map[string]string `json:"headers"`
	Body        interface{}       `json:"body,omitempty"`
	QueryParams map[string]string `json:"query_params,omitempty"`

	// Simple routing information
	TargetService string `json:"target_service"` // "user_service", "inventory_service", or "order_service"
	TargetPath    string `json:"target_path"`    // "/login" (stripped version)

	// Request context
	Context *RequestContext `json:"context"`

	// Phase 2: Circuit breaker information
	// CircuitBreaker *CircuitBreakerInfo `json:"circuit_breaker,omitempty"`
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

// ErrorResponse represents standardized error responses
// Phase 1: Simple error response structure
type ErrorResponse struct {
	Error     string            `json:"error"`
	Message   string            `json:"message"`
	Code      string            `json:"code"`
	Timestamp time.Time         `json:"timestamp"`
	Details   map[string]string `json:"details,omitempty"`
}

// ErrorCode represents different types of errors
type ErrorCode string

const (
	// Authentication Errors
	ErrAuthInvalidToken ErrorCode = "AUTH_001"
	ErrAuthExpiredToken ErrorCode = "AUTH_002"
	ErrAuthBlacklisted  ErrorCode = "AUTH_003"

	// Authorization Errors
	ErrPermInsufficient ErrorCode = "PERM_001"
	ErrPermForbidden    ErrorCode = "PERM_002"

	// Service Errors
	ErrSvcUnavailable ErrorCode = "SVC_001"
	ErrSvcTimeout     ErrorCode = "SVC_002"
	ErrSvcCircuitOpen ErrorCode = "SVC_003"

	// Rate Limiting
	ErrRateLimitExceeded ErrorCode = "RATE_001"
)

// RouteConfig defines routing configuration for API endpoints
// Phase 1: Simple route configuration
type RouteConfig struct {
	Path         string   `json:"path"`
	RequiresAuth bool     `json:"requires_auth"`
	AllowedRoles []string `json:"allowed_roles"`
}
