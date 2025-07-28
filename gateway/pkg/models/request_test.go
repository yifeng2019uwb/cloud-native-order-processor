package models

import (
	"testing"
	"time"
)

func TestRequestContextCreation(t *testing.T) {
	// Create a RequestContext
	ctx := &RequestContext{
		RequestID:   "test-request-id-123",
		Timestamp:   time.Now(),
		ServiceName: "gateway",
		Security: SecurityContext{
			IsAuthenticated: true,
			SecurityLevel:   "authenticated",
			TokenHash:       "abc123",
			RateLimitKey:    "192.168.1.100:user123",
		},
		Audit: AuditContext{
			IPHash:        "hash123",
			UserAgentHash: "hash456",
			RequestHash:   "hash789",
		},
	}

	// Test basic fields
	if ctx.RequestID == "" {
		t.Error("RequestID should not be empty")
	}
	if ctx.ServiceName != "gateway" {
		t.Errorf("ServiceName should be 'gateway', got %s", ctx.ServiceName)
	}
	if !ctx.Security.IsAuthenticated {
		t.Error("IsAuthenticated should be true")
	}
	if ctx.Security.SecurityLevel != "authenticated" {
		t.Errorf("SecurityLevel should be 'authenticated', got %s", ctx.Security.SecurityLevel)
	}
}

func TestProxyRequestCreation(t *testing.T) {
	// Create a RequestContext
	ctx := &RequestContext{
		RequestID:   "test-request-id-456",
		Timestamp:   time.Now(),
		ServiceName: "gateway",
		Security: SecurityContext{
			IsAuthenticated: true,
			SecurityLevel:   "authenticated",
		},
		Audit: AuditContext{},
	}

	// Create a ProxyRequest
	proxyReq := &ProxyRequest{
		Method:      "POST",
		Path:        "/api/users",
		Headers:     map[string]string{"Content-Type": "application/json"},
		Body:        `{"name": "test"}`,
		QueryParams: map[string]string{"page": "1"},
		Context:     ctx,
	}

	// Test basic fields
	if proxyReq.Method != "POST" {
		t.Errorf("Method should be 'POST', got %s", proxyReq.Method)
	}
	if proxyReq.Path != "/api/users" {
		t.Errorf("Path should be '/api/users', got %s", proxyReq.Path)
	}
	if proxyReq.Context == nil {
		t.Error("Context should not be nil")
	}
	if proxyReq.Context.RequestID != ctx.RequestID {
		t.Error("Context RequestID should match")
	}
}
