package services

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/models"
)

// AuthServiceClient handles communication with the Auth Service
type AuthServiceClient struct {
	config *config.Config
	client *http.Client
}

// NewAuthServiceClient creates a new auth service client
func NewAuthServiceClient(cfg *config.Config) *AuthServiceClient {
	return &AuthServiceClient{
		config: cfg,
		client: &http.Client{
			Timeout: constants.DefaultTimeout,
		},
	}
}

// ValidateToken sends a JWT token to the Auth Service for validation
func (a *AuthServiceClient) ValidateToken(ctx context.Context, token string) (*models.UserContext, error) {
	// Prepare request payload
	requestPayload := map[string]interface{}{
		constants.AuthTokenField: token,
	}

	// Marshal request to JSON
	requestBody, err := json.Marshal(requestPayload)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	// Create HTTP request
	req, err := http.NewRequestWithContext(ctx, "POST", a.config.Services.AuthService+constants.AuthValidatePath, bytes.NewBuffer(requestBody))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// Set headers
	req.Header.Set("Content-Type", constants.ContentTypeJSON)
	req.Header.Set(constants.XSourceHeader, constants.HeaderValueGateway)

	// Send request to Auth Service
	resp, err := a.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("auth service request failed: %w", err)
	}
	defer resp.Body.Close()

	// Read response body
	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	// Check HTTP status
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("auth service returned status %d: %s", resp.StatusCode, string(responseBody))
	}

	// Parse response
	var authResponse map[string]interface{}
	if err := json.Unmarshal(responseBody, &authResponse); err != nil {
		return nil, fmt.Errorf("failed to parse auth service response: %w", err)
	}

	// Check if token is valid
	valid, ok := authResponse[constants.AuthValidField].(bool)
	if !ok || !valid {
		return nil, fmt.Errorf("token validation failed: %s", authResponse[constants.AuthMessageField])
	}

	// Extract user information
	username, ok := authResponse[constants.AuthUserField].(string)
	if !ok {
		return nil, fmt.Errorf("invalid user information in response")
	}

	// Extract role from metadata if available, default to "customer"
	role := constants.DefaultUserRole
	if metadata, ok := authResponse[constants.AuthMetadataField].(map[string]interface{}); ok {
		if userRole, ok := metadata[constants.AuthRoleField].(string); ok {
			role = userRole
		}
	}

	// Create user context
	userContext := &models.UserContext{
		Username: username,
		Role:     role,
	}

	return userContext, nil
}
