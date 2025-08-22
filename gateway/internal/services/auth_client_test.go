package services

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"order-processor-gateway/internal/config"

	"github.com/stretchr/testify/assert"
)

func TestNewAuthServiceClient(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			AuthService: "http://localhost:8003",
		},
	}

	client := NewAuthServiceClient(cfg)

	assert.NotNil(t, client)
	assert.Equal(t, cfg, client.config)
	assert.NotNil(t, client.client)
}

func TestAuthServiceClient_ValidateToken(t *testing.T) {
	// Create a test server that simulates the Auth Service
	testServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Verify request method and path
		assert.Equal(t, "POST", r.Method)
		assert.Equal(t, "/internal/auth/validate", r.URL.Path)

		// Verify headers
		assert.Equal(t, "application/json", r.Header.Get("Content-Type"))
		assert.Equal(t, "gateway", r.Header.Get("X-Source"))

		// Parse request body
		var requestBody map[string]interface{}
		err := json.NewDecoder(r.Body).Decode(&requestBody)
		assert.NoError(t, err)

		token, ok := requestBody["token"].(string)
		assert.True(t, ok)

		// Simulate different responses based on token
		switch token {
		case "valid.token.here":
			// Return successful validation
			response := map[string]interface{}{
				"valid":      true,
				"user":       "testuser",
				"expires_at": "2025-08-21T22:24:58+00:00",
				"created_at": "2025-08-21T21:24:58+00:00",
				"metadata": map[string]interface{}{
					"algorithm": "HS256",
					"issuer":    "user_service",
					"audience":  "trading_platform",
					"role":      "customer",
				},
				"request_id": "req-123456789",
			}
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(response)

		case "invalid.token.here":
			// Return error response
			response := map[string]interface{}{
				"valid":      false,
				"error":      "token_invalid",
				"message":    "JWT token is invalid",
				"request_id": "req-123456789",
			}
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(response)

		default:
			// Return server error
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte("Internal Server Error"))
		}
	}))
	defer testServer.Close()

	cfg := &config.Config{
		Services: config.ServicesConfig{
			AuthService: testServer.URL,
		},
	}

	client := NewAuthServiceClient(cfg)
	ctx := context.Background()

	t.Run("Valid Token", func(t *testing.T) {
		userContext, err := client.ValidateToken(ctx, "valid.token.here")

		assert.NoError(t, err)
		assert.NotNil(t, userContext)
		assert.Equal(t, "testuser", userContext.Username)
		assert.Equal(t, "customer", userContext.Role)
	})

	t.Run("Invalid Token", func(t *testing.T) {
		userContext, err := client.ValidateToken(ctx, "invalid.token.here")

		assert.Error(t, err)
		assert.Nil(t, userContext)
		assert.Contains(t, err.Error(), "token validation failed")
	})

	t.Run("Server Error", func(t *testing.T) {
		userContext, err := client.ValidateToken(ctx, "server.error.token")

		assert.Error(t, err)
		assert.Nil(t, userContext)
		assert.Contains(t, err.Error(), "auth service returned status 500")
	})
}

func TestAuthServiceClient_ValidateTokenEdgeCases(t *testing.T) {
	// Test server for edge cases
	testServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var requestBody map[string]interface{}
		json.NewDecoder(r.Body).Decode(&requestBody)

		token, _ := requestBody["token"].(string)

		switch token {
		case "missing.user.field":
			response := map[string]interface{}{
				"valid":      true,
				"expires_at": "2025-08-21T22:24:58+00:00",
				"created_at": "2025-08-21T21:24:58+00:00",
				"metadata":   map[string]interface{}{},
				"request_id": "req-123456789",
				// Missing "user" field
			}
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(response)

		case "valid.with.default.role":
			response := map[string]interface{}{
				"valid":      true,
				"user":       "testuser",
				"expires_at": "2025-08-21T22:24:58+00:00",
				"created_at": "2025-08-21T21:24:58+00:00",
				"metadata":   map[string]interface{}{}, // No role in metadata
				"request_id": "req-123456789",
			}
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(response)

		default:
			w.WriteHeader(http.StatusBadRequest)
		}
	}))
	defer testServer.Close()

	cfg := &config.Config{
		Services: config.ServicesConfig{
			AuthService: testServer.URL,
		},
	}

	client := NewAuthServiceClient(cfg)
	ctx := context.Background()

	t.Run("Missing User Field", func(t *testing.T) {
		userContext, err := client.ValidateToken(ctx, "missing.user.field")

		assert.Error(t, err)
		assert.Nil(t, userContext)
		assert.Contains(t, err.Error(), "invalid user information in response")
	})

	t.Run("Valid Token with Default Role", func(t *testing.T) {
		userContext, err := client.ValidateToken(ctx, "valid.with.default.role")

		assert.NoError(t, err)
		assert.NotNil(t, userContext)
		assert.Equal(t, "testuser", userContext.Username)
		assert.Equal(t, "customer", userContext.Role) // Should default to "customer"
	})
}

func TestAuthServiceClient_NetworkErrors(t *testing.T) {
	cfg := &config.Config{
		Services: config.ServicesConfig{
			AuthService: "http://nonexistent.server:9999",
		},
	}

	client := NewAuthServiceClient(cfg)
	ctx := context.Background()

	t.Run("Network Connection Error", func(t *testing.T) {
		userContext, err := client.ValidateToken(ctx, "test.token")

		assert.Error(t, err)
		assert.Nil(t, userContext)
		assert.Contains(t, err.Error(), "auth service request failed")
	})
}
